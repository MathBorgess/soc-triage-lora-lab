# Reprojeção da v12 no formato canônico (contrato v2)

> Gerado por `scripts/11_reprojetar_v12.py` em 26/11/2026, na revisão `ec06e10`, com `reprojecao-v2-01`, `projetor-0.1`, `recorte-v2.0` e `sinais-0.1`. Python 3.12.1. A execução levou 690 s. A saída está em `data/processed/guardiao-v2-r01/`, fora do Git.

## O que foi feito

O ADR 0012 decidiu que o contrato v2 usa o formato canônico do Projetor. Esta rodada reprojetou os Recortes de linux_auth, apache e suricata da v12 a partir dos logs de origem:

- **Âncora:** a linha citada mais recente pelo localizador nativo do lote (horário, depois número da linha).
- **Janela:** a do Projetor de produção, mesma origem e até 900 s antes da Âncora em linux_auth e 300 s em apache e suricata. O Registro guarda até 12 linhas; acima disso o Recorte declara a janela cortada.
- **Rótulo:** o da v12, sem mudança. Nenhum Recorte foi aprovado.

## Contagens

| Estado | Recortes | Parcela |
| --- | ---: | ---: |
| Reprojetados sem mudança detectada | 73 | 10,8% |
| Reprojetados na fila de revisão | 348 | 51,6% |
| Fora do contrato v2 (sem linha nativa legível) | 253 | 37,5% |
| **Total** | 674 | 100% |

### Por split e Modalidade

| Split | Modalidade | Recortes | Sem mudança | Na fila | Fora | Fração fora |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| train | linux_auth | 206 | 19 | 107 | 80 | 38,8% |
| train | apache | 142 | 15 | 49 | 78 | 54,9% |
| train | suricata | 149 | 14 | 90 | 45 | 30,2% |
| valid | linux_auth | 42 | 6 | 10 | 26 | 61,9% |
| valid | apache | 24 | 4 | 12 | 8 | 33,3% |
| valid | suricata | 24 | 4 | 19 | 1 | 4,2% |
| test | linux_auth | 24 | 5 | 13 | 6 | 25,0% |
| test | apache | 39 | 1 | 31 | 7 | 17,9% |
| test | suricata | 24 | 5 | 17 | 2 | 8,3% |

### Por Veredito de referência

| Veredito | Recortes | Sem mudança | Na fila | Fora | Fração fora |
| --- | ---: | ---: | ---: | ---: | ---: |
| malicious | 215 | 21 | 140 | 54 | 25,1% |
| suspicious | 109 | 11 | 68 | 30 | 27,5% |
| benign | 241 | 27 | 101 | 113 | 46,9% |
| expected_admin | 109 | 14 | 39 | 56 | 51,4% |

**Fração fora do contrato v2:** 253 de 674 (37,5%), dos quais 54 são malicious. Eles ficam fora até ganharem localizador ou serem declarados como perda pelo responsável.

### Por que ficam fora

| Motivo | Recortes |
| --- | ---: |
| sem linha nativa: lote sem localizador nativo | 91 |
| sem linha nativa: localizador textual, sem linha numerada | 86 |
| sem linha nativa: registro numerado numa exportação do Splunk, sem linha de arquivo | 23 |
| sem linha nativa: offset em journal.gz do Splunk, sem linha de arquivo | 19 |
| sem linha nativa: item de localizador sem linha | 6 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw (organization-x/log/apache2/web-access.log.14.gz) | 6 |
| sem linha nativa: registro do CSV do filebeat, sem linha do auth.log | 5 |
| nenhuma linha citada tem horário legível | 4 |
| sem linha nativa: evento em banco SQLite, sem linha de arquivo | 3 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw (release/first-org-conf-2015/eve.json) | 2 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw (ait-lds-v2.1) | 2 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw (attackmate-eval-v4) | 1 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw (cam-lds-v2) | 1 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw () | 1 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw (organization-x/log/apache2/web-access.log.11.gz) | 1 |
| sem linha nativa: arquivo do localizador não encontrado em data/raw (organization-x/log/apache2/web-access.log.7.gz) | 1 |
| sem linha nativa: artefato em parquet, sem linha de arquivo | 1 |

A lista por Recorte está em `fora-do-contrato.csv`, com a família e o lote de cada um.

## Fila de revisão

**Tamanho:** 348 Recortes (82,7% dos 421 reprojetados). Um Recorte pode ter mais de um motivo.

| Motivo | Recortes | O que significa |
| --- | ---: | --- |
| `linha_citada_fora_do_registro` | 258 | linha citada pela curadoria saiu do Registro, mas uma Ferramenta de leitura ainda a alcança (mesma Fonte do grupo, até a Âncora e no máximo 24 h antes) |
| `linha_citada_fora_do_alcance` | 48 | linha citada pela curadoria saiu do Registro e nenhuma Ferramenta de leitura a alcança |
| `alvo_nao_literal` | 94 | campo do alvo da v12 que não aparece literalmente no Recorte reprojetado |
| `numero_da_justificativa_ausente` | 145 | número citado na justificativa da v12 que não aparece no Recorte reprojetado |
| `contexto_da_curadoria` | 12 | a v12 trazia Contexto que não está nos logs (agenda, linha de base ou mudança aprovada); ele precisa ser transcrito como Contexto da curadoria |

### Combinações mais comuns

| Motivos | Recortes |
| --- | ---: |
| `linha_citada_fora_do_registro + numero_da_justificativa_ausente` | 108 |
| `linha_citada_fora_do_registro` | 96 |
| `alvo_nao_literal + linha_citada_fora_do_registro` | 40 |
| `alvo_nao_literal` | 21 |
| `linha_citada_fora_do_alcance` | 19 |
| `alvo_nao_literal + linha_citada_fora_do_alcance` | 15 |
| `alvo_nao_literal + linha_citada_fora_do_registro + numero_da_justificativa_ausente` | 14 |
| `numero_da_justificativa_ausente` | 11 |

### Fila por família de lote

| Família | Reprojetados | Na fila | Motivo mais comum |
| --- | ---: | ---: | --- |
| `L14-APA` | 45 | 43 | `linha_citada_fora_do_registro` |
| `L14-SUR` | 43 | 33 | `linha_citada_fora_do_alcance` |
| `L14-LNXA` | 40 | 33 | `linha_citada_fora_do_registro` |
| `L14-LNXB` | 33 | 22 | `linha_citada_fora_do_registro` |
| `L15-RSVA` | 29 | 18 | `linha_citada_fora_do_registro` |
| `L15-RSVY` | 28 | 28 | `linha_citada_fora_do_registro` |
| `L15-TSS` | 27 | 22 | `linha_citada_fora_do_registro` |
| `L16-SUR` | 25 | 17 | `linha_citada_fora_do_registro` |
| `CAS` | 21 | 21 | `linha_citada_fora_do_registro` |
| `AIT1W` | 16 | 7 | `linha_citada_fora_do_registro` |
| `L16-APA` | 15 | 10 | `linha_citada_fora_do_registro` |
| `AITTLS` | 13 | 13 | `linha_citada_fora_do_registro` |
| `BOTSEVE` | 11 | 11 | `alvo_nao_literal` |
| `AITDNS` | 9 | 9 | `alvo_nao_literal` |
| `AITADS` | 8 | 8 | `alvo_nao_literal` |
| `AC` | 7 | 7 | `linha_citada_fora_do_alcance` |
| `CAM` | 5 | 5 | `alvo_nao_literal` |
| `SMLD` | 5 | 5 | `alvo_nao_literal` |
| `BOTSDNS` | 4 | 4 | `alvo_nao_literal` |
| `L11-LA` | 4 | 4 | `alvo_nao_literal` |
| `ASC` | 3 | 3 | `alvo_nao_literal` |
| `L11-HY` | 3 | 3 | `alvo_nao_literal` |
| `L12-LNX` | 3 | 3 | `alvo_nao_literal` |
| `MAWAP` | 3 | 2 | `linha_citada_fora_do_registro` |
| `RMX` | 3 | 1 | `linha_citada_fora_do_alcance` |
| `AITW` | 2 | 2 | `linha_citada_fora_do_registro` |
| `L09-MAWA` | 2 | 2 | `linha_citada_fora_do_registro` |
| `L10-SL700` | 2 | 2 | `alvo_nao_literal` |
| `L13-AIT-AUTH` | 2 | 2 | `linha_citada_fora_do_registro` |
| `LH` | 2 | 2 | `linha_citada_fora_do_registro` |
| `RTA` | 2 | 0 | — |
| `AC05-LH` | 1 | 1 | `linha_citada_fora_do_registro` |
| `AC05-RM` | 1 | 1 | `linha_citada_fora_do_alcance` |
| `AITAUTH` | 1 | 1 | `alvo_nao_literal` |
| `L10-SL300` | 1 | 1 | `linha_citada_fora_do_registro` |
| `L13-DED-AUTH` | 1 | 1 | `linha_citada_fora_do_alcance` |
| `VNL10-DNS-REFUSED` | 1 | 1 | `alvo_nao_literal` |

220 dos 421 Recortes reprojetados declaram a janela cortada.

## Taxa de cada Sinal

Parcela dos Recortes reprojetados com cada Sinal do `sinais-0.1`, por Modalidade e Veredito de referência. Um Sinal num Recorte benign ou expected_admin é o caso em que o Rebaixamento só vale com Evidência no Contexto (ADR 0003).

| Modalidade | Veredito | Recortes | Por regra | Com algum Sinal |
| --- | --- | ---: | --- | ---: |
| linux_auth | malicious | 62 | `rajada_de_falhas_ssh` 48 (77,4%); `sudo_negado` 0 (0,0%) | 48 (77,4%) |
| linux_auth | suspicious | 33 | `rajada_de_falhas_ssh` 13 (39,4%); `sudo_negado` 0 (0,0%) | 13 (39,4%) |
| linux_auth | benign | 30 | `rajada_de_falhas_ssh` 5 (16,7%); `sudo_negado` 0 (0,0%) | 5 (16,7%) |
| linux_auth | expected_admin | 35 | `rajada_de_falhas_ssh` 1 (2,9%); `sudo_negado` 0 (0,0%) | 1 (2,9%) |
| apache | malicious | 40 | `travessia` 7 (17,5%); `sqli` 0 (0,0%) | 7 (17,5%) |
| apache | suspicious | 16 | `travessia` 0 (0,0%); `sqli` 0 (0,0%) | 0 (0,0%) |
| apache | benign | 42 | `travessia` 0 (0,0%); `sqli` 0 (0,0%) | 0 (0,0%) |
| apache | expected_admin | 14 | `travessia` 0 (0,0%); `sqli` 0 (0,0%) | 0 (0,0%) |
| suricata | malicious | 59 | `alerta_de_assinatura` 55 (93,2%) | 55 (93,2%) |
| suricata | suspicious | 30 | `alerta_de_assinatura` 20 (66,7%) | 20 (66,7%) |
| suricata | benign | 56 | `alerta_de_assinatura` 23 (41,1%) | 23 (41,1%) |
| suricata | expected_admin | 4 | `alerta_de_assinatura` 3 (75,0%) | 3 (75,0%) |

- **Cobertura dos Alertas:** 143 dos 240 Recortes malicious ou suspicious têm algum Sinal (59,6%). Um Alerta sem Sinal não tem a proteção do ADR 0003 contra injeção que rebaixa.
- **Rebaixamentos que exigirão Evidência do Contexto:** 32 dos 181 Recortes benign ou expected_admin têm algum Sinal (17,7%). Sem Evidência no Contexto, o Runtime os manda para revisão humana.
- Estes números são a base para rever os limiares do `sinais-0.1`, como prevê o ADR 0012.

## Como o responsável revisa a fila

1. Abra `data/processed/guardiao-v2-r01/fila-de-revisao.csv`. Cada linha é um Recorte, com os motivos, o rótulo da v12 e o hash do Recorte reprojetado.
2. Para cada ID, compare a entrada da v12 (`soc-triage-v12/splits/revisao.csv`) com o `texto_v2` do mesmo ID em `data/processed/guardiao-v2-r01/recortes.jsonl`.
3. Preencha as colunas de decisão:
   - `decisao`: `manter` (o rótulo continua sustentado pelo Recorte reprojetado ou por uma Ferramenta de leitura), `mudar` (preencha `veredito_revisado` e `severidade_revisada`), `contexto` (o rótulo depende de Contexto da curadoria; escreva o texto em `contexto_curado`) ou `descartar` (o Recorte sai do contrato v2 e conta como perda);
   - `nota`: o porquê, em uma frase.
4. Motivos que pedem atenção diferente:
   - `linha_citada_fora_do_registro`: a linha continua ao alcance de uma Ferramenta de leitura. Em geral basta `manter`, e a Trajetória derivada fará a chamada (ADR 0009).
   - `linha_citada_fora_do_alcance`: a Evidência saiu do alcance do Guardião. Decida entre `mudar`, `contexto` e `descartar`.
   - `alvo_nao_literal`: o alvo do v2 precisa citar valores que estão no Recorte. É uma correção do alvo, não do Veredito.
   - `numero_da_justificativa_ausente`: a justificativa da v12 cita contagens da janela antiga. Ela será reescrita no alvo do v2.
   - `contexto_da_curadoria`: transcreva em `contexto_curado` a agenda, a linha de base ou a mudança aprovada que sustentava o rótulo.
5. Guarde a planilha preenchida ao lado da fila, com outro nome. Nenhum script aplica decisões ainda: o contrato v2 só recebe um rótulo depois que a fila desse Recorte fechar.

## Limites

- Os motivos são verificações mecânicas. "Sem mudança detectada" não aprova o Recorte: a amostragem desse grupo também cabe ao responsável.
- `numero_da_justificativa_ausente` procura cada número da justificativa como palavra no Recorte. Um número pequeno pode aparecer por acaso.
- A Âncora vem das linhas citadas. Quando o lote citou linhas de várias Fontes, a janela usa só a Fonte da Âncora; as demais contam como fora do Registro.
- Syslog sem ano recebe o ano 2000 para calcular durações. O texto do Recorte repete o relógio do log e não mostra esse ano.
