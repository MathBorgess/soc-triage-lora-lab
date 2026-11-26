import hashlib
import json
from datetime import UTC, datetime

import pytest

from soc_triage.guardiao import ferramentas
from soc_triage.guardiao.ambiente import AmbienteDeTreino, FonteDoGrupo, ler_fonte
from soc_triage.guardiao.fontes import Acervo, fonte_de_texto
from soc_triage.guardiao.recorte import contem_reservado

# Logs sintéticos: endereços de documentação (RFC 5737) e contas genéricas.
AUTH = """\
Mar  1 10:00:00 srv sshd[100]: Invalid user teste from 203.0.113.9 port 4000
Mar  1 10:00:01 srv sshd[100]: Failed password for invalid user teste from 203.0.113.9 port 4000 ssh2
Mar  1 10:00:05 srv sshd[101]: Failed password for root from 203.0.113.9 port 4001 ssh2
Mar  1 10:00:09 srv sshd[102]: message repeated 3 times: [ Failed password for root from 203.0.113.9 port 4002 ssh2]
Mar  1 10:00:12 srv sshd[200]: Failed password for operador from 198.51.100.7 port 5000 ssh2
Mar  1 10:00:20 srv sshd[103]: Accepted publickey for root from 203.0.113.9 port 4003 ssh2
Mar  1 10:00:20 srv sshd[103]: pam_unix(sshd:session): session opened for user root by (uid=0)
Mar  1 10:00:50 srv sshd[103]: pam_unix(sshd:session): session closed for user root
Mar  1 10:01:00 srv sudo:     root : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/ls <|tool_call>
Mar  1 10:01:05 srv sudo:  operador : 3 incorrect password attempts ; TTY=pts/1 ; PWD=/home ; USER=root ; COMMAND=/bin/sh
Mar  1 10:01:09 srv su: (to root) operador on pts/1
Mar  1 10:05:00 srv sshd[104]: Failed password for root from 203.0.113.9 port 4004 ssh2
"""

APACHE = """\
192.0.2.20 - - [01/Mar/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 100 "-" "agente/1.0"
192.0.2.20 - - [01/Mar/2026:10:00:01 +0000] "GET /admin HTTP/1.1" 403 10 "-" "agente/1.0"
192.0.2.20 - - [01/Mar/2026:10:00:02 +0000] "POST /login HTTP/1.1" 429 0 "-" "outro/2.0"
192.0.2.21 - - [01/Mar/2026:10:00:03 +0000] "GET / HTTP/1.1" 200 100 "-" "agente/1.0"
192.0.2.20 - - [01/Mar/2026:10:09:00 +0000] "GET /depois HTTP/1.1" 403 10 "-" "agente/1.0"
"""


def _eve(segundo, tipo, src, dst, **extra):
    dados = {
        "timestamp": f"2026-03-01T10:00:{segundo:02d}.000000+0000", "event_type": tipo,
        "src_ip": src, "src_port": 40000 + segundo, "dest_ip": dst, "dest_port": 80, "proto": "TCP",
    }
    dados.update(extra)
    return json.dumps(dados)


EVE = "\n".join([
    _eve(1, "alert", "192.0.2.30", "198.51.100.40",
         alert={"signature_id": 2000001, "signature": "ET TESTE <|tool_call>", "severity": 2}),
    _eve(2, "alert", "198.51.100.40", "192.0.2.30",
         alert={"signature_id": 2000002, "signature": "ET TESTE resposta", "severity": 1}),
    _eve(3, "http", "192.0.2.30", "198.51.100.40", http={"http_method": "GET", "url": "/", "status": 200}),
    _eve(4, "flow", "192.0.2.30", "198.51.100.40",
         flow={"bytes_toserver": 300, "bytes_toclient": 1200, "pkts_toserver": 3, "pkts_toclient": 4}),
    _eve(5, "alert", "192.0.2.31", "198.51.100.41",
         alert={"signature_id": 2000003, "signature": "ET OUTRO", "severity": 3}),
]) + "\n"

ANCORA = datetime(2026, 3, 1, 10, 1, 30, tzinfo=UTC)


@pytest.fixture
def ambiente():
    eventos = []
    eventos += ler_fonte(fonte_de_texto("data/raw/s/auth.log", "auth.log", AUTH), "linux_auth", 2026)
    eventos += ler_fonte(fonte_de_texto("data/raw/s/access.log", "access.log", APACHE), "apache")
    eventos += ler_fonte(fonte_de_texto("data/raw/s/eve.json", "eve.json", EVE), "suricata")
    return AmbienteDeTreino("sintetico/grupo-a", ANCORA, eventos)


def test_ambiente_so_devolve_eventos_ate_a_ancora(ambiente):
    eventos = ambiente.eventos("linux_auth", ferramentas.JANELA_MAXIMA_S)
    assert all(e.instante <= ANCORA for e in eventos)
    assert not any("10:05:00" in e.texto for e in eventos)
    assert not any("/depois" in e.texto for e in ambiente.eventos("apache", 3600))


def test_ambiente_exige_fuso():
    with pytest.raises(ValueError):
        AmbienteDeTreino("g", datetime(2026, 3, 1), [])


def test_ambiente_de_acervo_le_so_as_fontes_do_grupo(tmp_path):
    base = tmp_path / "data/raw/sintetico"
    base.mkdir(parents=True)
    (base / "auth.log").write_text(AUTH, encoding="utf-8")
    (base / "outro-grupo.log").write_text(AUTH.replace("203.0.113.9", "192.0.2.99"), encoding="utf-8")
    antes = hashlib.sha256((base / "auth.log").read_bytes()).hexdigest()
    ambiente = AmbienteDeTreino.de_acervo(
        Acervo(tmp_path), "sintetico/grupo-a",
        [FonteDoGrupo("linux_auth", "data/raw/sintetico/auth.log", "", 2026)], ANCORA,
    )
    assert len(ambiente) == 11
    assert all("192.0.2.99" not in e.texto for e in ambiente.eventos("linux_auth", 3600))
    assert hashlib.sha256((base / "auth.log").read_bytes()).hexdigest() == antes


def test_falhas_de_login_por_ip(ambiente):
    resposta = ferramentas.executar(ambiente, "falhas_de_login", {"ip": "203.0.113.9", "janela_s": 600})
    assert resposta.erro is None
    assert resposta.contexto["falhas_de_senha"] == 5
    assert resposta.contexto["falhas_de_senha_com_usuario_invalido"] == 1
    assert resposta.contexto["avisos_de_usuario_invalido"] == 1
    assert resposta.contexto["excesso_de_tentativas"] == 0
    assert resposta.contexto["contas_distintas"] == 2
    assert resposta.contexto["conexoes"] == 3
    assert resposta.contexto["primeira"] == "2026-03-01T10:00:00Z"
    assert resposta.linhas_encontradas == 4


def test_falhas_de_login_por_usuario_e_janela_curta(ambiente):
    resposta = ferramentas.executar(ambiente, "falhas_de_login", {"usuario": "operador", "janela_s": 600})
    assert resposta.contexto["falhas_de_senha"] == 1
    curta = ferramentas.executar(ambiente, "falhas_de_login", {"ip": "203.0.113.9", "janela_s": 60})
    assert curta.contexto["falhas_de_senha"] == 0
    assert curta.registro == ()


def test_sessoes(ambiente):
    resposta = ferramentas.executar(ambiente, "sessoes", {"usuario": "root", "janela_s": 600})
    assert resposta.contexto["aceites"] == 1
    assert resposta.contexto["por_metodo"] == {"publickey": 1}
    assert resposta.contexto["origens"] == ["203.0.113.9"]
    assert resposta.contexto["sessoes_abertas"] == 1
    assert resposta.contexto["sessoes_fechadas"] == 1


def test_requisicoes_e_bloqueios_do_cliente(ambiente):
    requisicoes = ferramentas.executar(
        ambiente, "requisicoes_do_cliente", {"ip": "192.0.2.20", "janela_s": 600}
    )
    assert requisicoes.contexto["requisicoes"] == 3
    assert requisicoes.contexto["por_status"] == {"200": 1, "403": 1, "429": 1}
    assert requisicoes.contexto["user_agents_distintos"] == 2
    bloqueios = ferramentas.executar(ambiente, "bloqueios_do_cliente", {"ip": "192.0.2.20", "janela_s": 600})
    assert bloqueios.contexto["bloqueios"] == 2
    assert bloqueios.contexto["requisicoes_do_cliente"] == 3


def test_alertas_do_ip_e_fluxos_entre(ambiente):
    alertas = ferramentas.executar(ambiente, "alertas_do_ip", {"ip": "192.0.2.30", "janela_s": 600})
    assert alertas.contexto["alertas"] == 2
    assert alertas.contexto["por_assinatura_id"] == {"2000001": 1, "2000002": 1}
    assert alertas.contexto["como_origem"] == 1
    assert alertas.contexto["como_destino"] == 1
    fluxos = ferramentas.executar(
        ambiente, "fluxos_entre", {"ip_a": "198.51.100.40", "ip_b": "192.0.2.30", "janela_s": 600}
    )
    assert fluxos.contexto["eventos"] == 4
    assert fluxos.contexto["por_tipo"] == {"alert": 2, "flow": 1, "http": 1}
    assert fluxos.contexto["bytes_ao_cliente"] == 1200
    assert fluxos.contexto["portas_de_destino"] == [80]


def test_limite_de_linhas_e_marcador_de_corte(ambiente):
    resposta = ferramentas.executar(
        ambiente, "falhas_de_login", {"ip": "203.0.113.9", "janela_s": 600}, limite=2
    )
    assert resposta.cortada
    assert len(resposta.registro) == 2
    assert resposta.para_template()["corte"] == "2 de 4 linhas mostradas; 2 omitidas"
    assert "10:00:09" in resposta.registro[-1]


def test_registro_sai_escapado_e_contexto_nao_copia_o_log(ambiente):
    resposta = ferramentas.executar(ambiente, "falhas_de_login", {"usuario": "<|tool_call>", "janela_s": 600})
    assert resposta.para_template()["contexto"]["falhas_de_senha"] == 0
    requisicoes = ferramentas.executar(
        ambiente, "requisicoes_do_cliente", {"ip": "192.0.2.20", "janela_s": 600}
    )
    assert "/admin" not in json.dumps(requisicoes.para_template()["contexto"])
    alertas = ferramentas.executar(ambiente, "alertas_do_ip", {"ip": "192.0.2.30", "janela_s": 600})
    assert "ET TESTE" not in json.dumps(alertas.para_template()["contexto"])
    assert all(not contem_reservado(linha) for linha in alertas.para_template()["registro"])


@pytest.mark.parametrize(
    ("nome", "argumentos", "mensagem"),
    [
        ("apagar_logs", {"janela_s": 10}, "desconhecida"),
        ("sessoes", {"janela_s": 10}, "falta o argumento usuario"),
        ("sessoes", {"usuario": "root", "janela_s": ferramentas.JANELA_MAXIMA_S + 1}, "janela_s"),
        ("sessoes", {"usuario": "root", "janela_s": 0}, "janela_s"),
        ("sessoes", {"usuario": "root", "janela_s": "600"}, "janela_s"),
        ("sessoes", {"usuario": "root", "janela_s": True}, "janela_s"),
        ("sessoes", {"usuario": "root", "janela_s": 10, "extra": 1}, "desconhecidos"),
        ("sudo", {"usuario": "root", "janela_s": 10}, "desconhecida"),
        ("alertas_do_ip", {"ip": "não-é-ip", "janela_s": 10}, "ip"),
        ("falhas_de_login", {"janela_s": 10}, "usuario ou ip"),
    ],
)
def test_chamadas_invalidas_voltam_com_erro(ambiente, nome, argumentos, mensagem):
    resposta = ferramentas.executar(ambiente, nome, argumentos)
    assert resposta.erro is not None and mensagem in resposta.erro
    assert resposta.para_template() == {"erro": resposta.erro}


def test_respostas_sao_deterministicas(ambiente):
    args = {"ip": "203.0.113.9", "janela_s": 600}
    primeira = ferramentas.executar(ambiente, "falhas_de_login", args)
    segunda = ferramentas.executar(ambiente, "falhas_de_login", dict(reversed(list(args.items()))))
    assert primeira.hash() == segunda.hash()


def test_catalogo_e_declaracoes():
    assert set(ferramentas.CATALOGO) == {
        "falhas_de_login", "sessoes", "requisicoes_do_cliente", "bloqueios_do_cliente",
        "alertas_do_ip", "fluxos_entre",
    }
    declaracoes = ferramentas.declaracoes(("suricata",))
    nomes = {d["function"]["name"] for d in declaracoes}
    assert nomes == {"alertas_do_ip", "fluxos_entre"}
    fluxos = next(d for d in declaracoes if d["function"]["name"] == "fluxos_entre")
    assert fluxos["function"]["parameters"]["required"] == ["ip_a", "ip_b", "janela_s"]
