# Revisão das propostas do lote 12

A etapa de coleta encerrou no marco de **1.000 registros para revisão**. A fila consolidada contém **1.054 registros**, compostos de **415 exemplos aprovados para treino** e **639 propostas**. Validação e teste têm 11 e 9 exemplos, respectivamente, e ficam fora da contagem. O lote 13 permanece como rascunho local.

## Propostas

O [índice público](propostas.csv) contém as 639 propostas. Cada linha tem um ID público, um grupo pseudonimizado, a modalidade do log, o veredito e a severidade propostos e a faixa de tokens. As faixas abrangem até 128 tokens. Os aliases valem para esta publicação. A coluna de grupo permite avaliar concentração e selecionar casos de grupos distintos. A independência das origens é conferida na revisão local.

O [manifesto](manifesto.json) registra o SHA-256 do índice e os totais conferidos. A validação local da fila usou Pydantic, checagem literal de IoCs e o tokenizer offline do Gemma 4 E4B-it. O maior registro da fila tem 1.014 tokens para um limite de 1.024. Essa verificação técnica permite encaminhar o caso para revisão humana.

As evidências, os localizadores e a correspondência entre IDs públicos e locais permanecem no workspace autorizado. A fila de referência fica em `data/processed/lote-expansao-12/revisao-consolidada/`. O mapa fica em `data/processed/revisao-pr-publico/lote-12/aliases.json`, na mesma cópia local. A adjudicação de um caso exige acesso às suas evidências locais.

## Decisões para a revisão

1. Avaliar veredito e severidade pela evidência disponível até a âncora, agrupando casos do mesmo incidente. Usar `precisa_contexto` quando faltar uma observação decisiva.
2. Conferir a independência entre splits por incidente, origem, captura e replay. A verificação atual confere os hashes da v7 e os grupos reservados conhecidos. Validação e teste ativos cobrem Apache e autenticação Linux. Avaliar Sysmon, WAF e Suricata exige exemplos de avaliação para essas modalidades.
3. Priorizar autenticação Linux com desfecho corroborado e negativos difíceis. Preparar propostas de coleta futura a partir dessas lacunas caso a aquisição seja retomada.
4. Levar as decisões ao responsável. O piloto tem mínimo de 500 exemplos de treino aprovados e ainda requer 85 aprovações líquidas. A exportação de uma nova versão é seguida por nova checagem de esquema, IoCs e truncamento. A aprovação dos splits e a autorização de treino são decisões próprias.

[Prompt para revisão conjunta](prompt-revisao.md)
