"""Leitura das linhas de log das Modalidades linux_auth, apache e suricata em Eventos.

Um Evento guarda a linha literal (que entra como Registro), o instante e os campos que regras
estritas extraem dela. Os campos numéricos, de horário e de endereço passam por validação e podem
entrar no Contexto. Nomes de conta, caminhos, comandos e user-agents vêm do log e só entram no
Registro.

Relógios sem fuso (syslog BSD) são tratados como UTC. Syslog sem ano recebe o ano informado e
avança um ano quando o mês volta (dezembro seguido de janeiro).
"""

from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

MESES = {nome: numero for numero, nome in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1
)}

SYSLOG_BSD = re.compile(
    r"^(?P<mes>[A-Z][a-z]{2}) +(?P<dia>\d{1,2}) (?P<hora>\d\d:\d\d:\d\d) (?P<host>\S+) "
    r"(?P<programa>[^\s\[:]+)(?:\[(?P<pid>\d+)\])?: ?(?P<mensagem>.*)$"
)
SYSLOG_ISO = re.compile(
    r"^(?P<carimbo>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:?\d\d)?) (?P<host>\S+) "
    r"(?P<programa>[^\s\[:]+)(?:\[(?P<pid>\d+)\])?: ?(?P<mensagem>.*)$"
)

_USUARIO = r"(?P<usuario>.*?)"
_IP = r"(?P<ip>[0-9A-Fa-f:.]+)"
REGRAS_AUTH: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "falha_de_senha",
        re.compile(
            r"^message repeated (?P<repeticoes>\d+) times: \[ Failed (?P<metodo>\S+) for "
            r"(?P<invalido>invalid user )?" + _USUARIO + r" from " + _IP + r" port (?P<porta>\d+)"
        ),
    ),
    (
        "falha_de_senha",
        re.compile(
            r"^Failed (?P<metodo>\S+) for (?P<invalido>(?:invalid|illegal) user )?" + _USUARIO
            + r" from " + _IP + r" port (?P<porta>\d+)"
        ),
    ),
    ("usuario_invalido", re.compile(r"^(?:Invalid|Illegal) user " + _USUARIO + r" from " + _IP)),
    (
        "excesso_de_tentativas",
        re.compile(
            r"^error: maximum authentication attempts exceeded for (?:invalid user )?" + _USUARIO
            + r" from " + _IP
        ),
    ),
    (
        "excesso_de_tentativas",
        re.compile(r"^Disconnecting: Too many authentication failures(?: for " + _USUARIO + r")?\b"),
    ),
    (
        "falha_pam",
        re.compile(
            r"^pam_unix\((?P<servico>[^:)]+):auth\): authentication failure;.*?rhost=(?P<ip>\S*)"
            r"(?:\s+user=(?P<usuario>\S+))?"
        ),
    ),
    (
        "aceite",
        re.compile(
            r"^Accepted (?P<metodo>\S+) for " + _USUARIO + r" from " + _IP + r" port (?P<porta>\d+)"
        ),
    ),
    (
        "sessao_aberta",
        re.compile(
            r"^pam_unix\((?P<servico>[^:)]+):session\): session opened for user "
            r"(?P<usuario>[^\s(]+)"
        ),
    ),
    (
        "sessao_fechada",
        re.compile(
            r"^pam_unix\((?P<servico>[^:)]+):session\): session closed for user (?P<usuario>\S+)"
        ),
    ),
    (
        "sudo",
        re.compile(
            r"^\s*(?P<usuario>\S+) : (?:(?P<falhas>\d+) incorrect password attempts? ; )?"
            r"(?P<negado>user NOT in sudoers ; )?TTY=(?P<tty>\S+) ; PWD=(?P<pwd>.*?) ; "
            r"USER=(?P<alvo>\S+) ; (?:COMMAND=(?P<comando>.*))?$"
        ),
    ),
    ("su", re.compile(r"^(?P<resultado>Successful|FAILED) su for (?P<alvo>\S+) by (?P<usuario>\S+)")),
    ("su", re.compile(r"^\((?P<alvo>to \S+)\) (?P<usuario>\S+) on (?P<tty>\S+)")),
    ("cron", re.compile(r"^\((?P<usuario>[^)]+)\) CMD \((?P<comando>.*)\)$")),
    ("quebra_de_mapeamento", re.compile(r".*\[" + _IP + r"\] failed - POSSIBLE BREAK-IN ATTEMPT")),
    (
        "conexao_encerrada",
        re.compile(
            r"^(?:Connection closed by|Disconnected from|Received disconnect from|"
            r"Connection reset by)(?: (?:authenticating|invalid) user (?P<usuario>\S+))? " + _IP
        ),
    ),
)


def _ip_valido(texto: str | None) -> str | None:
    if not texto:
        return None
    try:
        return str(ipaddress.ip_address(texto))
    except ValueError:
        return None


@dataclass(frozen=True)
class Evento:
    modalidade: str
    fonte: str
    linha: int
    texto: str
    instante: datetime | None
    tipo: str
    campos: dict = field(default_factory=dict, compare=False, hash=False)

    def get(self, chave: str, padrao=None):
        return self.campos.get(chave, padrao)

    @property
    def ip(self) -> str | None:
        return self.campos.get("ip")


class RelogioSyslog:
    """Atribui ano a carimbos BSD em ordem de leitura, avançando na virada de ano."""

    def __init__(self, ano: int):
        self.ano = ano
        self._mes_anterior: int | None = None

    def instante(self, mes: str, dia: str, hora: str) -> datetime:
        numero = MESES[mes]
        if self._mes_anterior is not None and numero < self._mes_anterior - 6:
            self.ano += 1
        self._mes_anterior = numero
        h, m, s = (int(parte) for parte in hora.split(":"))
        return datetime(self.ano, numero, int(dia), h, m, s, tzinfo=UTC)


def instante_iso(texto: str) -> datetime:
    valor = datetime.fromisoformat(texto)
    return valor if valor.tzinfo else valor.replace(tzinfo=UTC)


def ler_auth(texto: str, fonte: str, linha: int, relogio: RelogioSyslog | None) -> Evento:
    """Uma linha de auth.log, secure ou syslog."""
    bsd = SYSLOG_BSD.match(texto)
    iso = None if bsd else SYSLOG_ISO.match(texto)
    if not (bsd or iso):
        return Evento("linux_auth", fonte, linha, texto, None, "fora_do_formato", {})
    achado = bsd or iso
    if bsd:
        instante = (relogio or RelogioSyslog(2000)).instante(bsd["mes"], bsd["dia"], bsd["hora"])
    else:
        instante = instante_iso(iso["carimbo"])
    campos = {
        "host": achado["host"],
        "programa": achado["programa"],
        "pid": achado["pid"],
        "relogio": texto[: achado.start("host") - 1],
    }
    mensagem = achado["mensagem"]
    tipo = "outro"
    for nome, regra in REGRAS_AUTH:
        regra_achada = regra.match(mensagem)
        if regra_achada:
            tipo = nome
            extras = {k: v for k, v in regra_achada.groupdict().items() if v is not None}
            campos.update(extras)
            break
    if "ip" in campos:
        campos["ip"] = _ip_valido(campos["ip"])
    campos["repeticoes"] = int(campos.get("repeticoes", 1))
    campos["mensagem"] = mensagem
    return Evento("linux_auth", fonte, linha, texto, instante, tipo, campos)


APACHE = re.compile(
    r"^(?:(?P<vhost>\S+) )?(?P<cliente>\S+) (?P<ident>\S+) (?P<usuario_http>\S+) "
    r"\[(?P<carimbo>\d\d/[A-Z][a-z]{2}/\d{4}:\d\d:\d\d:\d\d [+-]\d{4})\] "
    r'"(?P<requisicao>(?:[^"\\]|\\.)*)" (?P<status>\d{3}) (?P<bytes>\S+)'
    r'(?: "(?P<referer>(?:[^"\\]|\\.)*)" "(?P<user_agent>(?:[^"\\]|\\.)*)")?'
)


def ler_apache(texto: str, fonte: str, linha: int) -> Evento:
    achado = APACHE.match(texto)
    if not achado:
        return Evento("apache", fonte, linha, texto, None, "fora_do_formato", {})
    instante = datetime.strptime(achado["carimbo"], "%d/%b/%Y:%H:%M:%S %z")
    partes = achado["requisicao"].split(" ")
    metodo, caminho, protocolo = (partes + ["", "", ""])[:3] if len(partes) >= 2 else ("", "", "")
    campos = {k: v for k, v in achado.groupdict().items() if v is not None}
    campos.update(
        ip=_ip_valido(achado["cliente"]),
        metodo=metodo if re.fullmatch(r"[A-Z]{3,10}", metodo or "") else None,
        caminho=caminho,
        protocolo=protocolo,
        status=int(achado["status"]),
        bytes=int(achado["bytes"]) if achado["bytes"].isdigit() else 0,
        relogio=achado["carimbo"],
    )
    return Evento("apache", fonte, linha, texto, instante, "requisicao", campos)


def ler_eve(texto: str, fonte: str, linha: int) -> Evento:
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError:
        return Evento("suricata", fonte, linha, texto, None, "fora_do_formato", {})
    if not isinstance(dados, dict):
        return Evento("suricata", fonte, linha, texto, None, "fora_do_formato", {})
    try:
        instante = instante_iso(str(dados.get("timestamp", "")))
    except ValueError:
        instante = None
    alerta = dados.get("alert") if isinstance(dados.get("alert"), dict) else {}
    campos = {
        "dados": dados,
        "event_type": dados.get("event_type"),
        "src_ip": _ip_valido(dados.get("src_ip")),
        "dest_ip": _ip_valido(dados.get("dest_ip")),
        "src_port": dados.get("src_port") if isinstance(dados.get("src_port"), int) else None,
        "dest_port": dados.get("dest_port") if isinstance(dados.get("dest_port"), int) else None,
        "proto": dados.get("proto"),
        "signature_id": alerta.get("signature_id") if isinstance(alerta.get("signature_id"), int)
        else None,
        "signature": alerta.get("signature"),
        "severity": alerta.get("severity") if isinstance(alerta.get("severity"), int) else None,
        "relogio": dados.get("timestamp"),
    }
    tipo = str(dados.get("event_type") or "sem_tipo")
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", tipo):
        tipo = "outro"
    return Evento("suricata", fonte, linha, texto, instante, tipo, campos)


def ler(modalidade: str, texto: str, fonte: str, linha: int, relogio: RelogioSyslog | None = None):
    if modalidade == "linux_auth":
        return ler_auth(texto, fonte, linha, relogio)
    if modalidade == "apache":
        return ler_apache(texto, fonte, linha)
    if modalidade == "suricata":
        return ler_eve(texto, fonte, linha)
    raise ValueError(f"Modalidade sem leitor: {modalidade}")
