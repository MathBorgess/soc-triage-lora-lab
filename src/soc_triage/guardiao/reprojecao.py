"""Reprojeção da v12 no formato canônico do Projetor (ADR 0012).

Para cada Recorte da v12 com linha nativa em ``data/raw``:

1. a Âncora é a linha citada mais recente (horário, depois número da linha);
2. o Projetor de produção escolhe a janela: mesma origem, ``JANELA_PADRAO_S`` antes da Âncora;
3. o Recorte canônico é comparado com o que sustentava o rótulo na v12. Quando algo muda, o
   Recorte vai para a fila de revisão do responsável, com os motivos.

Nada aqui muda rótulo nem aprova Recorte. Os Recortes sem linha nativa ficam fora do contrato v2
até ganharem localizador, ou são declarados como perda pelo responsável.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .ambiente import ANO_PADRAO_SYSLOG, JANELA_MAXIMA_S, _instante_rapido
from .eventos import Evento, RelogioSyslog, ler
from .fontes import Acervo, FonteIndisponivel
from .projetor import JANELA_PADRAO_S, Janela, projetar, selecionar_janela
from .recorte import Recorte
from .tipos_de_contexto import tipos_do_recorte
from .v12 import ExemploV12, IndiceDeArquivos, LinhaNativa, normalizar_localizador

VERSAO_REPROJECAO = "reprojecao-v2-01"

MOTIVOS = {
    "linha_citada_fora_do_registro": (
        "linha citada pela curadoria saiu do Registro, mas uma Ferramenta de leitura ainda a alcança "
        "(mesma Fonte do grupo, até a Âncora e no máximo 24 h antes)"
    ),
    "linha_citada_fora_do_alcance": (
        "linha citada pela curadoria saiu do Registro e nenhuma Ferramenta de leitura a alcança"
    ),
    "alvo_nao_literal": "campo do alvo da v12 que não aparece literalmente no Recorte reprojetado",
    "numero_da_justificativa_ausente": (
        "número citado na justificativa da v12 que não aparece no Recorte reprojetado"
    ),
    "contexto_da_curadoria": (
        "a v12 trazia Contexto que não está nos logs (agenda, linha de base ou mudança aprovada); "
        "ele precisa ser transcrito como Contexto da curadoria"
    ),
}
TIPOS_DA_CURADORIA = frozenset({"agenda_e_rotina", "linha_de_base", "mudanca_aprovada"})
CAMPOS_DO_ALVO = ("timestamp", "src_ip", "dst_ip", "user", "process_or_action")
NUMERO = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?(?![\w])")
TECNICA = re.compile(r"T\d{4}(?:\.\d{3})?")

Chave = tuple[str, str, str]  # (modalidade, arquivo, membro)


@dataclass
class Reprojecao:
    exemplo: ExemploV12
    ancora: LinhaNativa | None = None
    recorte: Recorte | None = None
    motivos: dict[str, str] = field(default_factory=dict)
    fora: str | None = None

    @property
    def na_fila(self) -> bool:
        return self.recorte is not None and bool(self.motivos)

    @property
    def estado(self) -> str:
        if self.recorte is None:
            return "fora_do_contrato"
        return "fila_de_revisao" if self.motivos else "sem_mudanca_detectada"


def _chave(exemplo: ExemploV12, item: LinhaNativa) -> Chave:
    return (exemplo.modalidade, item.arquivo, item.membro)


def _iterar_eventos(
    acervo: Acervo, chave: Chave, filtro: Iterable[tuple[datetime, datetime]] | None = None,
    linhas: set[int] | None = None,
) -> Iterable[Evento]:
    """Eventos de uma Fonte em ordem de leitura.

    Com ``linhas``, devolve só essas linhas. Com ``filtro``, só os eventos com horário dentro de
    alguma das faixas. O relógio do syslog BSD acompanha todas as linhas, para virar o ano.
    """
    modalidade, arquivo, membro = chave
    rotulo = f"{arquivo}::{membro}"
    relogio = RelogioSyslog(ANO_PADRAO_SYSLOG) if modalidade == "linux_auth" else None
    faixas = list(filtro or [])
    marcas = _marcas_de_data(faixas) if faixas and relogio is None else ()
    for numero, bruto in acervo.iterar(arquivo, membro or None):
        if linhas is not None and numero not in linhas and relogio is None:
            continue
        if marcas and not any(marca in bruto for marca in marcas):
            continue
        if faixas and relogio is None:
            previo = _instante_rapido(modalidade, bruto)
            if previo is not None and not any(a <= previo <= b for a, b in faixas):
                continue
        evento = ler(modalidade, bruto.decode("utf-8", errors="replace"), rotulo, numero, relogio)
        if linhas is not None and numero not in linhas:
            continue
        if faixas and (evento.instante is None or not any(a <= evento.instante <= b for a, b in faixas)):
            continue
        yield evento


def _marcas_de_data(faixas: list[tuple[datetime, datetime]]) -> tuple[bytes, ...]:
    """Datas (EVE e Apache) que uma linha precisa conter para cair numa das faixas.

    Inclui o dia anterior e o seguinte, porque o carimbo local pode estar em outro dia do UTC.
    """
    marcas = set()
    for inicio, fim in faixas:
        dia = (inicio - timedelta(days=1)).date()
        while dia <= (fim + timedelta(days=1)).date():
            marcas.add(dia.strftime("%Y-%m-%d").encode())
            marcas.add(dia.strftime("%d/%b/%Y").encode())
            dia += timedelta(days=1)
    return tuple(sorted(marcas))


def _texto_contem(texto: str, valor: str) -> bool:
    return valor.casefold() in texto.casefold()


def _motivos(
    exemplo: ExemploV12,
    recorte: Recorte,
    mostradas: set[tuple[str, int]],
    alcancaveis: set[tuple[str, int]],
) -> dict[str, str]:
    motivos: dict[str, str] = {}
    texto = recorte.texto_v2()
    citadas = {(f"{item.arquivo}::{item.membro}", item.linha) for item in exemplo.nativo}
    fora = citadas - mostradas
    if fora:
        fora_do_alcance = fora - alcancaveis
        if fora_do_alcance:
            motivos["linha_citada_fora_do_alcance"] = (
                f"{len(fora_do_alcance)} de {len(citadas)} linhas citadas"
            )
        else:
            motivos["linha_citada_fora_do_registro"] = f"{len(fora)} de {len(citadas)} linhas citadas"
    evento = (exemplo.alvo or {}).get("normalized_event") or {}
    ausentes = [
        campo for campo in CAMPOS_DO_ALVO
        if isinstance(evento.get(campo), str) and evento[campo] and not _texto_contem(texto, evento[campo])
    ]
    iocs = [ioc for ioc in evento.get("iocs") or [] if isinstance(ioc, str) and not _texto_contem(texto, ioc)]
    if iocs:
        ausentes.append(f"iocs ({len(iocs)})")
    if ausentes:
        motivos["alvo_nao_literal"] = ", ".join(ausentes)
    justificativa = ((exemplo.alvo or {}).get("triage") or {}).get("rationale") or ""
    justificativa = TECNICA.sub(" ", justificativa)
    numeros_do_texto = set(NUMERO.findall(texto))
    faltam = sorted({n for n in NUMERO.findall(justificativa) if n not in numeros_do_texto})
    if faltam:
        motivos["numero_da_justificativa_ausente"] = f"{len(faltam)} números"
    tipos, _ = tipos_do_recorte(exemplo.entrada)
    curadoria = sorted(tipos & TIPOS_DA_CURADORIA)
    if curadoria:
        motivos["contexto_da_curadoria"] = ", ".join(curadoria)
    return motivos


def reprojetar(
    exemplos: list[ExemploV12],
    acervo: Acervo,
    indice: IndiceDeArquivos,
    janelas: dict[str, int] | None = None,
) -> list[Reprojecao]:
    """Reprojeta os exemplos no formato canônico, lendo cada Fonte em duas passadas."""
    janelas = janelas or JANELA_PADRAO_S
    resultados = [Reprojecao(exemplo) for exemplo in exemplos]
    citadas_por_fonte: dict[Chave, set[int]] = {}
    for r in resultados:
        exemplo = r.exemplo
        if not exemplo.nativo:
            exemplo.nativo, exemplo.motivo_sem_nativo = normalizar_localizador(exemplo.nativo_bruto, indice)
        if not exemplo.nativo:
            r.fora = f"sem linha nativa: {exemplo.motivo_sem_nativo}"
            continue
        for item in exemplo.nativo:
            citadas_por_fonte.setdefault(_chave(exemplo, item), set()).add(item.linha)

    # Passada 1: horário de cada linha citada, com o mesmo relógio que o Ambiente usa.
    instantes: dict[tuple[Chave, int], Evento] = {}
    ilegiveis: dict[Chave, str] = {}
    for chave, linhas in sorted(citadas_por_fonte.items()):
        try:
            for evento in _iterar_eventos(acervo, chave, linhas=linhas):
                instantes[(chave, evento.linha)] = evento
        except (FonteIndisponivel, OSError, ValueError) as erro:
            ilegiveis[chave] = f"{type(erro).__name__}"

    # Âncora de cada exemplo e faixas de horário a ler na segunda passada.
    faixas: dict[Chave, list[tuple[datetime, datetime]]] = {}
    ancoras: dict[int, tuple[Chave, Evento]] = {}
    for indice_r, r in enumerate(resultados):
        if r.fora:
            continue
        candidatos = []
        for item in r.exemplo.nativo:
            chave = _chave(r.exemplo, item)
            if chave in ilegiveis:
                r.fora = f"fonte ilegível: {ilegiveis[chave]}"
                break
            evento = instantes.get((chave, item.linha))
            if evento is not None and evento.instante is not None:
                candidatos.append((evento.instante, item.linha, chave, evento, item))
        if r.fora:
            continue
        if not candidatos:
            r.fora = "nenhuma linha citada tem horário legível"
            continue
        _, _, chave, evento, item = max(candidatos, key=lambda c: (c[0], c[1]))
        r.ancora = item
        ancoras[indice_r] = (chave, evento)
        janela = janelas[r.exemplo.modalidade]
        faixas.setdefault(chave, []).append((evento.instante - timedelta(seconds=janela), evento.instante))

    # Passada 2: eventos das faixas, uma vez por Fonte.
    eventos_por_fonte: dict[Chave, list[Evento]] = {}
    for chave, lista in sorted(faixas.items()):
        eventos_por_fonte[chave] = list(_iterar_eventos(acervo, chave, filtro=lista))

    for indice_r, (chave, ancora) in ancoras.items():
        r = resultados[indice_r]
        modalidade, arquivo, membro = chave
        eventos = eventos_por_fonte[chave]
        janela = selecionar_janela(eventos, ancora, janelas[modalidade])
        r.recorte = projetar(
            Janela(modalidade, tuple(janela), ancora),
            descricao_fonte=f"arquivo {os.path.basename(membro or arquivo)}",
        )
        mostrados = set(r.recorte.metadados["linhas_do_registro"])
        alcancaveis = _alcancaveis(r.exemplo, ancora, instantes)
        r.motivos = _motivos(r.exemplo, r.recorte, mostrados, alcancaveis)
    return resultados


def _alcancaveis(
    exemplo: ExemploV12, ancora: Evento, instantes: dict[tuple[Chave, int], Evento]
) -> set[tuple[str, int]]:
    """Linhas citadas que uma Ferramenta de leitura alcança a partir da Âncora.

    O Ambiente de treino tem todas as Fontes do grupo e devolve eventos até a Âncora, no máximo
    ``JANELA_MAXIMA_S`` antes dela.
    """
    limite = ancora.instante - timedelta(seconds=JANELA_MAXIMA_S)
    alcancaveis = set()
    for item in exemplo.nativo:
        chave = _chave(exemplo, item)
        evento = instantes.get((chave, item.linha))
        if evento is None or evento.instante is None:
            continue
        mesma_fonte = evento.fonte == ancora.fonte
        if limite <= evento.instante <= ancora.instante and (not mesma_fonte or item.linha <= ancora.linha):
            alcancaveis.add((evento.fonte, item.linha))
    return alcancaveis
