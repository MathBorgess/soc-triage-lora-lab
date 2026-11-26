---
status: accepted
---

# O opensec-triage entra no treino por Família, e o Guardião se mede só no Teste real

Em 25/11/2026, o responsável pelo estudo definiu que o Guardião precisa superar o Rival, o adaptador
`infosecn1nja/soc-triage-nemotron-bolt-e4b-lora`, reaproveitando o dataset que o treinou,
`tegridydev/opensec-triage` (CC BY 4.0). O Rival reporta Macro-F1 0,954 em 55 exemplos
sintéticos da mesma família do treino. O opensec é 100% sintético e não declara o modelo gerador
nem revisão humana. O próprio card admite que TF-IDF com regressão logística acerta 100% de um
split. Por isso a decisão separa o uso dos dados da medida de superioridade:

- Os Exemplos sintéticos entram no treino com teto de um para cada exemplo real (cerca de
  1.100), estratificados por Família e priorizando os grupos contrafactuais. As linhas de
  validação e teste do opensec ficam em splits próprios, usados só como diagnóstico.
- A aprovação é por Família: o responsável aprova a regra de derivação e uma amostra das linhas.
  É uma exceção deliberada à aprovação linha a linha do AGENTS.md. Cada Família registra a regra,
  o tamanho da amostra e o resultado da revisão.
- Cada exemplo vira um Recorte da Modalidade `audit`. O `observable` vai para o Registro. A
  `evidence` e o contexto de negócio vão para o Contexto. Assim o modelo não aprende a obedecer
  texto que afirma a conclusão.
- A superioridade se mede no Teste real: Macro-F1 maior, FPR igual ou menor e não mais
  `malicious` perdidos. O teste do opensec é secundário, com TF-IDF + LR como piso.

## Considered Options

- **Aprovar linha a linha cerca de 1.100 sintéticos.** Rejeitada. O custo é alto, e revisar
  linhas não resolve o gerador desconhecido nem a separabilidade por estilo.
- **Não usar o opensec.** Fica como braço da ablação (proporção zero), não como decisão.
- **Medir a superioridade no teste do opensec, como faz o Rival.** Rejeitada. Avaliação só em
  laboratório, com sintéticos separáveis, infla resultados (Arp et al., USENIX Security 2022; ver
  `docs/pesquisa/01-revisao-de-literatura.md`).

## Consequences

- O treino v2 compara as proporções sintético:real 0; 0,25; 0,5 e 1, medidas só na validação
  real.
- Um classificador real contra sintético serve de diagnóstico de vazamento de estilo.
- O gerador desconhecido e o risco de envenenamento ficam declarados como ameaças à validade.
  Cerca de 100 exemplos envenenados bastaram para plantar um gatilho em instruction tuning (Wan
  et al., ICML 2023), então o tamanho da amostra de cada Família precisa de justificativa.
- Qualquer publicação credita o opensec-triage conforme a CC BY 4.0.
