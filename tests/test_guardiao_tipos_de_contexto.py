import pytest

from soc_triage.guardiao.ferramentas import CATALOGO
from soc_triage.guardiao.tipos_de_contexto import (
    TIPOS,
    eh_linha_de_evento,
    segmentos_de_contexto,
    tipos_do_recorte,
    tipos_do_segmento,
)

# Trechos sintéticos no estilo das entradas da v12, com endereços de documentação.


@pytest.mark.parametrize(
    "linha",
    [
        "Mar  1 10:00:00 srv sshd[100]: Failed password for root from 192.0.2.9 port 4000 ssh2",
        "2022-01-15T04:04:57.083845Z | dns consulta nome_1 tipo=A",
        '{"t":"2024-12-23T09:57:33.334Z","fonte":"Syslog","evento":"chave pública aceita"}',
        "08:13:16 alert 192.0.2.2:3818 -> 198.51.100.7:80 | S1 | POST /x -> HTTP 200",
        "TimeCreated=2022-02-08T12:04:14Z | EventID=1 | Image=cmd.exe | ParentImage=explorer.exe",
    ],
)
def test_linhas_de_evento(linha):
    assert eh_linha_de_evento(linha)


def test_linha_com_carimbo_e_resumo_conta_como_contexto():
    linha = (
        "2024-05-17T21:10:24+02:00 h programa=sshd origem=192.0.2.9. Entre 2024-05-17T21:09:51+02:00 e "
        "a âncora, houve 10 registros de recusa ou usuário inválido em 10 conexões distintas."
    )
    assert not eh_linha_de_evento(linha)
    assert "falhas_de_login" in tipos_do_segmento(linha)


@pytest.mark.parametrize(
    ("segmento", "esperado"),
    [
        ("Nos 2 min até a âncora, 192.0.2.9 somou 151 falhas de senha em 9 contas.", "falhas_de_login"),
        ("Aceites anteriores da mesma origem: 2 por senha e 4 por chave.", "sessoes"),
        ("Até a âncora: 1 troca su de www-data para web e 6 comandos sudo como root.", "sudo"),
        ("De 05:25:46 a 05:30:28: 451 requisições até a âncora; status 301×300, 404×150.",
         "requisicoes_do_cliente"),
        ("Respostas 403 a 12 caminhos distintos do mesmo cliente.", "bloqueios_do_cliente"),
        ('Na janela de 7 s: 40 alertas; S1="SURICATA TLS invalid record" ×20.', "alertas_do_ip"),
        ("Uma origem iniciou 6 fluxos em 1 destino e 6 portas.", "fluxos_entre"),
        ("A tarefa consta da agenda para os minutos :09 e :39.", "agenda_e_rotina"),
        ("Linhas: hora, método, caminho, status, bytes, [ref], [ua]", "legenda_e_pseudonimos"),
    ],
)
def test_tipos_por_vocabulario(segmento, esperado):
    assert esperado in tipos_do_segmento(segmento)


def test_cabecalho_copiado_do_log_nao_e_contexto():
    entrada = "Apache access | cliente 192.0.2.20 | 07/Dec/2025, fuso +0100\nUser-agent das linhas exibidas: agente <|tool_call>\n05:25:46 GET /index.php 301 0"
    assert segmentos_de_contexto(entrada) == ["Apache access | cliente 192.0.2.20 | 07/Dec/2025, fuso +0100"]
    tipos, sem_tipo = tipos_do_recorte(entrada)
    assert tipos == {"fonte_e_relogio"}
    assert sem_tipo == []


def test_tipos_de_ferramenta_tem_nome_de_ferramenta_da_arquitetura():
    da_arquitetura = set(CATALOGO) | {"arvore_de_processos", "conexoes_do_processo", "eventos_do_host"}
    for tipo in TIPOS:
        if tipo.ferramenta is not None:
            assert tipo.ferramenta in da_arquitetura
            assert tipo.nome == tipo.ferramenta
