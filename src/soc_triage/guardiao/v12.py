"""Reprodução dos Recortes aprovados da v12 a partir dos logs de origem.

A v12 não guarda o Recorte separado em Contexto e Registro: cada exemplo tem uma ``entrada`` em
texto, escrita pelo script do lote de curadoria que o gerou. Este módulo:

1. carrega os exemplos de ``revisao.csv`` e os localizadores nativos de cada lote;
2. normaliza os localizadores em linhas de ``data/raw`` e confere o SHA-256 de cada linha;
3. aplica o perfil do Projetor que corresponde à família do exemplo e compara o texto byte a byte;
4. quando não reproduz, registra a causa.

Os caminhos de ``data/processed`` e ``data/raw`` ficam fora do Git. Nada aqui grava nesses
diretórios.
"""

from __future__ import annotations

import csv
import glob
import json
import os
import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .fontes import Acervo, FonteIndisponivel, Trechos, sha256_linha
from .recorte import Recorte, escapar, sha256_texto

MODALIDADES_DO_PROJETOR = ("linux_auth", "apache", "suricata")

PROVENIENCIAS = (
    ("lote-08", "soc-triage-v7/fontes/proveniencia-lote-08.json"),
    ("lote-12", "soc-triage-v8/fontes/proveniencia-lote-12.json"),
    ("lote-14", "soc-triage-v9/fontes/proveniencia-lote-14.json"),
)
CANDIDATOS = (
    ("lote-15", "lote-expansao-15/*/candidatos*.jsonl"),
    ("lote-16", "lote-expansao-16/*/candidatos*.jsonl"),
)
FONTES_ANTIGAS = ("soc-triage-v3", "soc-triage-v4", "soc-triage-v5", "soc-triage-v6")


@dataclass(frozen=True)
class LinhaNativa:
    arquivo: str
    membro: str
    linha: int
    sha256: str | None = None


@dataclass
class ExemploV12:
    id: str
    split: str
    grupo: str
    incidente: str
    modalidade: str
    dataset: str
    entrada: str
    localizador: str
    lote: str = "sem prova de lote"
    nativo_bruto: object = None
    meta: dict = field(default_factory=dict)
    nativo: list[LinhaNativa] = field(default_factory=list)
    motivo_sem_nativo: str | None = None
    veredito: str = ""
    severidade: str = ""
    alvo: dict = field(default_factory=dict)

    @property
    def familia(self) -> str:
        return familia_do_id(self.id)

    @property
    def sha256(self) -> str:
        return sha256_texto(self.entrada)


def familia_do_id(identificador: str) -> str:
    """Prefixo que identifica o script de curadoria, como ``L14-LNXB`` ou ``OX09``."""
    sem_sufixo = re.sub(r"[-_]?[0-9A-Fa-f]{6,}$", "", identificador)
    sem_numero = re.sub(r"[-_]?\d+$", "", sem_sufixo)
    return sem_numero or identificador


def carregar_exemplos(
    processados: Path, modalidades: tuple[str, ...] = MODALIDADES_DO_PROJETOR
) -> list[ExemploV12]:
    """Exemplos da v12 das Modalidades pedidas, com o localizador nativo de cada lote."""
    revisao = processados / "soc-triage-v12" / "splits" / "revisao.csv"
    with open(revisao, encoding="utf-8-sig", newline="") as arquivo:
        linhas = [linha for linha in csv.DictReader(arquivo) if linha["origem"] in modalidades]
    exemplos = {
        linha["id"]: ExemploV12(
            id=linha["id"],
            split=linha["split"],
            grupo=linha["grupo"],
            incidente=linha["incidente"],
            modalidade=linha["origem"],
            dataset=linha["dataset"],
            entrada=linha["entrada"],
            localizador=linha["localizador"],
            veredito=linha.get("veredito", ""),
            severidade=linha.get("severidade", ""),
            alvo=json.loads(linha["alvo_json"]) if linha.get("alvo_json") else {},
        )
        for linha in linhas
    }
    for lote, relativo in PROVENIENCIAS:
        caminho = processados / relativo
        if not caminho.is_file():
            continue
        provas = json.loads(caminho.read_text(encoding="utf-8"))["provas"]
        for identificador, prova in provas.items():
            if identificador in exemplos:
                exemplos[identificador].lote = lote
                exemplos[identificador].nativo_bruto = prova.get("localizador_nativo")
                exemplos[identificador].meta = prova
    for lote, padrao in CANDIDATOS:
        for caminho in sorted(glob.glob(str(processados / padrao))):
            with open(caminho, encoding="utf-8") as arquivo:
                for texto in arquivo:
                    dado = json.loads(texto)
                    if dado.get("id") in exemplos:
                        exemplos[dado["id"]].lote = lote
                        exemplos[dado["id"]].nativo_bruto = dado.get("locator")
                        exemplos[dado["id"]].meta = dado
    for versao in FONTES_ANTIGAS:
        for caminho in sorted(glob.glob(str(processados / versao / "fontes" / "*.jsonl"))):
            with open(caminho, encoding="utf-8") as arquivo:
                for texto in arquivo:
                    try:
                        dado = json.loads(texto)
                    except json.JSONDecodeError:
                        continue
                    alvo = exemplos.get(dado.get("id"))
                    if alvo is not None and alvo.lote == "sem prova de lote":
                        alvo.lote = versao
    return sorted(exemplos.values(), key=lambda e: e.id)


class IndiceDeArquivos:
    """Resolve nomes de arquivo citados sem caminho completo para ``data/raw/...``."""

    def __init__(self, raiz: Path):
        self.raiz = Path(raiz)
        self.por_nome: dict[str, list[str]] = {}
        base = self.raiz / "data" / "raw"
        for pasta, _, nomes in os.walk(base):
            for nome in nomes:
                relativo = os.path.relpath(os.path.join(pasta, nome), self.raiz)
                self.por_nome.setdefault(nome, []).append(relativo)

    def resolver(self, citado: str | None) -> str | None:
        if not citado:
            return None
        citado = citado.replace("\\", "/")
        marcador = "/data/raw/"
        if marcador in citado:
            citado = "data/raw/" + citado.split(marcador, 1)[1]
        if citado.startswith("raw/"):
            citado = "data/" + citado
        if citado.startswith("data/raw/") and (self.raiz / citado).is_file():
            return citado
        candidatos = [
            caminho
            for caminho in self.por_nome.get(os.path.basename(citado), [])
            if caminho.endswith("/" + citado) or os.path.basename(citado) == citado
        ]
        return candidatos[0] if len(candidatos) == 1 else None


SEM_LINHA = {
    "record": "registro numerado numa exportação do Splunk, sem linha de arquivo",
    "archive_member": "offset em journal.gz do Splunk, sem linha de arquivo",
    "csv_record": "registro do CSV do filebeat, sem linha do auth.log",
    "artifact_id": "artefato em parquet, sem linha de arquivo",
    "origin_member": "offset em journal.gz do Splunk, sem linha de arquivo",
    "events": "evento em banco SQLite, sem linha de arquivo",
}


def _sha_da_linha(item: dict) -> str | None:
    for chave in ("sha256_line", "sha256_native_record"):
        if item.get(chave):
            return item[chave]
    return None


def normalizar_localizador(
    bruto: object, indice: IndiceDeArquivos
) -> tuple[list[LinhaNativa], str | None]:
    """Linhas de ``data/raw`` citadas por um localizador nativo, ou o motivo de não haver."""
    if bruto is None:
        return [], "lote sem localizador nativo"
    if isinstance(bruto, str):
        return [], "localizador textual, sem linha numerada"
    itens: list[tuple[str | None, str, int, str | None]] = []
    if isinstance(bruto, dict):
        for chave, motivo in SEM_LINHA.items():
            if chave in bruto:
                return [], motivo
        membros = bruto.get("members") or bruto.get("points") or bruto.get("rows") or bruto.get("records")
        if membros:
            fonte = bruto.get("source") or {}
            for item in membros:
                for chave, motivo in SEM_LINHA.items():
                    if chave in item:
                        return [], motivo
                if "line" not in item:
                    return [], "item de localizador sem linha"
                arquivo = (
                    item.get("archive") or item.get("file") or item.get("local_file")
                    or fonte.get("archive") or fonte.get("path") or bruto.get("archive")
                )
                sha = item.get("sha256_line") or item.get("sha256")
                itens.append((arquivo, item.get("member", ""), int(item["line"]), sha))
        else:
            mapa = (
                bruto.get("sha256_por_linha") or bruto.get("sha256_by_line")
                or bruto.get("sha256_por_linha_usada") or {}
            )
            for numero in sorted(mapa, key=int):
                itens.append((bruto.get("archive"), bruto.get("member", ""), int(numero), mapa[numero]))
            if not mapa and bruto.get("lines"):
                for numero in bruto["lines"]:
                    itens.append((bruto.get("archive"), bruto.get("member", ""), int(numero), None))
    elif isinstance(bruto, list):
        for item in bruto:
            for chave, motivo in SEM_LINHA.items():
                if chave in item:
                    return [], motivo
            if "line" not in item:
                return [], "item de localizador sem linha"
            itens.append((item.get("archive"), item.get("member", ""), int(item["line"]), _sha_da_linha(item)))
    if not itens:
        return [], "localizador sem linhas"
    linhas = []
    for arquivo, membro, numero, sha in itens:
        resolvido = indice.resolver(arquivo) if arquivo else None
        if resolvido is None and membro:
            resolvido = indice.resolver(membro)
            membro = "" if resolvido else membro
        if resolvido is None:
            return [], f"arquivo do localizador não encontrado em data/raw ({arquivo or membro})"
        linhas.append(LinhaNativa(resolvido, membro, numero, sha))
    return linhas, None


Chave = tuple[str, str]


class Leitor:
    """Linhas de ``data/raw`` lidas para a reprodução, por arquivo e membro."""

    def __init__(self, trechos: dict[Chave, Trechos]):
        self._trechos = trechos

    def trechos(self, arquivo: str, membro: str) -> Trechos:
        return self._trechos[(arquivo, membro)]

    def texto(self, arquivo: str, membro: str, numero: int) -> str:
        return self.trechos(arquivo, membro).texto(numero)

    def bruto(self, arquivo: str, membro: str, numero: int) -> bytes:
        trechos = self.trechos(arquivo, membro)
        if numero not in trechos.linhas:
            raise IndexError(f"{trechos.chave}: linha {numero} não lida")
        return trechos.linhas[numero]


def alcance_padrao(exemplo: ExemploV12) -> dict[Chave, set[int]]:
    """Linhas citadas e, em cada Fonte, todo o intervalo entre a primeira e a última."""
    pedidos: dict[Chave, set[int]] = {}
    for item in exemplo.nativo:
        pedidos.setdefault((item.arquivo, item.membro), set()).add(item.linha)
    for numeros in pedidos.values():
        numeros |= set(range(min(numeros), max(numeros) + 1))
    return pedidos


@dataclass(frozen=True)
class Perfil:
    """Forma de um lote da v12 que o Projetor reproduz a partir dos logs de origem."""

    nome: str
    familias: tuple[str, ...]
    projetar: Callable[[ExemploV12, Leitor], Recorte]
    alcance: Callable[[ExemploV12], dict[Chave, set[int]]] = alcance_padrao
    filtro: Callable[[ExemploV12], bool] = lambda exemplo: True

    def aceita(self, exemplo: ExemploV12) -> bool:
        return exemplo.familia in self.familias and self.filtro(exemplo)


class PerfilNaoAplicavel(ValueError):
    """O exemplo é da família do perfil, mas foge do caso que o perfil cobre."""


@dataclass
class Conferencia:
    total: int = 0
    conferidas: int = 0
    pelo_membro: int = 0
    divergentes: int = 0
    sem_sha: int = 0
    erro: str | None = None
    textos: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.erro is None and self.divergentes == 0


def coletar(
    exemplos: Iterable[ExemploV12], perfis: Iterable[Perfil], acervo: Acervo
) -> dict[Chave, Trechos | str]:
    """Lê cada Fonte uma vez, em fluxo, guardando só as linhas que algum exemplo pede."""
    perfis = list(perfis)
    pedidos: dict[Chave, set[int]] = {}
    for exemplo in exemplos:
        if not exemplo.nativo:
            continue
        perfil = next((p for p in perfis if p.aceita(exemplo)), None)
        alcance = (perfil.alcance if perfil else alcance_padrao)(exemplo)
        for chave, numeros in alcance.items():
            pedidos.setdefault(chave, set()).update(numeros)
    lidos: dict[Chave, Trechos | str] = {}
    for chave in sorted(pedidos):
        try:
            lidos[chave] = acervo.trechos(chave[0], chave[1] or None, pedidos[chave])
        except (FonteIndisponivel, OSError, EOFError, ValueError) as erro:
            lidos[chave] = f"{type(erro).__name__}: {erro}"
    return lidos


def conferir(exemplo: ExemploV12, lidos: dict[Chave, Trechos | str]) -> Conferencia:
    """Confere o SHA-256 de cada linha citada contra ``data/raw``.

    Os lotes usaram três convenções: SHA da linha sem ``\\n``, com ``\\n`` ou, em poucos lotes,
    o SHA do membro inteiro repetido em cada linha.
    """
    resultado = Conferencia(total=len(exemplo.nativo))
    for item in exemplo.nativo:
        trechos = lidos.get((item.arquivo, item.membro))
        if trechos is None or isinstance(trechos, str):
            resultado.erro = trechos or "fonte não lida"
            return resultado
        if item.linha not in trechos.linhas:
            resultado.erro = f"linha {item.linha} fora do membro ({trechos.total} linhas)"
            return resultado
        bruto = trechos.linhas[item.linha]
        resultado.textos.append(bruto.decode("utf-8", errors="replace"))
        if item.sha256 is None:
            resultado.sem_sha += 1
        elif item.sha256 in sha256_linha(bruto):
            resultado.conferidas += 1
        elif item.sha256 == trechos.sha256:
            resultado.pelo_membro += 1
        else:
            resultado.divergentes += 1
    return resultado


def linhas_literais(entrada: str, textos_nativos: list[str]) -> tuple[int, int]:
    """Quantas linhas da entrada são cópia exata (com controles escapados) de linhas nativas."""
    nativos = {escapar(texto) for texto in textos_nativos} | set(textos_nativos)
    linhas = entrada.split("\n")
    return sum(1 for linha in linhas if linha in nativos), len(linhas)


@dataclass
class Reproducao:
    id: str
    split: str
    modalidade: str
    familia: str
    lote: str
    linhas_citadas: int = 0
    linhas_conferidas: int = 0
    fonte_conferida: bool = False
    literais: int = 0
    linhas_da_entrada: int = 0
    perfil: str | None = None
    byte_a_byte: bool = False
    causa: str = ""
    detalhe: str = ""
    sha256_v12: str = ""
    hash_recorte: str | None = None


def primeira_diferenca(esperado: str, obtido: str) -> str:
    """Descreve a primeira linha divergente sem copiar o conteúdo do log."""
    linhas_e, linhas_o = esperado.split("\n"), obtido.split("\n")
    for indice, (a, b) in enumerate(zip(linhas_e, linhas_o), 1):
        if a != b:
            coluna = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
            return f"linha {indice}, coluna {coluna + 1}"
    return f"{len(linhas_e)} linhas esperadas, {len(linhas_o)} obtidas"


def reproduzir(
    exemplos: list[ExemploV12],
    perfis: Iterable[Perfil],
    acervo: Acervo,
    indice: IndiceDeArquivos,
    causas_conhecidas: dict[str, str] | None = None,
) -> list[Reproducao]:
    """Confere localizadores, aplica os perfis e compara cada entrada byte a byte."""
    perfis = list(perfis)
    causas_conhecidas = causas_conhecidas or {}
    for exemplo in exemplos:
        exemplo.nativo, exemplo.motivo_sem_nativo = normalizar_localizador(exemplo.nativo_bruto, indice)
    lidos = coletar(exemplos, perfis, acervo)
    leitor = Leitor({k: v for k, v in lidos.items() if isinstance(v, Trechos)})
    resultados = []
    for exemplo in exemplos:
        r = Reproducao(
            exemplo.id, exemplo.split, exemplo.modalidade, exemplo.familia, exemplo.lote,
            sha256_v12=exemplo.sha256,
        )
        resultados.append(r)
        r.linhas_da_entrada = len(exemplo.entrada.split("\n"))
        if not exemplo.nativo:
            r.causa = "sem linha nativa"
            r.detalhe = exemplo.motivo_sem_nativo or ""
            continue
        conferencia = conferir(exemplo, lidos)
        r.linhas_citadas = conferencia.total
        r.linhas_conferidas = conferencia.conferidas + conferencia.pelo_membro
        if conferencia.erro:
            r.causa = "fonte ilegível"
            r.detalhe = conferencia.erro
            continue
        r.fonte_conferida = conferencia.ok
        r.literais, _ = linhas_literais(exemplo.entrada, conferencia.textos)
        if not conferencia.ok:
            r.causa = "linha citada não confere com data/raw"
            r.detalhe = f"{conferencia.divergentes} de {conferencia.total} linhas com SHA-256 diferente"
            continue
        perfil = next((p for p in perfis if p.aceita(exemplo)), None)
        if perfil is None:
            r.causa = "perfil não portado"
            r.detalhe = causas_conhecidas.get(exemplo.familia, "")
            continue
        r.perfil = perfil.nome
        try:
            recorte = perfil.projetar(exemplo, leitor)
        except PerfilNaoAplicavel as erro:
            r.causa = "caso fora do perfil"
            r.detalhe = str(erro)
            continue
        r.hash_recorte = recorte.hash()
        if recorte.hash_v1() == exemplo.sha256:
            r.byte_a_byte = True
            r.causa = "reproduzido"
        else:
            r.causa = "perfil diverge"
            r.detalhe = primeira_diferenca(exemplo.entrada, recorte.texto_v1())
    return resultados


def fontes_por_grupo(exemplos: Iterable[ExemploV12]) -> dict[str, list[tuple[str, str, str]]]:
    """Arquivos de ``data/raw`` de cada grupo de incidente, pelos localizadores conferidos.

    Devolve ``grupo -> [(modalidade, arquivo, membro)]``. Um grupo nunca recebe arquivo citado só
    por outro grupo, o que mantém o Ambiente de treino dentro do split do grupo.
    """
    grupos: dict[str, set[tuple[str, str, str]]] = {}
    for exemplo in exemplos:
        for item in exemplo.nativo:
            grupos.setdefault(exemplo.grupo, set()).add((exemplo.modalidade, item.arquivo, item.membro))
    return {grupo: sorted(itens) for grupo, itens in grupos.items()}
