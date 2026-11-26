# Fontes adicionais e controles da triagem SOC

Continuação do [registro de rendimento](03-rendimento-e-rastreabilidade.md), em 23/11/2026. A v7 e a fila do lote 09 servem de referência congelada. O consolidador do lote 10 revalida a fila anterior e acondiciona as novas propostas num CSV próprio e num CSV acumulado. O lote mantém os casos de avaliação fora da contagem de expansão.

O lote 10 trouxe **80 propostas validadas**, incluindo 56 controles. O total acumulado ficou em **877 de 1.200**, com 323 unidades pendentes.

## Evidência dos negativos difíceis

No CPTC3, a correlação HTTP usa registros EVE do mesmo sensor. O cliente e o servidor precisam de contexto consistente. Um redirecionamento vem acompanhado pela observação do destino e da resposta correspondente. Uma resposta 304 tem um acesso anterior ao mesmo recurso. Uma falha localizada no ativo é revisada junto à sequência de navegação que a rodeia. As equipes compartilham o grupo do exercício usado nas propostas de autenticação. [Acervo CPTC no RIT](https://mirrors.rit.edu/cptc/)

A amostra Virtual Network Threat Detection ilustra outro contraste. O mesmo cliente recebe recusa numa consulta reversa e obtém resposta válida para uma consulta direta no mesmo resolvedor. O resultado do DNS e o tipo de consulta ficam explícitos na janela. [Documentação da fonte](https://marc-chamorro.github.io/virtual-network-threat-detection/ml/data/)

O catálogo EVTX-ATTACK-SAMPLES acrescentou 15 propostas `suspicious` apoiadas em pares Sysmon com efeito observável. O catálogo tem 278 membros EVTX e gerou 32 pré-seleções. A curadoria agrupou ocorrências simultâneas do mesmo processo e comparou as formas com as filas anteriores. A verificação reabriu as 30 coordenadas usadas nos 15 casos. O nome do arquivo é reservado à proveniência. [Catálogo EVTX-ATTACK-SAMPLES](https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES/tree/4ceed2f4706daf601c212a8f91c113dd85349a2c)

## Medidas de rendimento

| Fonte ou recorte | Volume observado | Propostas na triagem da fonte |
| --- | ---: | ---: |
| CPTC3 EVE HTTP | 2.606.607 transações | 18 |
| CPTC4 | 6.640 registros EVE regionais e 1.369.221 nacionais em três journals amostrados | 10 |
| PAWS | 685.735 eventos Sysmon | 15 |
| ProvCon | 11 arquivos em seis campanhas | 6 |
| Atomic-EVTX TalTech | 180 execuções e três capturas de controle amostradas | 7 |
| EVTX-ATTACK-SAMPLES | 278 membros, 37.357 eventos lidos e 3.234 Sysmon | 15 |
| Suricata Sample Data v4 | 566.975 transações candidatas e 2.137 janelas pré-selecionadas | 2 |
| AInception | 63 membros verificados por faixa em ZIP | 3 em autenticação Linux |
| ASCEND Clubs e Wicked6 | 513 membros de autenticação dos servidores-alvo | 3 |
| Virtual Network Threat Detection | Um recorte EVE de laboratório de rede | 1 |

O arquivo Suricata Sample Data v4 reúne quatro recortes. As duas propostas retidas mostram repetições em rotas distintas com predominância de erro, contextualizadas pelo mesmo cliente e serviço. A janela agregada termina na última transação usada na decisão. A rechecagem leu 47 coordenadas nativas. O digest da publicação é local e o tamanho coincide com o ativo oficial. [Suricata Sample Data v4](https://github.com/FrankHassanabad/suricata-sample-data/releases/tag/v4.0.0) · [AInception](https://zenodo.org/records/17659656)

A inspeção do CPTC4 recuperou eventos EVE de um journal regional e dois nacionais em prefixos de 8 e 148 MiB. O primeiro journal nacional rendeu quatro propostas. O segundo rendeu seis após descartar 245 combinações equivalentes ou sobrepostas. Foram relidas 33 referências nacionais por offset e hash. [Acervo CPTC4](https://mirrors.rit.edu/cptc/cptc4/)

Em PAWS, as tarefas administrativas são corroboradas entre o Agendador e o Sysmon. ProvCon preserva campanha e máquina. Os registros de criação e término cobertos no recorte Atomic-EVTX sustentaram controles de rotina. [PAWS](https://github.com/daveherrald/echolake-datasets/tree/38e19f60c366ef278e78f9c161c1248c812f7a4f/datasets/paws-operation-yarn-ball) · [ProvCon](https://github.com/NUS-Curiosity/provcon/tree/57e38a58b3d62d295a20259f7ab49a616a112419) · [TalTech](https://github.com/arniki/atomic-evtx/tree/8de5fa8f158b4d72d1e3c6f07053162c90ee6238)

A seleção do ASCEND preservou o grupo de linhagem das duas edições. Os arquivos completos de estudo incluem várias modalidades. A aquisição usou o índice ZIP64 e intervalos HTTP só dos membros de autenticação dos servidores-alvo, com conferência de CRC e SHA-256. Os 10.708 eventos de falha elegíveis vieram de um único endereço de origem. A seleção reteve dois episódios de autenticação suspeita e um controle de agendamento. [ASCEND OGames](https://ascend-data.sri.com/experiment-ogames-2025/) · [Licença](https://ascend-data.sri.com/ascend-data-license.txt)

No BOTS v2, a leitura seletiva de 261 MiB confirmou um journal com 11.725 eventos Sysmon e 3.739 linhas SSH RFC3164. A única janela Sysmon elegível repetia uma forma existente. O recorte SSH omite o fuso de origem. O lote reteve zero propostas dessa amostra. [BOTS v2 oficial](https://github.com/splunk/botsv2)
