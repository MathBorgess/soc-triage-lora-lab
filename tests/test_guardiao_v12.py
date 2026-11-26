import bz2
import csv
import gzip
import hashlib
import io
import json
import tarfile
import zipfile

import pytest

from soc_triage.guardiao.fontes import Acervo, FonteGrande
from soc_triage.guardiao.perfis_v12 import PERFIS
from soc_triage.guardiao.v12 import (
    ExemploV12,
    IndiceDeArquivos,
    familia_do_id,
    normalizar_localizador,
    reproduzir,
)

# Linhas sintéticas: endereços de documentação (RFC 5737) e contas genéricas.
CAS_LINHAS = [
    "2024-05-17T21:09:51.744092+02:00 intranet-01 sshd[100]: Invalid user teste from 203.0.113.9 port 4000",
    ("2024-05-17T21:09:52.000000+02:00 intranet-01 sshd[100]: Failed password for invalid user teste "
    "from 203.0.113.9 port 4000 ssh2"),
    ("2024-05-17T21:09:55.500000+02:00 intranet-01 sshd[101]: Failed password for root from 203.0.113.9 "
    "port 4001 ssh2"),
    "2024-05-17T21:10:00+02:00 intranet-01 sshd[102]: Invalid user admin from 203.0.113.9 port 4002",
    ("2024-05-17T21:10:10.250000+02:00 intranet-01 sshd[103]: Failed password for root from 203.0.113.9 "
    "port 4003 ssh2"),
    ("2024-05-17T21:10:24.365823+02:00 intranet-01 sshd[104]: Accepted password for root from 203.0.113.9 "
    "port 4004 ssh2"),
]
CAS_ESPERADO = (
    "2024-05-17T21:10:24.365823+02:00 intranet-01 programa=sshd origem=203.0.113.9. Entre "
    "2024-05-17T21:09:51.744092+02:00 e a âncora, houve 5 registros de recusa ou usuário inválido em "
    "4 conexões distintas, para 3 conta(s). 3 registros indicam usuário inválido. Duração observada "
    "32.6 s. Na âncora, o sshd aceitou por password a mesma origem e uma das contas anteriormente "
    "recusadas."
)


def _sha(texto: str, com_quebra: bool = True) -> str:
    return hashlib.sha256((texto + ("\n" if com_quebra else "")).encode()).hexdigest()


@pytest.fixture
def raiz(tmp_path):
    base = tmp_path / "data/raw/casino-sintetico"
    base.mkdir(parents=True)
    with zipfile.ZipFile(base / "syslogs.zip", "w") as pacote:
        pacote.writestr("syslogs/teste/intranet-01/auth.log", "\n".join(CAS_LINHAS) + "\n")
    return tmp_path


def _exemplo_cas(entrada: str, sha_de=None) -> ExemploV12:
    mapa = {str(n): (sha_de or _sha)(linha) for n, linha in enumerate(CAS_LINHAS, 1)}
    return ExemploV12(
        id="CAS01", split="train", grupo="casino/teste", incidente="casino/teste/x",
        modalidade="linux_auth", dataset="casino", entrada=entrada, localizador="",
        lote="lote-08",
        nativo_bruto={"archive": "syslogs.zip", "member": "syslogs/teste/intranet-01/auth.log",
                      "sha256_por_linha": mapa},
    )


@pytest.mark.parametrize(
    ("identificador", "familia"),
    [
        ("L14-LNXB-0001", "L14-LNXB"),
        ("CAS36", "CAS"),
        ("AITTLS13-0ecc53280c76a1eb", "AITTLS"),
        ("OX07-34E767234829", "OX"),
        ("AIT-RM-ab3b82cb8d47", "AIT-RM"),
        ("L15-RSVA-0101", "L15-RSVA"),
    ],
)
def test_familia_do_id(identificador, familia):
    assert familia_do_id(identificador) == familia


def test_reproduz_cas_byte_a_byte(raiz):
    resultado = reproduzir([_exemplo_cas(CAS_ESPERADO)], PERFIS, Acervo(raiz), IndiceDeArquivos(raiz))[0]
    assert resultado.causa == "reproduzido"
    assert resultado.byte_a_byte
    assert resultado.linhas_conferidas == len(CAS_LINHAS)
    assert resultado.sha256_v12 == hashlib.sha256(CAS_ESPERADO.encode()).hexdigest()


def test_aceita_sha_da_linha_sem_quebra(raiz):
    exemplo = _exemplo_cas(CAS_ESPERADO, lambda linha: _sha(linha, com_quebra=False))
    resultado = reproduzir([exemplo], PERFIS, Acervo(raiz), IndiceDeArquivos(raiz))[0]
    assert resultado.causa == "reproduzido"


def test_divergencia_aponta_linha_e_coluna_sem_copiar_o_log(raiz):
    resultado = reproduzir(
        [_exemplo_cas(CAS_ESPERADO.replace("32.6", "32.7"))], PERFIS, Acervo(raiz), IndiceDeArquivos(raiz)
    )[0]
    assert resultado.causa == "perfil diverge"
    assert resultado.detalhe.startswith("linha 1, coluna ")
    assert "203.0.113.9" not in resultado.detalhe


def test_sha_errado_vira_causa(raiz):
    exemplo = _exemplo_cas(CAS_ESPERADO, lambda linha: "0" * 64)
    resultado = reproduzir([exemplo], PERFIS, Acervo(raiz), IndiceDeArquivos(raiz))[0]
    assert resultado.causa == "linha citada não confere com data/raw"


def test_familia_sem_perfil_e_sem_linha_nativa(raiz):
    sem_perfil = _exemplo_cas("x")
    sem_perfil.id = "OX07-0123456789AB"
    sem_nativo = _exemplo_cas("x")
    sem_nativo.id, sem_nativo.nativo_bruto = "LH01", "SSH.log:10"
    resultados = reproduzir([sem_perfil, sem_nativo], PERFIS, Acervo(raiz), IndiceDeArquivos(raiz))
    assert [r.causa for r in resultados] == ["perfil não portado", "sem linha nativa"]
    assert resultados[1].detalhe == "localizador textual, sem linha numerada"


@pytest.mark.parametrize(
    ("bruto", "motivo"),
    [
        (None, "lote sem localizador nativo"),
        ("arquivo.zip!membro: 1, 2", "localizador textual, sem linha numerada"),
        ({"members": [{"record": 1}]}, "registro numerado numa exportação do Splunk, sem linha de arquivo"),
        ([{"csv_record": 5}], "registro do CSV do filebeat, sem linha do auth.log"),
        ({"archive": "x.db", "events": [1]}, "evento em banco SQLite, sem linha de arquivo"),
        ([{"archive": "nao-existe.log", "line": 1}], "arquivo do localizador não encontrado em data/raw"),
    ],
)
def test_localizadores_sem_linha(raiz, bruto, motivo):
    linhas, encontrado = normalizar_localizador(bruto, IndiceDeArquivos(raiz))
    assert linhas == []
    assert encontrado.startswith(motivo)


def test_formas_de_localizador_com_linha(raiz):
    indice = IndiceDeArquivos(raiz)
    absoluto = str(raiz / "data/raw/casino-sintetico/syslogs.zip")
    formas = [
        [{"archive": "data/raw/casino-sintetico/syslogs.zip", "member": "m", "line": 3, "sha256_line": "a"}],
        {"source": {"archive": absoluto}, "points": [{"member": "m", "line": 3, "sha256": "a"}]},
        {"members": [{"local_file": "raw/casino-sintetico/syslogs.zip", "member": "m", "line": 3,
                      "sha256": "a"}]},
        {"archive": "syslogs.zip", "member": "m", "sha256_by_line": {"3": "a"}},
        {"archive": "casino-sintetico", "rows": [{"file": "data/raw/casino-sintetico/syslogs.zip",
                                                  "member": "m", "line": 3, "sha256_line": "a"}]},
    ]
    for forma in formas:
        linhas, motivo = normalizar_localizador(forma, indice)
        assert motivo is None, forma
        assert [(item.arquivo, item.membro, item.linha, item.sha256) for item in linhas] == [
            ("data/raw/casino-sintetico/syslogs.zip", "m", 3, "a")
        ]


def test_acervo_le_pacotes_em_fluxo(tmp_path):
    base = tmp_path / "data/raw/p"
    base.mkdir(parents=True)
    texto = "linha 1\nlinha 2\nlinha 3\n"
    (base / "a.log.gz").write_bytes(gzip.compress(texto.encode()))
    (base / "a.log.bz2").write_bytes(bz2.compress(texto.encode()))
    with tarfile.open(base / "a.tar.gz", "w:gz") as pacote:
        info = tarfile.TarInfo("pasta/auth.log")
        info.size = len(texto)
        pacote.addfile(info, io.BytesIO(texto.encode()))
    with zipfile.ZipFile(base / "b.zip", "w") as pacote:
        pacote.writestr("diario/D1.jsonl.bz2", bz2.compress(texto.encode()))
    acervo = Acervo(tmp_path)
    for arquivo, membro in [
        ("data/raw/p/a.log.gz", None), ("data/raw/p/a.log.bz2", None), ("data/raw/p/a.tar.gz", None),
        ("data/raw/p/a.tar.gz", "auth.log"), ("data/raw/p/b.zip", "diario/D1.jsonl.bz2"),
    ]:
        trechos = acervo.trechos(arquivo, membro, {2, 3})
        assert trechos.linhas == {2: b"linha 2", 3: b"linha 3"}, arquivo
        assert trechos.total == 3
        assert not trechos.truncado


def test_gzip_truncado_guarda_as_linhas_lidas(tmp_path):
    base = tmp_path / "data/raw/p"
    base.mkdir(parents=True)
    dados = gzip.compress(("".join(f"linha {n}\n" for n in range(1, 5000))).encode())
    (base / "t.gz").write_bytes(dados[: len(dados) // 2])
    trechos = Acervo(tmp_path).trechos("data/raw/p/t.gz", None, {1, 2})
    assert trechos.truncado
    assert trechos.linhas[1] == b"linha 1"


def test_reconstroi_log_do_csv_do_filebeat(tmp_path):
    base = tmp_path / "data/raw/msas"
    base.mkdir(parents=True)
    registros = [
        {"host": {"name": "web"}, "log": {"offset": 20, "file": {"path": "/var/log/auth.log"}},
         "message": "segunda\r"},
        {"host": {"name": "web"}, "log": {"offset": 0, "file": {"path": "/var/log/auth.log"}},
         "message": "primeira"},
        {"host": {"name": "db"}, "log": {"offset": 0, "file": {"path": "/var/log/auth.log"}},
         "message": "outro host"},
    ]
    with open(base / "export.csv", "w", encoding="utf-8", newline="") as saida:
        escritor = csv.writer(saida)
        escritor.writerow(["@timestamp", "message"])
        for registro in registros:
            escritor.writerow(["x", json.dumps(registro)])
    trechos = Acervo(tmp_path).trechos("data/raw/msas/export.csv", "web/var/log/auth.log", {1, 2})
    assert trechos.linhas == {1: b"primeira", 2: b"segunda\r"}


def test_fonte_inteira_respeita_limite(tmp_path):
    base = tmp_path / "data/raw/p"
    base.mkdir(parents=True)
    (base / "grande.log").write_text("x" * 100, encoding="utf-8")
    with pytest.raises(FonteGrande):
        Acervo(tmp_path, limite=10).fonte("data/raw/p/grande.log")


def _eve(**campos) -> str:
    return json.dumps(campos)


def test_perfil_aittls(tmp_path):
    base = tmp_path / "data/raw/ait"
    base.mkdir(parents=True)
    linhas = [
        _eve(timestamp="2022-01-15T04:04:57.083845+0000", event_type="dns", src_ip="192.0.2.4",
             dest_ip="192.0.2.53", dns={"type": "query", "rrname": "exemplo.test", "rrtype": "A"}),
        _eve(timestamp="2022-01-15T04:04:57.090000+0000", event_type="dns", src_ip="192.0.2.53",
             dest_ip="192.0.2.4", dns={"type": "answer", "rrname": "exemplo.test", "rrtype": "A",
                                       "rcode": "NOERROR", "answers": [
                                           {"rrtype": "CNAME", "rdata": "cdn.exemplo.test"},
                                           {"rrtype": "A", "rdata": "198.51.100.80"}]}),
        _eve(timestamp="2022-01-15T04:04:57.200000+0000", event_type="tls", src_ip="192.0.2.4",
             dest_ip="198.51.100.80", dest_port=443, tls={"sni": "exemplo.test", "version": "TLS 1.3"}),
        _eve(timestamp="2022-01-15T04:05:30.000000+0000", event_type="flow", src_ip="192.0.2.4",
             dest_ip="198.51.100.80", dest_port=443, proto="TCP", app_proto="tls",
             flow={"state": "closed", "pkts_toserver": 12, "pkts_toclient": 15}),
    ]
    (base / "eve.json").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    esperado = "Suricata EVE | src_ip=192.0.2.4 | dest_ip=198.51.100.80\n2022-01-15T04:04:57.083845Z | dns consulta nome_1 tipo=A\n2022-01-15T04:04:57.090000Z | dns resposta nome_1 NOERROR com endereço=198.51.100.80 e CNAME=1\n2022-01-15T04:04:57.200000Z | tls nome_1 | versão=TLS 1.3\n2022-01-15T04:05:30.000000Z | flow app=tls | estado=closed | pacotes cliente→servidor=12 servidor→cliente=15"
    exemplo = ExemploV12(
        id="AITTLS13-0123456789abcdef", split="train", grupo="ait/fox", incidente="ait/fox/x",
        modalidade="suricata", dataset="ait", entrada=esperado, localizador="", lote="lote-14",
        nativo_bruto={"source": {"archive": "data/raw/ait/eve.json"},
                      "points": [{"member": "", "line": n, "sha256": _sha(linha, False)}
                                 for n, linha in enumerate(linhas, 1)]},
    )
    resultado = reproduzir([exemplo], PERFIS, Acervo(tmp_path), IndiceDeArquivos(tmp_path))[0]
    assert resultado.causa == "reproduzido", resultado.detalhe


def test_perfil_l15_validacao_com_janela_e_sessao(tmp_path):
    base = tmp_path / "data/raw/cse"
    base.mkdir(parents=True)
    linhas = [
        "Feb 14 08:30:03 ip-172-31-69-22 systemd[1]: Started Session 1 of user ubuntu.",
        "Feb 14 08:40:00 ip-172-31-69-22 CRON[10]: (root) CMD (run-parts /etc/cron.hourly)",
        "Feb 14 08:47:50 ip-172-31-69-22 dhclient[20]: DHCPREQUEST of 192.0.2.5 on eth0",
        "Feb 14 08:47:57 ip-172-31-69-22 systemd-tmpfiles[30]: Duplicate line, ignoring (error).",
        "Feb 14 08:47:57 ip-172-31-69-22 systemd[1]: Started Cleanup of Temporary Directories.",
    ]
    with zipfile.ZipFile(base / "logs.zip", "w") as pacote:
        pacote.writestr("logs/U172.31.69.22", "\n".join(linhas) + "\n")
    esperado = "\n".join([
        "syslog do host ip-172-31-69-22 (Ubuntu). Syslog sem ano e sem fuso.",
        ("Na janela de 7 min 57 s até a âncora (08:40:00 a 08:47:57): 4 linhas (1 CRON, 1 dhclient, "
        "1 systemd-tmpfiles, 1 systemd); linhas de sshd, sudo, su ou login: 0; linhas com failed, "
        "denied, invalid, error ou refused: 1."),
        "A última sessão de ubuntu começou às 08:30:03, 17 min 54 s antes.",
        linhas[3],
        linhas[4],
    ])
    exemplo = ExemploV12(
        id="L15-RSVA-0006", split="valid", grupo="cse-cic-ids2018/2018-02-14",
        incidente="cse-cic-ids2018/2018-02-14/U172.31.69.22/tmpfiles-22", modalidade="linux_auth",
        dataset="cse", entrada=esperado, localizador="", lote="lote-15",
        nativo_bruto=[{"archive": "data/raw/cse/logs.zip", "member": "logs/U172.31.69.22", "line": n,
                       "sha256_line": _sha(linhas[n - 1], False)} for n in (4, 5)],
        meta={"janela_agregada": {"linhas": "2-5"}},
    )
    resultado = reproduzir([exemplo], PERFIS, Acervo(tmp_path), IndiceDeArquivos(tmp_path))[0]
    assert resultado.causa == "reproduzido", resultado.detalhe
    teste = ExemploV12(**{**exemplo.__dict__, "id": "L15-RSVA-0101", "grupo": "echolake/captura"})
    resultado_teste = reproduzir([teste], PERFIS, Acervo(tmp_path), IndiceDeArquivos(tmp_path))[0]
    assert resultado_teste.causa == "perfil não portado"
