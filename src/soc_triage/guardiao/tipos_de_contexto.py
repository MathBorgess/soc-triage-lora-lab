"""Tipos de linha de Contexto na entrada da v12 (insumo do ADR 0009).

A v12 não separa Contexto de Registro. Este módulo aplica regras heurísticas e versionadas:

1. Cada linha da entrada é um segmento. Uma linha de evento (começa com carimbo, JSON ou campos
   de um evento e não traz palavras de resumo) é Registro e fica de fora.
2. Os demais segmentos são Contexto. Cada regra de tipo procura o vocabulário que a curadoria usou
   para aquele tipo de informação. Um segmento pode ter mais de um tipo.
3. Um Recorte "tem" um tipo quando algum segmento dele casa com a regra.

Os tipos que correspondem a uma Ferramenta de leitura levam o nome dela. Os demais são Contexto que
o Projetor ou a curadoria escrevem. O ADR 0009 só aceita como ferramenta os tipos presentes em pelo
menos 20 Recortes. A classificação é aproximada: o relatório mostra exemplos e o que ficou sem tipo
para a revisão do responsável.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

VERSAO_REGRAS = "tipos-de-contexto-0.1"
MINIMO_DE_RECORTES = 20

INICIO_DE_EVENTO = re.compile(
    r"^(?:\d{4}-\d\d-\d\d[T ]\d\d:\d\d|[A-Z][a-z]{2} +\d{1,2} \d\d:\d\d:\d\d|\d\d:\d\d:\d\d\b"
    r"|\d\d/[A-Z][a-z]{2}[ /]|\{|\[|Timestamp=|TimeCreated=|UtcTime=|Δt=|-?\d+ (?:@|imagem=)"
    r"|evento=|\w+=\S|(?:\d{1,3}\.){3}\d{1,3}\b|antes: )"
)
PALAVRAS_DE_RESUMO = re.compile(
    r"\b(?:Entre|janela|houve|registra|somou|reporta|Resumo|anterior|anteriores|Antes|Nos|Na|"
    r"Até a âncora|Desde|agendador|Agendamento|Intervalo)\b"
)
# Cabeçalhos que repetem texto do log comum às linhas (user-agent, host do Windows, Host HTTP).
# São Registro, não Contexto.
REGISTRO_COMPARTILHADO = re.compile(
    r"^(?:User-agent das linhas exibidas|Sem user-agent nas linhas|ua\d+=|"
    r"Microsoft-Windows-[\w-]+/Operational \| Computer=|Campos comuns:)"
)


@dataclass(frozen=True)
class TipoDeContexto:
    nome: str
    ferramenta: str | None
    descricao: str
    regra: re.Pattern[str]


def _r(padrao: str) -> re.Pattern[str]:
    return re.compile(padrao, re.IGNORECASE)


TIPOS: tuple[TipoDeContexto, ...] = (
    TipoDeContexto(
        "falhas_de_login",
        "falhas_de_login",
        "contagem de falhas, recusas ou usuários inválidos de uma origem ou conta",
        _r(r"\bfalhas?\b|\brecusas?\b|rejeiç|recusou|usu[aá]rios? (?:inv[aá]lid|ilegal)|"
           r"tentativas? com usu|erros? de limite|excesso de tentativas|Auth fail|POSSIBLE BREAK-IN"),
    ),
    TipoDeContexto(
        "sessoes",
        "sessoes",
        "aceites de login e sessões de uma conta, inclusive anteriores",
        _r(r"\baceites?\b|aceitou|\bsess(?:ão|ões)\b|PAM (?:abriu|encerrou|registra abertura)|"
           r"abertura PAM|logins? por chave"),
    ),
    TipoDeContexto(
        "sudo",
        None,
        "comandos sudo e trocas de conta com su (fora do catálogo pela emenda do ADR 0009)",
        _r(r"comandos? sudo|\btrocas? su\b|\bsu de\b|Programa=sudo|ações? sudo|via sudo|"
           r"sudo (?:como|para|de)|elevação"),
    ),
    TipoDeContexto(
        "requisicoes_do_cliente",
        "requisicoes_do_cliente",
        "requisições HTTP do mesmo cliente: contagem, status, rotas e user-agents",
        _r(r"\d+ (?:requisiç|solicitaç|GETs?\b|transações distintas)|recursos?_distintos|"
           r"Respostas HTTP do mesmo cliente|Rotas distintas|nenhuma requisição|"
           r"caminhos(?: \.php)? distintos|respostas_por_recurso|status \d{3}×|rotas? com erro|"
           r"user-agents \d+|referers distintos"),
    ),
    TipoDeContexto(
        "bloqueios_do_cliente",
        "bloqueios_do_cliente",
        "respostas de bloqueio ou recusa HTTP (403, WAF, ModSecurity) ao cliente",
        _r(r"\b403\b|bloque|anomaly score|\bregras? (?:\d{6}|na mesma)|negad[oa]s? pelo|"
           r"recusa 403"),
    ),
    TipoDeContexto(
        "alertas_do_ip",
        "alertas_do_ip",
        "alertas do Suricata de um endereço: contagem e assinaturas",
        _r(r"\d+ alertas?\b|\balertas? (?:de|para|do|da|em)\b|assinaturas?:|S\d+=\"|"
           r"alerta de segurança|Regras \d{7}|com alerta|sem alertas"),
    ),
    TipoDeContexto(
        "fluxos_entre",
        "fluxos_entre",
        "fluxos e transações entre dois endereços: portas, pacotes, protocolos",
        _r(r"\d+ (?:fluxos?|pacotes|portas|transações? (?:HTTP|DNS)?|consultas)|"
           r"pacotes cliente|portas de destino|combinações de endereços|início dos fluxos|"
           r"no mesmo par|servidores (?:externos )?distintos"),
    ),
    TipoDeContexto(
        "arvore_de_processos",
        "arvore_de_processos",
        "processo pai, filhos e ligação por GUID (sysmon)",
        _r(r"processo pai|\bpai\b|pai=|filiação|\bfilhos? d|ligados por GUID|árvore de processos|"
           r"cadeia de processos"),
    ),
    TipoDeContexto(
        "conexoes_do_processo",
        "conexoes_do_processo",
        "conexões de rede de um processo (sysmon)",
        _r(r"conex(?:ão|ões) de rede|conectou|DestinationIp|destino de rede"),
    ),
    TipoDeContexto(
        "eventos_do_host",
        "eventos_do_host",
        "contagem genérica de eventos ou linhas do host na janela",
        _r(r"\d+ linhas \(|\d+ registros;|Tipos alert=|\d+ eventos (?:no|do) host|EventID \d+ ×"),
    ),
    TipoDeContexto(
        "agenda_e_rotina",
        None,
        "agenda do cron, rotina programada e periodicidade",
        _r(r"agenda|agendamento|agendador|crontab|rotinas? (?:programad|horári|diári)|"
           r"tarefas? (?:horári|diári)|minuto \d+|minutos :\d\d|Intervalo entre invocações|"
           r"Configuração registra rotinas"),
    ),
    TipoDeContexto(
        "linha_de_base",
        None,
        "histórico e comportamento normal: primeira vez, mesmo ritmo, dias anteriores",
        _r(r"pela primeira vez|primeira vez|origem nova|mesmo ritmo|habitual|dias anteriores|"
           r"nenhum evento desta origem|horas? anteriores|histórico"),
    ),
    TipoDeContexto(
        "mudanca_aprovada",
        None,
        "operação administrativa conhecida, playbook ou manutenção",
        _r(r"playbook|Ansible|operação administrativa|AURA|manutenção|aprovad|autorizad"),
    ),
    TipoDeContexto(
        "fonte_e_relogio",
        None,
        "descrição da fonte, do host e do relógio (cabeçalho do Projetor)",
        _r(r"sem ano|sem fuso|fuso|relógio|Carimbos?|Horário (?:local|do registro)|"
           r"^(?:Apache access|Suricata (?:EVE|fast\.log)|Projeção de|auth\.log do host|"
           r"syslog do host|secure do host|OpenSSH auth\.log|Telemetria de|Log de autenticação)"),
    ),
    TipoDeContexto(
        "legenda_e_pseudonimos",
        None,
        "legenda de colunas e aviso de pseudônimos ou campos omitidos",
        _r(r"^Linhas: |pseudônimos|Legenda:|omitid|^Âncora observada|^Faça a triagem|"
           r"^Janela retrospectiva"),
    ),
)

TIPOS_POR_NOME = {tipo.nome: tipo for tipo in TIPOS}


def eh_linha_de_evento(linha: str) -> bool:
    return bool(INICIO_DE_EVENTO.match(linha)) and not PALAVRAS_DE_RESUMO.search(linha)


def segmentos_de_contexto(entrada: str) -> list[str]:
    """Linhas da entrada que não são linha de evento nem cabeçalho copiado do log."""
    return [
        linha
        for linha in entrada.split("\n")
        if linha.strip() and not eh_linha_de_evento(linha) and not REGISTRO_COMPARTILHADO.match(linha)
    ]


def tipos_do_segmento(segmento: str) -> set[str]:
    return {tipo.nome for tipo in TIPOS if tipo.regra.search(segmento)}


def tipos_do_recorte(entrada: str) -> tuple[set[str], list[str]]:
    """Tipos presentes num Recorte e os segmentos de Contexto que não casaram com nenhum tipo."""
    tipos: set[str] = set()
    sem_tipo = []
    for segmento in segmentos_de_contexto(entrada):
        achados = tipos_do_segmento(segmento)
        tipos |= achados
        if not achados:
            sem_tipo.append(segmento)
    return tipos, sem_tipo
