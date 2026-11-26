# Tipos de linha de Contexto na v12

> Gerado por `scripts/10_tipos_de_contexto.py` em 26/11/2026, com as regras `tipos-de-contexto-0.1` de `soc_triage.guardiao.tipos_de_contexto`. Python 3.12.1. A entrada é `data/processed/soc-triage-v12/splits/revisao.csv` (1490 Recortes), fora do Git.

## Pergunta

O ADR 0009 define o catálogo final de Ferramentas de leitura como os tipos de linha de Contexto que aparecem em pelo menos 20 Recortes da v12. Cada linha de Contexto desses tipos vira uma chamada numa Trajetória derivada. Este relatório conta os tipos.

## Como contei

A v12 não separa Contexto de Registro. Uma linha da entrada conta como Contexto quando não é linha de evento (carimbo, JSON ou campos de um evento, sem palavras de resumo) nem cabeçalho que copia texto do log (user-agent, host do Windows). Cada tipo tem uma regra de vocabulário. Um Recorte tem o tipo quando alguma linha de Contexto dele casa com a regra. As regras são heurísticas: servem para decidir o catálogo, não para gerar Trajetórias.

## Tipos que viram ferramenta

| Tipo | Modalidade na arquitetura | Implementada | Recortes | No treino | Por Modalidade | Regra dos 20 | Exemplos |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| `falhas_de_login` | linux_auth | sim | 113 | 89 | linux_auth 112, apache 1 | entra | `LH01`, `LH02`, `LH05` |
| `sessoes` | linux_auth | sim | 122 | 85 | linux_auth 116, suricata 6 | entra | `AIT-RM-ab3b82cb8d47`, `AIT-RM-cca75eb3bb61`, `AIT-RM-87fab52d99d5` |
| `sudo` | linux_auth | sim | 11 | 9 | linux_auth 11 | sai (abaixo de 20) | `AIT-RM-32136a71a3d3`, `L14-LNXB-0015`, `L14-LNXB-0020` |
| `arvore_de_processos` | sysmon | não | 9 | 4 | sysmon 9 | sai (abaixo de 20) | `WAPT11`, `WAPT12`, `WAPT13` |
| `conexoes_do_processo` | sysmon | não | 0 | 0 | — | sai (abaixo de 20) | — |
| `eventos_do_host` | sysmon | não | 38 | 10 | linux_auth 14, suricata 24 | entra | `L15-TSS-0012`, `L15-TSS-0013`, `L15-TSS-0014` |
| `requisicoes_do_cliente` | apache e waf | sim | 130 | 62 | apache 108, suricata 10, waf 12 | entra | `AIT-RM-c92d57f27c9a`, `OX07-07BF16AF91DE`, `OX07-408528676C9D` |
| `bloqueios_do_cliente` | apache e waf | sim | 78 | 61 | apache 16, suricata 8, waf 54 | entra | `CRS09-00001`, `CRS09-00156`, `CRS09-00606` |
| `alertas_do_ip` | suricata | sim | 111 | 73 | suricata 97, waf 14 | entra | `EVE10-cecdbb53a710b6cfc5`, `EVE10-4ce078e92e3ffc6797`, `L14-SUR-0039` |
| `fluxos_entre` | suricata | sim | 57 | 29 | suricata 50, waf 7 | entra | `BOTSEVE-e9eeeba8e4b8a3`, `BOTSEVE-48ff428a68acd1`, `BOTSEVE-61bb66067dda7f` |

"Implementada" diz se a ferramenta já está em `soc_triage.guardiao.ferramentas`. Esta rodada implementou as sete de linux_auth, apache e suricata.

## Tipos que o Projetor ou a curadoria escrevem

Estes tipos não viram ferramenta: o ADR 0009 diz que o Projetor continua escrevendo no Contexto o que não está nos logs.

| Tipo | O que é | Recortes | Por Modalidade |
| --- | --- | ---: | --- |
| `agenda_e_rotina` | agenda do cron, rotina programada e periodicidade | 16 | linux_auth 16 |
| `linha_de_base` | histórico e comportamento normal: primeira vez, mesmo ritmo, dias anteriores | 11 | linux_auth 11 |
| `mudanca_aprovada` | operação administrativa conhecida, playbook ou manutenção | 3 | linux_auth 3 |
| `fonte_e_relogio` | descrição da fonte, do host e do relógio (cabeçalho do Projetor) | 751 | linux_auth 98, apache 182, suricata 182, sysmon 57, waf 232 |
| `legenda_e_pseudonimos` | legenda de colunas e aviso de pseudônimos ou campos omitidos | 189 | linux_auth 45, apache 96, suricata 19, sysmon 28, waf 1 |

## Cobertura

| Modalidade | Recortes | Sem nenhuma linha de Contexto | Linhas de Contexto sem tipo |
| --- | ---: | ---: | ---: |
| linux_auth | 272 | 29 | 4 |
| apache | 205 | 4 | 19 |
| suricata | 197 | 9 | 13 |
| sysmon | 519 | 439 | 13 |
| waf | 297 | 0 | 45 |

## Leitura

- Pela regra do ADR 0009, ficam abaixo de 20 Recortes: `arvore_de_processos` (9), `conexoes_do_processo` (0), `sudo` (11).
- `sudo` foi pedida nesta rodada e está implementada, mas aparece em 11 Recortes. A maior parte do sudo da v12 está em linhas de evento (Registro), não em linhas de Contexto. Manter ou tirar a ferramenta é decisão do responsável.
- Em sysmon, `arvore_de_processos` tem 9 Recortes, `conexoes_do_processo` tem 0 e `eventos_do_host` tem 0. `eventos_do_host` passa da regra (38) só pela contagem genérica de linhas e registros em linux_auth e suricata, a "contagem genérica" da arquitetura. O sysmon da v12 quase não tem linhas de resumo: 439 dos 519 Recortes de sysmon só têm linhas de evento, e o processo pai está dentro da linha do evento (`ParentImage=`), que é Registro.
- `fonte_e_relogio` e `legenda_e_pseudonimos` são cabeçalhos do Projetor, não informação que a ferramenta busca.
- A contagem é heurística. Antes de gerar Trajetórias derivadas, cada linha de Contexto precisa de um tipo atribuído pelo perfil do Projetor que a escreveu, como prevê o ADR 0009.
