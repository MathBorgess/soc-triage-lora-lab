"""Perfis do Projetor que reproduzem formatos de lotes da v12.

Cada perfil reproduz um molde que o script de um lote aplicou a toda a família, calculado só a
partir das linhas citadas pelo localizador nativo e da janela que o lote registrou. Um resumo
escrito à mão para um episódio não é molde de família e fica fora dos perfis.

Os perfis separam Contexto e Registro: cabeçalhos e contagens são Contexto; linhas copiadas do log
e linhas que misturam contagens com texto do log (conta, caminho, user-agent) são Registro.
"""

from __future__ import annotations

import ipaddress
import json
import re
from collections import Counter
from datetime import UTC, datetime

from .recorte import Linha, Recorte, contexto, registro
from .v12 import Chave, ExemploV12, Leitor, Perfil, PerfilNaoAplicavel, alcance_padrao


def _fonte_unica(exemplo: ExemploV12) -> tuple[str, str]:
    chaves = {(item.arquivo, item.membro) for item in exemplo.nativo}
    if len(chaves) != 1:
        raise PerfilNaoAplicavel(f"{len(chaves)} fontes citadas; o perfil espera uma")
    return chaves.pop()


def _linhas_citadas(exemplo: ExemploV12) -> list[int]:
    return [item.linha for item in exemplo.nativo]


def _duracao_l15(segundos: float) -> str:
    """Duração no formato dos lotes 15 e 16."""
    segundos = round(segundos)
    if segundos < 60:
        return f"{segundos} s"
    minutos, resto = divmod(segundos, 60)
    if minutos < 60:
        return f"{minutos} min {resto} s" if resto else f"{minutos} min"
    horas, minutos = divmod(minutos, 60)
    return f"{horas} h {minutos} min" if minutos else f"{horas} h"


# --------------------------------------------------------------------------------------
# Lote 08, CasinoLimit (família CAS): rajadas de SSH numa linha de resumo.
# --------------------------------------------------------------------------------------

_CAS_SSHD = re.compile(r"\bsshd\[(\d+)\]:\s+(.*)$")
_CAS_AUTH = re.compile(r"^(Accepted|Failed) ([\w/-]+) for (invalid user )?(\S+) from (\S+) port (\d+)\b")
_CAS_INVALIDO = re.compile(r"^Invalid user (\S+) from (\S+) port (\d+)\b")
_CAS_PAM = re.compile(r"^pam_unix\((?:sshd|ssh):session\): session (opened|closed) for user ([^\s(]+)")


def _ip_ou_vazio(valor: str) -> str:
    try:
        return str(ipaddress.ip_address(valor))
    except ValueError:
        return ""


def _cas_evento(texto: str) -> dict | None:
    achado = _CAS_SSHD.search(texto)
    if not achado:
        return None
    pid, mensagem = achado.groups()
    base = {"quando": datetime.fromisoformat(texto.split()[0]), "pid": pid}
    if auth := _CAS_AUTH.match(mensagem):
        verbo, metodo, invalido, usuario, origem, porta = auth.groups()
        resultado = "aceitou" if verbo == "Accepted" else "recusou"
        return base | {
            "resultado": resultado, "metodo": metodo, "invalido": bool(invalido),
            "usuario": usuario, "ip": _ip_ou_vazio(origem), "porta": porta,
        }
    if invalido := _CAS_INVALIDO.match(mensagem):
        usuario, origem, porta = invalido.groups()
        return base | {
            "resultado": "usuário inválido", "metodo": "", "invalido": True,
            "usuario": usuario, "ip": _ip_ou_vazio(origem), "porta": porta,
        }
    if pam := _CAS_PAM.match(mensagem):
        return base | {
            "resultado": f"PAM {pam[1]}", "metodo": "", "invalido": False,
            "usuario": pam[2], "ip": "", "porta": "",
        }
    return None


def projetar_cas(exemplo: ExemploV12, leitor: Leitor) -> Recorte:
    arquivo, membro = _fonte_unica(exemplo)
    eventos = [_cas_evento(leitor.texto(arquivo, membro, n)) for n in _linhas_citadas(exemplo)]
    if any(evento is None for evento in eventos):
        raise PerfilNaoAplicavel("linha citada fora do formato de SSH do lote")
    eventos.sort(key=lambda e: e["quando"])
    origens = {e["ip"] for e in eventos}
    if len(origens) != 1 or "" in origens:
        raise PerfilNaoAplicavel("a janela não tem uma origem única")
    falhas = [e for e in eventos if e["resultado"] != "aceitou"]
    aceites = [e for e in eventos if e["resultado"] == "aceitou"]
    contas = {e["usuario"] for e in falhas}
    conexoes = {(e["pid"], e["porta"]) for e in falhas}
    invalidos = sum(e["invalido"] for e in falhas)
    duracao = (eventos[-1]["quando"] - eventos[0]["quando"]).total_seconds()
    host = membro.split("/")[2]
    texto = (
        f"{eventos[-1]['quando'].isoformat()} {host} programa=sshd origem={origens.pop()}. "
        f"Entre {eventos[0]['quando'].isoformat()} e a âncora, houve {len(falhas)} registros de recusa "
        f"ou usuário inválido em {len(conexoes)} conexões distintas, para {len(contas)} conta(s). "
        f"{invalidos} registros indicam usuário inválido. Duração observada {duracao:.1f} s."
    )
    if aceites:
        texto += (
            f" Na âncora, o sshd aceitou por {aceites[-1]['metodo']} a mesma origem e uma das contas "
            "anteriormente recusadas."
        )
    # O host vem do nome do membro e o método do log: a linha inteira é Registro.
    return Recorte("linux_auth", (registro(texto, "resumo_da_janela"),), perfil="lote08_cas")


# --------------------------------------------------------------------------------------
# Lote 15, validação no syslog do CSE-CIC-IDS2018 (família L15-RSVA, grupo 2018-02-14).
# --------------------------------------------------------------------------------------

_SYSLOG_L15 = re.compile(
    r"^(?P<stamp>[A-Z][a-z]{2} +\d{1,2} \d\d:\d\d:\d\d) (?P<host>\S+) "
    r"(?P<prog>[^\s\[:]+)(?:\[(?P<pid>\d+)\])?: (?P<body>.*)$"
)
_RUIM_L15 = re.compile(r"(?i)failed|denied|invalid|error|refused")
_SESSAO_UBUNTU = re.compile(r"Started Session (\d+) of user ubuntu")
GRUPO_L15_VALIDACAO = "cse-cic-ids2018/2018-02-14"
# Episódios em que o script do lote 15 acrescentou a última sessão de ubuntu (with_session=True).
L15_RSVA_COM_SESSAO = frozenset({"tmpfiles-22", "tcpdump-cron-18", "tcpdump-cron-27"})


def _janela_registrada(exemplo: ExemploV12) -> tuple[int, int]:
    janela = (exemplo.meta or {}).get("janela_agregada") or {}
    if not janela.get("linhas"):
        raise PerfilNaoAplicavel("o lote não registrou a janela agregada")
    inicio, fim = (int(parte) for parte in janela["linhas"].split("-"))
    return inicio, fim


def _l15_val_alcance(exemplo: ExemploV12) -> dict[Chave, set[int]]:
    pedidos = alcance_padrao(exemplo)
    for numeros in pedidos.values():
        numeros |= set(range(1, max(numeros) + 1))
    return pedidos


def _l15_registro_syslog(texto: str) -> dict:
    achado = _SYSLOG_L15.match(texto)
    if not achado:
        raise PerfilNaoAplicavel("linha fora do formato syslog do lote 15")
    quando = datetime.strptime("2018 " + " ".join(achado["stamp"].split()), "%Y %b %d %H:%M:%S")
    return {**achado.groupdict(), "quando": quando}


def projetar_l15_rsva_validacao(exemplo: ExemploV12, leitor: Leitor) -> Recorte:
    if exemplo.grupo != GRUPO_L15_VALIDACAO:
        raise PerfilNaoAplicavel("o perfil cobre só a validação do lote 15 (CSE-CIC-IDS2018)")
    arquivo, membro = _fonte_unica(exemplo)
    inicio, ancora = _janela_registrada(exemplo)
    mostradas = _linhas_citadas(exemplo)
    if mostradas[-1] != ancora:
        raise PerfilNaoAplicavel("a última linha citada não é a âncora")
    registros = {n: _l15_registro_syslog(leitor.texto(arquivo, membro, n)) for n in range(inicio, ancora + 1)}
    programas: Counter = Counter()
    ruins = 0
    for numero in range(inicio, ancora + 1):
        programas[re.sub(r"\[\d+\]", "", registros[numero]["prog"])] += 1
        ruins += bool(_RUIM_L15.search(registros[numero]["body"]))
    t0, t1 = registros[inicio]["quando"], registros[ancora]["quando"]
    ordem = ", ".join(f"{quantidade} {nome}" for nome, quantidade in programas.most_common())
    seguranca = sum(programas[nome] for nome in ("sshd", "sudo", "su", "login"))
    host = membro.rsplit(".", 1)[-1]
    linhas: list[Linha] = [
        contexto(f"syslog do host ip-172-31-69-{host} (Ubuntu). Syslog sem ano e sem fuso.", "cabecalho"),
        # A ordem cita nomes de programa vindos do log: a linha é Registro.
        registro(
            f"Na janela de {_duracao_l15((t1 - t0).total_seconds())} até a âncora "
            f"({t0:%H:%M:%S} a {t1:%H:%M:%S}): {ancora - inicio + 1} linhas ({ordem}); "
            f"linhas de sshd, sudo, su ou login: {seguranca}; "
            f"linhas com failed, denied, invalid, error ou refused: {ruins}.",
            "resumo_da_janela",
        ),
    ]
    episodio = exemplo.incidente.rsplit("/", 1)[-1]
    if episodio in L15_RSVA_COM_SESSAO:
        sessoes = [
            n for n in range(1, ancora)
            if _SESSAO_UBUNTU.search(_l15_registro_syslog(leitor.texto(arquivo, membro, n))["body"])
        ]
        if sessoes:
            ultima = _l15_registro_syslog(leitor.texto(arquivo, membro, sessoes[-1]))
            intervalo = (t1 - ultima["quando"]).total_seconds()
            linhas.append(
                contexto(
                    f"A última sessão de ubuntu começou às {ultima['stamp'].split()[-1]}, "
                    f"{_duracao_l15(intervalo)} antes.",
                    "sessoes",
                )
            )
    linhas += [registro(leitor.texto(arquivo, membro, n), "linha_do_log") for n in mostradas]
    return Recorte("linux_auth", tuple(linhas), perfil="lote15_rsva_validacao")


# --------------------------------------------------------------------------------------
# Lote 13, DNS, TLS e fluxo correlacionados no EVE do AIT-LDS v2.1 (família AITTLS).
# --------------------------------------------------------------------------------------


def _utc_micro(texto: str) -> str:
    instante = datetime.fromisoformat(texto).astimezone(UTC)
    return instante.isoformat(timespec="microseconds").replace("+00:00", "Z")


def projetar_aittls(exemplo: ExemploV12, leitor: Leitor) -> Recorte:
    arquivo, membro = _fonte_unica(exemplo)
    papeis: dict[str, dict] = {}
    for numero in _linhas_citadas(exemplo):
        linha = json.loads(leitor.texto(arquivo, membro, numero))
        tipo = linha.get("event_type")
        evento = linha.get(tipo) or {}
        if tipo == "dns":
            papeis["consulta" if evento.get("type") == "query" else "resposta"] = linha
        elif tipo == "tls":
            papeis["tls"] = linha
        elif tipo == "flow":
            novo_sem_resposta = evento.get("state") == "new" and not evento.get("pkts_toclient")
            papeis["tentativa" if novo_sem_resposta else "fluxo"] = linha
    if not {"consulta", "resposta", "tls", "fluxo"} <= set(papeis):
        raise PerfilNaoAplicavel("faltam eventos de DNS, TLS ou fluxo na janela citada")
    fluxo, resposta = papeis["fluxo"], papeis["resposta"]
    cliente, destino = fluxo["src_ip"], fluxo["dest_ip"]
    if not (_ip_ou_vazio(cliente) and _ip_ou_vazio(destino)):
        raise PerfilNaoAplicavel("endereços do fluxo fora do formato IP")
    tipo_rr = resposta["dns"]["rrtype"]
    alias = any(a.get("rrtype") == "CNAME" for a in resposta["dns"].get("answers", []))
    dados_fluxo = fluxo["flow"]
    consulta, tls = papeis["consulta"], papeis["tls"]
    eventos = [
        f"{_utc_micro(consulta['timestamp'])} | dns consulta nome_1 tipo={tipo_rr}",
        (
            f"{_utc_micro(resposta['timestamp'])} | dns resposta nome_1 NOERROR "
            f"com endereço={destino} e CNAME={int(alias)}"
        ),
        f"{_utc_micro(tls['timestamp'])} | tls nome_1 | versão={tls['tls']['version']}",
        (
            f"{_utc_micro(fluxo['timestamp'])} | flow app=tls | estado={dados_fluxo['state']} | "
            f"pacotes cliente→servidor={dados_fluxo.get('pkts_toserver', 0)} "
            f"servidor→cliente={dados_fluxo.get('pkts_toclient', 0)}"
        ),
    ]
    if "tentativa" in papeis:
        tentativa = papeis["tentativa"]
        eventos.append(
            f"{_utc_micro(tentativa['timestamp'])} | tentativa TCP anterior ao mesmo destino | "
            f"estado=new | enviados={tentativa['flow'].get('pkts_toserver', 0)} recebidos=0"
        )
    linhas = [contexto(f"Suricata EVE | src_ip={cliente} | dest_ip={destino}", "cabecalho")]
    # O nome consultado vira o pseudônimo nome_1; versão e estado vêm do sensor, mas a linha
    # copia campos do log e fica no Registro.
    linhas += [registro(texto, "evento_eve") for texto in sorted(eventos)]
    return Recorte("suricata", tuple(linhas), perfil="lote13_aittls")


PERFIS: tuple[Perfil, ...] = (
    Perfil("lote08_cas", ("CAS",), projetar_cas),
    Perfil(
        "lote15_rsva_validacao",
        ("L15-RSVA",),
        projetar_l15_rsva_validacao,
        _l15_val_alcance,
        lambda exemplo: exemplo.grupo == GRUPO_L15_VALIDACAO,
    ),
    Perfil("lote13_aittls", ("AITTLS",), projetar_aittls),
)
