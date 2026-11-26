import hashlib

import pytest

from soc_triage.guardiao.fontes import Acervo
from soc_triage.guardiao.reprojecao import reprojetar
from soc_triage.guardiao.v12 import ExemploV12, IndiceDeArquivos

# Log sintético: endereços de documentação (RFC 5737) e contas genéricas.
LINHAS = [
    "Mar  1 08:00:00 srv sshd[90]: Failed password for root from 203.0.113.9 port 3999 ssh2",
    "Mar  1 10:00:00 srv sshd[100]: Invalid user teste from 203.0.113.9 port 4000",
    "Mar  1 10:00:01 srv sshd[100]: Failed password for invalid user teste from 203.0.113.9 port 4000 ssh2",
    "Mar  1 10:00:05 srv sshd[101]: Failed password for root from 203.0.113.9 port 4001 ssh2",
    "Mar  1 10:00:09 srv sshd[102]: Failed password for root from 203.0.113.9 port 4002 ssh2",
    "Mar  1 10:00:12 srv sshd[103]: Failed password for root from 203.0.113.9 port 4003 ssh2",
    "Mar  1 10:00:20 srv sshd[104]: Accepted password for root from 203.0.113.9 port 4004 ssh2",
    "Mar  1 10:00:30 srv sshd[105]: Failed password for root from 203.0.113.9 port 4005 ssh2",
]


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


@pytest.fixture
def raiz(tmp_path):
    base = tmp_path / "data/raw/sintetico"
    base.mkdir(parents=True)
    (base / "auth.log").write_text("\n".join(LINHAS) + "\n", encoding="utf-8")
    return tmp_path


def _exemplo(identificador, linhas, *, usuario="root", justificativa="Rajada de 5 falhas.", entrada=""):
    return ExemploV12(
        id=identificador, split="train", grupo="sintetico/grupo", incidente=f"sintetico/grupo/{identificador}",
        modalidade="linux_auth", dataset="sintetico", entrada=entrada or "resumo da curadoria",
        localizador="", lote="lote-14", veredito="malicious", severidade="high",
        nativo_bruto=[
            {"archive": "data/raw/sintetico/auth.log", "member": "auth.log", "line": n,
             "sha256_line": _sha(LINHAS[n - 1])}
            for n in linhas
        ],
        alvo={
            "normalized_event": {"timestamp": None, "src_ip": "203.0.113.9", "dst_ip": None,
                                 "user": usuario, "process_or_action": "sshd", "iocs": ["203.0.113.9"]},
            "triage": {"verdict": "malicious", "severity": "high", "mitre_technique": "T1110.001",
                       "rationale": justificativa},
        },
    )


def _reprojetar(raiz, exemplos):
    return {r.exemplo.id: r for r in reprojetar(exemplos, Acervo(raiz), IndiceDeArquivos(raiz))}


def test_ancora_e_a_linha_citada_mais_recente_e_nada_muda(raiz):
    r = _reprojetar(raiz, [_exemplo("A", [7, 2, 3])])["A"]
    assert r.ancora.linha == 7
    assert r.estado == "sem_mudanca_detectada"
    assert r.motivos == {}
    assert [linha.texto for linha in r.recorte.registro] == LINHAS[1:7]
    assert [s.regra for s in r.recorte.sinais] == ["linux_auth.rajada_de_falhas_ssh"]
    assert "Mar 1 10:00:00 a Mar 1 10:00:20" in r.recorte.texto_v2()


def test_linha_citada_fora_da_janela_mas_ao_alcance_da_ferramenta(raiz):
    r = _reprojetar(raiz, [_exemplo("B", [1, 7])])["B"]
    assert r.estado == "fila_de_revisao"
    assert r.motivos == {"linha_citada_fora_do_registro": "1 de 2 linhas citadas"}


def test_alvo_justificativa_e_contexto_da_curadoria(raiz):
    exemplo = _exemplo(
        "C", [2, 7], usuario="administrador", justificativa="Foram 151 falhas antes do aceite.",
        entrada="A tarefa consta da agenda para os minutos :09 e :39.\n" + LINHAS[6],
    )
    r = _reprojetar(raiz, [exemplo])["C"]
    assert r.motivos == {
        "alvo_nao_literal": "user",
        "numero_da_justificativa_ausente": "1 números",
        "contexto_da_curadoria": "agenda_e_rotina",
    }


def test_sem_linha_nativa_fica_fora_do_contrato(raiz):
    exemplo = _exemplo("D", [2])
    exemplo.nativo_bruto = "SSH.log: 1, 2"
    r = _reprojetar(raiz, [exemplo])["D"]
    assert r.estado == "fora_do_contrato"
    assert r.fora == "sem linha nativa: localizador textual, sem linha numerada"
    assert r.recorte is None


def test_reprojecao_nao_muda_o_rotulo(raiz):
    exemplo = _exemplo("E", [1, 7])
    antes = (exemplo.veredito, exemplo.severidade, repr(exemplo.alvo))
    _reprojetar(raiz, [exemplo])
    assert (exemplo.veredito, exemplo.severidade, repr(exemplo.alvo)) == antes
