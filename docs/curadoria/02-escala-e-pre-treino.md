# De 92 exemplos a um corpus de 1.200

> Planejamento histórico. O [marco revisado de 1.000 registros técnicos e os próximos passos](08-marco-de-1000-e-proximos-passos.md) registram a decisão mais recente.

Registro de curadoria de 23/11/2026. Este documento acompanha a metodologia e os
resultados agregados do [primeiro registro de curadoria](01-evidencia-e-vies.md).

## O que conta para a meta

Um exemplo é uma janela que permite uma decisão de triagem. A janela tem uma
âncora, evidência rastreável no log e uma decisão revisada de veredito e severidade.
Um incidente pode oferecer janelas com decisões distintas. Janelas sobrepostas ou
com a mesma decisão e evidência equivalente recebem uma revisão de redundância.
Repetições, rotações e replays da mesma captura ficam na mesma família.

| Estado em 23/11 | Contagem |
| --- | ---: |
| Treino aprovado e exportado na v6 | 92 |
| Validação e teste já exportados | 11 e 9 |
| Propostas para treino com rótulos pendentes de revisão | 276 |
| Casos da fila que precisam de contexto | 19 |
| Aprovação retida por evidência insuficiente na janela | 1 |
| Aprovações que faltam para 1.200 no treino | 1.108 |

O DEDALE acrescentou 49 exemplos em um único grupo de treino. DED01 manteve o
rótulo aprovado `malicious/high` no registro de revisão. A anotação do incidente
confirma sua origem, mas o trecho de SSH disponível para o modelo apresenta os
mesmos sinais de uma sessão rotineira por chave. A exportação aguarda uma janela
com evidência discriminante. DED28–30 usam uma decisão no fim da janela, com
autenticação observada após o alerta. Esse horizonte precisa acompanhar qualquer
uso desses casos em um benchmark.

A v6 tem 54 janelas `linux_auth`, 21 `sysmon`, 14 `apache`, três
`suricata` e zero `waf` no treino. O DEDALE representa 53% do treino e
concentra os 20 positivos Sysmon. A prioridade é
obter controles Sysmon de outros ambientes, positivos Linux com contexto e
tráfego HTTP e Suricata que teste os limites da rotulagem.

## Margem de revisão

O planejamento usa **1.750 janelas na fila total**, incluindo as 92 já
exportadas. A fila atual cobre 368 dessas vagas se incluirmos as 276 propostas
rotuladas. Faltam **1.382 propostas adicionais**. Depois de deduplicação,
adjudicação e validação, a meta é ter 1.200 registros utilizáveis em treino.

| Retenção entre as 1.658 propostas futuras ou pendentes | Treino estimado | Margem sobre 1.200 |
| --- | ---: | ---: |
| 65% | 1.169 | −31 |
| 70% | 1.252 | +52 |
| 75% | 1.335 | +135 |

As taxas são cenários, com arredondamento para baixo. A retenção mínima é
aproximadamente 66,8%. Se a retenção observada for 65%, a fila precisa subir
para ao menos 1.797 janelas para chegar a 1.200. Recalibrar por origem e
classe de evidência após cada lote. Uma origem concentrada em poucos
incidentes pode atingir seu teto de diversidade antes de esgotar as linhas.

## Onde procurar as próximas janelas

As faixas abaixo são metas de amostragem condicionais de **novas propostas**.
O limite superior de cada frente exige confirmação de evidência e deduplicação.

| Frente | Faixa de planejamento | Escopo |
| --- | ---: | --- |
| Acervo local autorizado | 80–145 | Security-Gym v4.1 e Cyber Czech. Procurar sessões SSH completas, rotinas de manutenção e falhas seguidas de atividade confirmada. |
| Controles e cenários para piloto | 220–375 | Nextron clientes e servidores (80–140), CyLab (35–60), Online Shop (40–60), SR-BH (45–80), SOCBED (20–35). |
| Capturas adicionais com condições de elegibilidade | 325–555 | LAN multiorigem (80–140), Organização X (80–120), Linux-APT (70–120), AIT AttackMate (30–45), ASU Unraveled (30–60), AInception (10–25), Loghub Linux (10–20), Virtual Network Threat Detection (15–25). |
| Escala Sysmon com auditoria de linhagem | 240–360 | Telemetria Sysmon do catálogo ART do EchoLake. Amostrar um comportamento por execução, restringir a contribuição por família de comportamento e parear com controles Nextron ou CyLab. |
| Suricata derivado do AIT-LDS | 90–150 | AIT-ADS. Concentrar a expansão em cenários ainda livres após verificar a reserva de cada captura. |

O acervo local tem **891** chaves SSH com aceite, abertura e encerramento
ordenados no Cyber Czech, em sete segmentos do exercício. Elas foram ligadas
por segmento, host, PID e usuário. O Security-Gym tem **2.912** IDs de sessão em
3.737 registros `auth_log`; o inventário permite localizar contrastes. A
confirmação de rotina e a deduplicação entre segmentos ou cenários ainda
determinam quais podem entrar no corpus. [Cyber Czech](https://zenodo.org/records/3746129) · [Security-Gym](https://zenodo.org/records/21763493)

Prioridade de pesquisa para os próximos recortes:

1. **Organização X e Online Shop.** O primeiro tem cerca de 2,1 MB de logs
   Apache e regras do publicador. Separar X e Y somente após verificar
   independência das organizações e das capturas. O segundo tem 28,6 MB de
   requisições reais anonimizadas em formato Combined. Usar contexto de sessão
   e rotas para revisar 403 e 404. Verificar o servidor de origem antes de
   classificar a fonte como `apache` e preservar como `null` os IPs removidos
   ou substituídos por aliases que não sejam IPs válidos. [Organizações X/Y](https://zenodo.org/records/20001206) · [Online Shop](https://zenodo.org/records/18895701)
2. **Nextron v0.8.5 e CyLab.** Parear operações administrativas e árvores de
   processo em estações e servidores Windows. Para o próximo recorte Nextron,
   `win2022-ad.tgz` e `win2022-evtx.tgz` somam 93,4 MB. A extensão de
   servidor faz parte da mesma família Nextron. [evtx-baseline](https://github.com/NextronSystems/evtx-baseline/releases/tag/v0.8.5) · [CyLab](https://gitlab.cylab.be/cylab/datasets/apt-persistence/-/tree/c373881ab08c772270a090f06362bb71da819751/Datasets)
3. **Multi-source Cybersecurity LAN v2.0.** O arquivo
   `System_and_service_logs.zip` tem 460.724.720 bytes e eventos em JSON. O
   piloto depende da presença efetiva de Sysmon ou autenticação Linux e da
   ligação entre os horários do host e a campanha. Usar o dicionário para
   verificar campos, descartar severidades heurísticas e manter a coleta de
   PCAPs e payloads fora da amostra proposta. [Depósito](https://zenodo.org/records/24394558) · [Dicionário dos autores](https://zenodo.org/records/24394558/preview/DATA_DICTIONARY_v1.0.md?include_deleted=0)
4. **Catálogo ART, somente logs.** O inventário Git na revisão
   `38e19f60c366ef278e78f9c161c1248c812f7a4f` contém 1.640 arquivos
   `sysmon.xml.gz`, 1.607 blobs distintos e 15,3 MB ao todo. Um blob
   diferente pode representar o mesmo comportamento em outro host. A amostra
   usa dados de eventos já coletados e exige ligação ao cenário e controles
   comparáveis em captura separada. [Estrutura da captura ART](https://github.com/daveherrald/echolake-datasets/tree/38e19f60c366ef278e78f9c161c1248c812f7a4f/datasets/art)
5. **AIT Alert Data Set.** O arquivo `ait_ads.zip` tem 96,2 MB.
   Usar somente o evento Suricata nativo dentro dos registros, com a
   cronologia para localizar e revisar a janela. Santos e Harrison já têm
   splits reservados. Preservar a linhagem AIT também em cada cenário novo e
   cruzar com os recortes já curados. [AIT-ADS](https://zenodo.org/records/8263181)

As demais opções no planejamento são [SR-BH](https://doi.org/10.7910/DVN/OGOIXX),
[SOCBED](https://github.com/fkie-cad/socbed-eval-acsac-2021),
[Linux-APT](https://data.mendeley.com/datasets/5x68fv63sh/2),
[AIT AttackMate](https://zenodo.org/records/19810174),
[ASU Unraveled](https://gitlab.com/asu22/unraveled/-/tree/d2ea90055d82fa448ab20588a13e3ec8bfd74816/data/host-logs),
[AInception](https://zenodo.org/records/17659656),
[Loghub Linux](https://zenodo.org/records/8196385) e
[Virtual Network Threat Detection](https://marc-chamorro.github.io/virtual-network-threat-detection/ml/data/).
SOCBED e DEDALE exigem comparação de linhagem de coleta. ASU e Virtual Network
Threat Detection exigem confirmação de termos de uso dos dados. Linux-APT exige
ligar telemetria original e anotações ao mesmo episódio. ModSec-WP fica na fila
existente e qualquer extensão começa pela deduplicação das transações.

As frentes somam **955–1.585** novas propostas sob essas hipóteses. O teto cobre
as 1.382 vagas com margem de 203 propostas. A parte inferior da faixa deixa
déficit, então o próximo lote precisa medir o rendimento e informar onde ampliar.
OTRF APT29/Atomic, Biblio-US17 e recortes Splunk ficam como alternativas sem
cota. Os bloqueios são licença ou acesso, procedência dos rótulos e sobreposição
com outros catálogos. [OTRF](https://github.com/OTRF/Security-Datasets/tree/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87) · [Biblio-US17](https://doi.org/10.12795/11441/148254) · [Splunk no EchoLake](https://github.com/daveherrald/echolake-datasets/tree/38e19f60c366ef278e78f9c161c1248c812f7a4f/datasets/splunk-detections)

Se faltarem famílias de Windows, COMISET LAB tem custo de aquisição maior
(4,9 GB) e permite investigar o evento original atrás dos rótulos por regra.
Se faltarem negativos Apache, o Rootly publica logs de acesso e erro.
Sua contribuição depende de identificar a captura upstream e excluir
reaproveitamento do Loghub. Essas reservas ficam fora do total estimado.
[COMISET LAB](https://zenodo.org/records/15375146) · [Rootly](https://github.com/Rootly-AI-Labs/logs-dataset)

## Curadoria e validação antes do fine-tuning

1. Selecionar janelas pelo sinal que muda a decisão. Para o bastion, parear
   positivos e controles por papel do host, autenticação, desfecho, volume
   e duração. Uma sessão finalizada mostra seu desfecho. A autorização para
   `expected_admin` precisa de contexto adicional observável.
2. Revisar em lotes com localizador, janela, justificativa, veredito, severidade
   e evidência ausente. Separar os rótulos do publicador da entrada. Manter
   `precisa_contexto` na revisão e usar `null` para campos que o contrato permite
   omitir quando o veredito da janela é sustentado.
3. Preservar as [reservas](../../configs/datasets/reservas-avaliacao.yaml) por
   campanha ou organização. O EchoLake também espelha capturas do Splunk e da
   série BOTS, inclusive com horários deslocados. A reserva atual do EchoLake é
   a captura Cloud Data Exfiltration. Verificar nomes de origem, revisões,
   hashes e similaridade de janelas em adições futuras. [Catálogo EchoLake](https://github.com/daveherrald/echolake-datasets/tree/38e19f60c366ef278e78f9c161c1248c812f7a4f#boss-of-the-soc-bots-datasets)
4. Validar schema e IoCs em todas as janelas aprovadas. Relatar concentração
   por grupo e distribuição por fonte, veredito e severidade. Rodar o tokenizer
   do Gemma 4 E4B-it nas conversas completas e conferir o orçamento de 1.024
   tokens. A v6 passou com 112 sequências, zero truncamentos e máximo de 969
   tokens.
5. Verificar cobertura de validação e teste para os recortes que se quer medir.
   A v6 tem só Apache e autenticação Linux nesses splits. Avaliar FPR nos
   negativos difíceis e Macro-F1 por telemetria quando houver suporte. Congelar
   a versão usada no baseline e nas ablações após a revisão do corpus.

O conjunto de trabalho fica local. Para uma versão pública, preparar
estatísticas, regras de adjudicação, referências e exemplos sintéticos.
Redistribuição de recortes depende dos termos da fonte e da revisão do conteúdo.
