"""Projetor por Modalidade: transforma eventos de log num Recorte.

O Projetor é determinístico. Ele recebe os eventos de uma Fonte e a Âncora e:

1. escolhe a janela da Âncora (mesma origem, até ``janela_s`` antes dela, nada depois);
2. escreve no Contexto só campos calculados: janela, contagens e o Contexto da curadoria;
3. copia as linhas do log para o Registro, que a renderização escapa;
4. marca os Sinais pelas regras versionadas de ``sinais``;
5. declara o Recorte incompleto quando corta a janela ou quando faltam campos.

Esta é a forma canônica do Projetor (perfil ``canonico``). Os perfis que reproduzem os formatos
da v12 ficam em ``perfis_v12``.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from . import sinais as regras_de_sinal
from .eventos import Evento
from .recorte import Linha, Recorte, Sinal, contexto, registro

VERSAO_PROJETOR = "projetor-0.1"
MODALIDADES = ("linux_auth", "apache", "suricata")

JANELA_PADRAO_S = {"linux_auth": 900, "apache": 300, "suricata": 300}
MAX_LINHAS_REGISTRO = 12

TIPOS_FALHA = regras_de_sinal.TIPOS_DE_FALHA_SSH


def formatar_duracao(segundos: float) -> str:
    segundos = round(segundos)
    if segundos < 60:
        return f"{segundos} s"
    minutos, resto = divmod(segundos, 60)
    if minutos < 60:
        return f"{minutos} min {resto} s" if resto else f"{minutos} min"
    horas, minutos = divmod(minutos, 60)
    return f"{horas} h {minutos} min" if minutos else f"{horas} h"


def formatar_instante(instante: datetime | None, sem_ano: bool = False) -> str:
    """Horário em UTC. Num relógio sem ano nem fuso (syslog BSD), repete o relógio do log."""
    if instante is None:
        return "sem horário"
    if sem_ano:
        return f"{instante:%b} {instante.day} {instante:%H:%M:%S}"
    return instante.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def contagem(contador: Counter, limite: int = 6) -> str:
    itens = sorted(contador.items(), key=lambda par: (-par[1], str(par[0])))
    texto = ", ".join(f"{chave}×{valor}" for chave, valor in itens[:limite])
    resto = len(itens) - limite
    return texto + (f" e mais {resto}" if resto > 0 else "")


def chave_da_origem(modalidade: str) -> Callable[[Evento], object]:
    """Como o Projetor reconhece eventos da mesma origem da Âncora."""
    if modalidade == "suricata":
        return lambda e: frozenset(filter(None, (e.get("src_ip"), e.get("dest_ip"))))
    return lambda e: e.ip


def selecionar_janela(
    eventos: Sequence[Evento],
    ancora: Evento,
    janela_s: int,
    mesma_origem: Callable[[Evento], object] | None = None,
) -> list[Evento]:
    """Eventos da mesma Fonte e origem, até ``janela_s`` antes da Âncora e nunca depois dela.

    Em linux_auth, linhas do mesmo processo do sshd de um evento da origem (abertura de sessão,
    desconexão) também entram, como a curadoria fazia.
    """
    if ancora.instante is None:
        return [ancora]
    inicio = ancora.instante - timedelta(seconds=janela_s)
    chave = mesma_origem or chave_da_origem(ancora.modalidade)
    alvo = chave(ancora)
    na_janela = [
        e
        for e in eventos
        if e.fonte == ancora.fonte
        and e.linha <= ancora.linha
        and e.instante is not None
        and inicio <= e.instante <= ancora.instante
    ]
    if not alvo and ancora.modalidade == "linux_auth" and ancora.get("programa") == "sshd":
        # Linha sem endereço (abertura de sessão): a origem é a do mesmo processo do sshd.
        alvo = next(
            (e.ip for e in na_janela if e.ip and e.get("pid") == ancora.get("pid")
             and e.get("programa") == "sshd"),
            None,
        )
    escolhidos = [e for e in na_janela if not alvo or chave(e) == alvo]
    if ancora.modalidade == "linux_auth" and alvo:
        processos = {e.get("pid") for e in escolhidos if e.get("programa") == "sshd" and e.get("pid")}
        escolhidos += [
            e
            for e in na_janela
            if e not in escolhidos and e.get("programa") == "sshd" and e.get("pid") in processos
        ]
    if ancora not in escolhidos:
        escolhidos.append(ancora)
    return sorted(escolhidos, key=lambda e: e.linha)


def plural(valor: int, singular: str, varios: str) -> str:
    return f"{valor} {singular if valor == 1 else varios}"


def _resumo_linux_auth(eventos: list[Evento]) -> str:
    falhas = sum(e.get("repeticoes", 1) for e in eventos if e.tipo in TIPOS_FALHA)
    invalidas = sum(
        e.get("repeticoes", 1)
        for e in eventos
        if e.tipo == "usuario_invalido" or (e.tipo == "falha_de_senha" and e.get("invalido"))
    )
    contas = {e.get("usuario") for e in eventos if e.get("usuario")}
    origens = {e.ip for e in eventos if e.ip}
    conexoes = {e.get("pid") for e in eventos if e.get("programa") == "sshd" and e.get("pid")}
    encerradas = sum(1 for e in eventos if e.tipo == "conexao_encerrada" and e.get("usuario"))
    aceites = sum(1 for e in eventos if e.tipo == "aceite")
    sessoes = sum(1 for e in eventos if e.tipo == "sessao_aberta")
    sudo = sum(1 for e in eventos if e.tipo == "sudo")
    return (
        f"Contagens: {plural(falhas, 'falha', 'falhas')} de autenticação ({invalidas} com usuário "
        f"inválido); {plural(len(origens), 'origem', 'origens')}; "
        f"{plural(len(contas), 'conta', 'contas distintas')}; "
        f"{plural(len(conexoes), 'conexão', 'conexões')} do sshd; "
        f"{plural(encerradas, 'conexão encerrada', 'conexões encerradas')} durante a autenticação; "
        f"{plural(aceites, 'aceite', 'aceites')}; "
        f"{plural(sessoes, 'sessão aberta', 'sessões abertas')}; "
        f"{plural(sudo, 'comando sudo', 'comandos sudo')}."
    )


def _resumo_apache(eventos: list[Evento]) -> str:
    status = Counter(e.get("status") for e in eventos if e.get("status"))
    metodos = Counter(e.get("metodo") for e in eventos if e.get("metodo"))
    caminhos = {e.get("caminho") for e in eventos if e.get("caminho")}
    agentes = {e.get("user_agent") for e in eventos if e.get("user_agent") is not None}
    return (
        f"Contagens: {plural(len(eventos), 'requisição', 'requisições')}; "
        f"status {contagem(status) or 'nenhum'}; métodos {contagem(metodos) or 'nenhum'}; "
        f"{plural(len(caminhos), 'caminho', 'caminhos distintos')}; "
        f"{plural(len(agentes), 'user-agent', 'user-agents distintos')}."
    )


def _resumo_suricata(eventos: list[Evento]) -> str:
    tipos = Counter(e.tipo for e in eventos)
    assinaturas = {e.get("signature_id") for e in eventos if e.get("signature_id") is not None}
    portas = {e.get("dest_port") for e in eventos if e.get("dest_port") is not None}
    pares = {
        frozenset(filter(None, (e.get("src_ip"), e.get("dest_ip")))) for e in eventos
    } - {frozenset()}
    return (
        f"Contagens: {plural(len(eventos), 'evento', 'eventos')} ({contagem(tipos)}); "
        f"{plural(len(assinaturas), 'assinatura', 'assinaturas distintas')}; "
        f"{plural(len(pares), 'par', 'pares')} de endereços; "
        f"{plural(len(portas), 'porta', 'portas')} de destino."
    )


def resumo_sudo(eventos: list[Evento]) -> str:
    """Contexto de sudo e su, escrito pelo Projetor desde a emenda do ADR 0009."""
    sudo = [e for e in eventos if e.tipo == "sudo"]
    comandos = sum(1 for e in sudo if e.get("comando") is not None)
    senhas = sum(int(e.get("falhas") or 0) for e in sudo)
    negados = sum(1 for e in sudo if e.get("negado"))
    trocas = sum(1 for e in eventos if e.tipo == "su")
    alvos = {e.get("alvo") for e in eventos if e.tipo in ("sudo", "su") and e.get("alvo")}
    return (
        f"Sudo e su: {plural(comandos, 'comando sudo', 'comandos sudo')}; "
        f"{plural(senhas, 'senha incorreta', 'senhas incorretas')}; "
        f"{plural(negados, 'recusa', 'recusas')} por estar fora do sudoers; "
        f"{plural(trocas, 'troca', 'trocas')} de conta com su; "
        f"{plural(len(alvos), 'conta-alvo', 'contas-alvo distintas')}."
    )


RESUMOS = {
    "linux_auth": _resumo_linux_auth,
    "apache": _resumo_apache,
    "suricata": _resumo_suricata,
}


@dataclass(frozen=True)
class Janela:
    modalidade: str
    eventos: tuple[Evento, ...]
    ancora: Evento


def projetar(
    janela: Janela,
    *,
    descricao_fonte: str,
    contexto_curado: Iterable[str] = (),
    max_linhas: int = MAX_LINHAS_REGISTRO,
) -> Recorte:
    """Recorte canônico de uma janela que termina na Âncora.

    ``descricao_fonte`` vem da configuração da máquina (caminho do arquivo e relógio), não do log.
    ``contexto_curado`` traz o que não está nos logs, como a linha de base e as mudanças aprovadas.
    """
    modalidade = janela.modalidade
    if modalidade not in RESUMOS:
        raise ValueError(f"Modalidade sem Projetor: {modalidade}")
    eventos = [e for e in janela.eventos if e.linha <= janela.ancora.linha]
    if janela.ancora not in eventos:
        raise ValueError("a Âncora precisa estar na janela")
    eventos.sort(key=lambda e: e.linha)
    incompleto = []
    mostrados = eventos
    if len(eventos) > max_linhas:
        mostrados = [eventos[0], *eventos[-(max_linhas - 1) :]]
        incompleto.append(f"janela cortada: {len(mostrados)} de {len(eventos)} linhas no Registro")
    fora = sum(1 for e in eventos if e.tipo == "fora_do_formato" or e.instante is None)
    if fora:
        incompleto.append(f"campos ausentes: {fora} linhas sem horário ou fora do formato")

    inicio, fim = eventos[0].instante, janela.ancora.instante
    duracao = (fim - inicio).total_seconds() if inicio and fim else 0
    sem_ano = bool(janela.ancora.get("sem_ano"))
    relogio = " (relógio do log, sem ano e sem fuso)" if sem_ano else ""
    linhas: list[Linha] = [
        contexto(f"Modalidade {modalidade} | {descricao_fonte}", "cabecalho"),
        contexto(
            f"Janela: {formatar_duracao(duracao)} até a âncora ({formatar_instante(inicio, sem_ano)} a "
            f"{formatar_instante(fim, sem_ano)}{relogio}); "
            f"{plural(len(eventos), 'evento', 'eventos')} da mesma origem.",
            "janela",
        ),
        contexto(RESUMOS[modalidade](eventos), "contagens"),
    ]
    if modalidade == "linux_auth" and any(e.tipo in ("sudo", "su") for e in eventos):
        linhas.append(contexto(resumo_sudo(eventos), "sudo"))
    linhas += [contexto(texto, "curadoria") for texto in contexto_curado]
    linhas.append(contexto("Âncora: última linha do Registro.", "ancora"))
    posicao = {id(evento): indice for indice, evento in enumerate(mostrados)}
    linhas += [registro(evento.texto, "linha_do_log") for evento in mostrados]

    sinais = tuple(
        Sinal(
            disparo.regra,
            disparo.versao,
            disparo.descricao,
            tuple(sorted(posicao[id(e)] for e in disparo.eventos if id(e) in posicao)),
        )
        for disparo in regras_de_sinal.detectar(modalidade, eventos)
    )
    return Recorte(
        modalidade=modalidade,
        linhas=tuple(linhas),
        sinais=sinais,
        incompleto=tuple(incompleto),
        perfil="canonico",
        metadados={
            "versao_projetor": VERSAO_PROJETOR,
            "versao_sinais": regras_de_sinal.VERSAO_CATALOGO,
            "linhas_do_registro": [(e.fonte, e.linha) for e in mostrados],
        },
    )
