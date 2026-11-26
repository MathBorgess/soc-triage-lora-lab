"""Catálogo de Ferramentas de leitura do Guardião.

O catálogo segue a regra dos 20 Recortes do ADR 0009. A ``sudo`` saiu na emenda de 26/11/2026 e o
Contexto de sudo voltou a ser escrito pelo Projetor.

Cada ferramenta é determinística e somente-leitura: lê eventos do Ambiente de treino (no treino e na
avaliação) ou dos logs locais (em produção) e nunca muda nada. A resposta tem duas partes:

- ``contexto``: campos que a própria ferramenta calcula, como contagens, horários e endereços
  validados. Entram como Contexto e podem sustentar um Rebaixamento (emenda do ADR 0003).
- ``registro``: linhas copiadas do log. Entram como Registro, escapadas, e nunca são instrução.

Toda ferramenta tem janela máxima e limite de linhas. Quando corta a saída, a resposta diz quantas
linhas mostrou e quantas omitiu.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC

from .ambiente import AmbienteDeTreino
from .eventos import Evento
from .recorte import escapar

VERSAO_CATALOGO = "ferramentas-0.2"
JANELA_MAXIMA_S = 24 * 3600
LIMITE_DE_LINHAS = 8
BLOQUEIO_HTTP = frozenset({403, 406, 429})
TIPOS_FALHA = frozenset({"falha_de_senha", "usuario_invalido", "excesso_de_tentativas", "falha_pam"})
TIPOS_SESSAO = frozenset({"aceite", "sessao_aberta", "sessao_fechada"})
METODO_SSH = re.compile(r"[a-z0-9-]{1,32}")


class ChamadaInvalida(ValueError):
    """Argumento ausente, desconhecido, com tipo errado ou fora do limite."""


@dataclass(frozen=True)
class Resposta:
    nome: str
    argumentos: dict
    contexto: dict
    registro: tuple[str, ...]
    linhas_encontradas: int
    erro: str | None = None

    @property
    def cortada(self) -> bool:
        return self.linhas_encontradas > len(self.registro)

    def para_template(self) -> dict:
        """Dicionário para ``tool_responses`` do template do Gemma 4, com o Registro escapado."""
        if self.erro:
            return {"erro": self.erro}
        corpo: dict = {"contexto": self.contexto, "registro": [escapar(t) for t in self.registro]}
        if self.cortada:
            corpo["corte"] = (
                f"{len(self.registro)} de {self.linhas_encontradas} linhas mostradas; "
                f"{self.linhas_encontradas - len(self.registro)} omitidas"
            )
        return corpo

    def hash(self) -> str:
        """SHA-256 da resposta, que vai na Remessa e no Diário de inferências."""
        dados = json.dumps(
            {"nome": self.nome, "argumentos": self.argumentos, "resposta": self.para_template()},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(dados.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Parametro:
    nome: str
    tipo: str  # "string" ou "integer"
    descricao: str
    obrigatorio: bool = True
    valida: Callable[[object], bool] = field(default=lambda valor: True, compare=False)


@dataclass(frozen=True)
class Ferramenta:
    nome: str
    modalidade: str
    descricao: str
    parametros: tuple[Parametro, ...]
    calcular: Callable[[AmbienteDeTreino, dict], tuple[dict, list[Evento]]] = field(compare=False)
    renderizar: Callable[[Evento], str] = field(default=lambda e: e.texto, compare=False)

    def declaracao(self) -> dict:
        """Declaração no formato de função que o template do Gemma 4 aceita em ``tools``."""
        propriedades = {p.nome: {"type": p.tipo, "description": p.descricao} for p in self.parametros}
        return {
            "type": "function",
            "function": {
                "name": self.nome,
                "description": self.descricao,
                "parameters": {
                    "type": "object",
                    "properties": propriedades,
                    "required": [p.nome for p in self.parametros if p.obrigatorio],
                },
            },
        }


def _ip(valor: object) -> bool:
    try:
        ipaddress.ip_address(str(valor))
    except ValueError:
        return False
    return True


def _usuario(valor: object) -> bool:
    return isinstance(valor, str) and 0 < len(valor) <= 128 and "\n" not in valor


def _janela(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and 1 <= valor <= JANELA_MAXIMA_S


JANELA = Parametro(
    "janela_s", "integer", f"Segundos antes da âncora, de 1 a {JANELA_MAXIMA_S}.", valida=_janela
)


def _iso(evento: Evento | None) -> str | None:
    if evento is None or evento.instante is None:
        return None
    return evento.instante.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extremos(eventos: list[Evento]) -> dict:
    return {
        "primeira": _iso(eventos[0]) if eventos else None,
        "ultima": _iso(eventos[-1]) if eventos else None,
    }


def _contagem(contador: Counter) -> dict:
    return {str(chave): contador[chave] for chave in sorted(contador, key=str)}


# --------------------------------------------------------------------------------------
# linux_auth
# --------------------------------------------------------------------------------------


def _falhas_de_login(ambiente: AmbienteDeTreino, args: dict) -> tuple[dict, list[Evento]]:
    usuario, ip = args.get("usuario"), args.get("ip")
    eventos = [
        e
        for e in ambiente.eventos("linux_auth", args["janela_s"])
        if e.tipo in TIPOS_FALHA
        and (usuario is None or e.get("usuario") == usuario)
        and (ip is None or e.ip == ip)
    ]
    def soma(tipo: str, condicao=lambda e: True) -> int:
        return sum(e.get("repeticoes", 1) for e in eventos if e.tipo == tipo and condicao(e))

    contexto = {
        "falhas_de_senha": soma("falha_de_senha"),
        "falhas_de_senha_com_usuario_invalido": soma("falha_de_senha", lambda e: bool(e.get("invalido"))),
        "avisos_de_usuario_invalido": soma("usuario_invalido"),
        "excesso_de_tentativas": soma("excesso_de_tentativas"),
        "falhas_pam": soma("falha_pam"),
        "contas_distintas": len({e.get("usuario") for e in eventos if e.get("usuario")}),
        "origens_distintas": len({e.ip for e in eventos if e.ip}),
        "conexoes": len({(e.fonte, e.get("pid")) for e in eventos if e.get("pid")}),
        **_extremos(eventos),
    }
    return contexto, eventos


def _sessoes(ambiente: AmbienteDeTreino, args: dict) -> tuple[dict, list[Evento]]:
    usuario = args["usuario"]
    eventos = [
        e
        for e in ambiente.eventos("linux_auth", args["janela_s"])
        if e.tipo in TIPOS_SESSAO and e.get("usuario") == usuario
    ]
    aceites = [e for e in eventos if e.tipo == "aceite"]
    metodos = Counter(
        e.get("metodo") if METODO_SSH.fullmatch(e.get("metodo") or "") else "outro" for e in aceites
    )
    contexto = {
        "aceites": len(aceites),
        "por_metodo": _contagem(metodos),
        "origens": sorted({e.ip for e in aceites if e.ip}),
        "sessoes_abertas": sum(1 for e in eventos if e.tipo == "sessao_aberta"),
        "sessoes_fechadas": sum(1 for e in eventos if e.tipo == "sessao_fechada"),
        **_extremos(eventos),
    }
    return contexto, eventos


# --------------------------------------------------------------------------------------
# apache
# --------------------------------------------------------------------------------------


def _requisicoes_do_cliente(ambiente: AmbienteDeTreino, args: dict) -> tuple[dict, list[Evento]]:
    eventos = [e for e in ambiente.eventos("apache", args["janela_s"]) if e.ip == args["ip"]]
    contexto = {
        "requisicoes": len(eventos),
        "por_status": _contagem(Counter(e.get("status") for e in eventos)),
        "por_metodo": _contagem(Counter(e.get("metodo") or "outro" for e in eventos)),
        "caminhos_distintos": len({e.get("caminho") for e in eventos}),
        "user_agents_distintos": len({e.get("user_agent") for e in eventos}),
        "bytes": sum(e.get("bytes", 0) for e in eventos),
        **_extremos(eventos),
    }
    return contexto, eventos


def _bloqueios_do_cliente(ambiente: AmbienteDeTreino, args: dict) -> tuple[dict, list[Evento]]:
    do_cliente = [e for e in ambiente.eventos("apache", args["janela_s"]) if e.ip == args["ip"]]
    eventos = [e for e in do_cliente if e.get("status") in BLOQUEIO_HTTP]
    contexto = {
        "bloqueios": len(eventos),
        "requisicoes_do_cliente": len(do_cliente),
        "por_status": _contagem(Counter(e.get("status") for e in eventos)),
        "caminhos_bloqueados_distintos": len({e.get("caminho") for e in eventos}),
        **_extremos(eventos),
    }
    return contexto, eventos


# --------------------------------------------------------------------------------------
# suricata
# --------------------------------------------------------------------------------------


def _ponta(ip: str | None, porta: int | None) -> str:
    if ip is None:
        return "?"
    return f"{ip}:{porta}" if porta is not None else ip


def renderizar_eve(evento: Evento) -> str:
    """Linha compacta de um evento EVE. Todo texto variável vem do log, então é Registro."""
    dados = evento.get("dados") or {}
    partes = [
        str(evento.get("relogio")),
        evento.tipo,
        (f"{_ponta(evento.get('src_ip'), evento.get('src_port'))} -> "
        f"{_ponta(evento.get('dest_ip'), evento.get('dest_port'))}"),
        str(evento.get("proto") or ""),
    ]
    if evento.tipo == "alert":
        partes.append(f"[{evento.get('signature_id')}] {evento.get('signature')}")
    for chave in ("http", "dns", "tls", "flow", "ssh", "fileinfo"):
        bloco = dados.get(chave)
        if isinstance(bloco, dict):
            campos = (
                "http_method", "hostname", "url", "status", "rrname", "rrtype", "rcode", "sni",
                "version", "pkts_toserver", "pkts_toclient", "bytes_toserver", "bytes_toclient",
                "state", "filename", "size",
            )
            texto = " ".join(f"{c}={bloco[c]}" for c in campos if c in bloco and bloco[c] is not None)
            if texto:
                partes.append(f"{chave} {texto}")
    return " | ".join(p for p in partes if p)


def _envolve(evento: Evento, ip: str) -> bool:
    return ip in (evento.get("src_ip"), evento.get("dest_ip"))


def _alertas_do_ip(ambiente: AmbienteDeTreino, args: dict) -> tuple[dict, list[Evento]]:
    ip = args["ip"]
    eventos = [
        e for e in ambiente.eventos("suricata", args["janela_s"]) if e.tipo == "alert" and _envolve(e, ip)
    ]
    contexto = {
        "alertas": len(eventos),
        "por_assinatura_id": _contagem(Counter(e.get("signature_id") for e in eventos)),
        "por_severidade": _contagem(Counter(e.get("severity") for e in eventos)),
        "como_origem": sum(1 for e in eventos if e.get("src_ip") == ip),
        "como_destino": sum(1 for e in eventos if e.get("dest_ip") == ip),
        "pares_distintos": len({frozenset((e.get("src_ip"), e.get("dest_ip"))) for e in eventos}),
        **_extremos(eventos),
    }
    return contexto, eventos


def _fluxos_entre(ambiente: AmbienteDeTreino, args: dict) -> tuple[dict, list[Evento]]:
    par = {args["ip_a"], args["ip_b"]}
    eventos = [
        e
        for e in ambiente.eventos("suricata", args["janela_s"])
        if {e.get("src_ip"), e.get("dest_ip")} == par
    ]
    portas = sorted({e.get("dest_port") for e in eventos if e.get("dest_port") is not None})
    fluxos = [(e.get("dados") or {}).get("flow") for e in eventos if e.tipo == "flow"]
    fluxos = [f for f in fluxos if isinstance(f, dict)]
    contexto = {
        "eventos": len(eventos),
        "por_tipo": _contagem(Counter(e.tipo for e in eventos)),
        "portas_de_destino": portas[:20],
        "portas_de_destino_distintas": len(portas),
        "bytes_ao_servidor": sum(int(f.get("bytes_toserver") or 0) for f in fluxos),
        "bytes_ao_cliente": sum(int(f.get("bytes_toclient") or 0) for f in fluxos),
        **_extremos(eventos),
    }
    return contexto, eventos


IP = Parametro("ip", "string", "Endereço IPv4 ou IPv6.", valida=_ip)
USUARIO = Parametro("usuario", "string", "Nome da conta como aparece no log.", valida=_usuario)

CATALOGO: dict[str, Ferramenta] = {
    f.nome: f
    for f in (
        Ferramenta(
            "falhas_de_login",
            "linux_auth",
            "Falhas de autenticação de uma conta ou de uma origem na janela até a âncora.",
            (
                Parametro("usuario", "string", "Conta (opcional).", False, _usuario),
                Parametro("ip", "string", "Origem (opcional).", False, _ip),
                JANELA,
            ),
            _falhas_de_login,
        ),
        Ferramenta(
            "sessoes",
            "linux_auth",
            "Aceites de login e sessões PAM de uma conta na janela até a âncora.",
            (USUARIO, JANELA),
            _sessoes,
        ),
        Ferramenta(
            "requisicoes_do_cliente",
            "apache",
            "Requisições HTTP de um cliente no log de acesso na janela até a âncora.",
            (IP, JANELA),
            _requisicoes_do_cliente,
        ),
        Ferramenta(
            "bloqueios_do_cliente",
            "apache",
            "Respostas de bloqueio (403, 406 ou 429) a um cliente na janela até a âncora.",
            (IP, JANELA),
            _bloqueios_do_cliente,
        ),
        Ferramenta(
            "alertas_do_ip",
            "suricata",
            "Alertas do Suricata em que o endereço é origem ou destino, na janela até a âncora.",
            (IP, JANELA),
            _alertas_do_ip,
            renderizar_eve,
        ),
        Ferramenta(
            "fluxos_entre",
            "suricata",
            "Eventos do Suricata entre dois endereços, na janela até a âncora.",
            (
                Parametro("ip_a", "string", "Primeiro endereço.", valida=_ip),
                Parametro("ip_b", "string", "Segundo endereço.", valida=_ip),
                JANELA,
            ),
            _fluxos_entre,
            renderizar_eve,
        ),
    )
}


def validar(nome: str, argumentos: dict) -> Ferramenta:
    """Confere nome, argumentos obrigatórios, tipos e limites. Levanta ``ChamadaInvalida``."""
    ferramenta = CATALOGO.get(nome)
    if ferramenta is None:
        raise ChamadaInvalida(f"ferramenta desconhecida: {nome}")
    if not isinstance(argumentos, dict):
        raise ChamadaInvalida("argumentos precisam ser um objeto")
    conhecidos = {p.nome: p for p in ferramenta.parametros}
    extras = sorted(set(argumentos) - set(conhecidos))
    if extras:
        raise ChamadaInvalida(f"argumentos desconhecidos: {', '.join(extras)}")
    for parametro in ferramenta.parametros:
        if parametro.nome not in argumentos or argumentos[parametro.nome] is None:
            if parametro.obrigatorio:
                raise ChamadaInvalida(f"falta o argumento {parametro.nome}")
            continue
        if not parametro.valida(argumentos[parametro.nome]):
            raise ChamadaInvalida(f"valor inválido para {parametro.nome}")
    if nome == "falhas_de_login" and not (argumentos.get("usuario") or argumentos.get("ip")):
        raise ChamadaInvalida("informe usuario ou ip")
    return ferramenta


def executar(
    ambiente: AmbienteDeTreino, nome: str, argumentos: dict, limite: int = LIMITE_DE_LINHAS
) -> Resposta:
    """Executa uma chamada. Chamadas inválidas voltam como resposta com ``erro``."""
    try:
        ferramenta = validar(nome, argumentos)
    except ChamadaInvalida as erro:
        return Resposta(nome, dict(argumentos) if isinstance(argumentos, dict) else {}, {}, (), 0, str(erro))
    args = {chave: valor for chave, valor in argumentos.items() if valor is not None}
    contexto, eventos = ferramenta.calcular(ambiente, args)
    mostrados = eventos[-limite:] if limite else []
    return Resposta(
        nome,
        args,
        contexto,
        tuple(ferramenta.renderizar(e) for e in mostrados),
        len(eventos),
    )


def declaracoes(modalidades: tuple[str, ...] | None = None) -> list[dict]:
    return [
        f.declaracao()
        for f in CATALOGO.values()
        if modalidades is None or f.modalidade in modalidades
    ]
