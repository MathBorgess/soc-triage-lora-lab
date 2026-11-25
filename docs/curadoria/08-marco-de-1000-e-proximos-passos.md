# Marco de 1.000 registros e próximos passos da curadoria

Em 23/11/2026, Matheus definiu 1.000 registros tecnicamente validados como o marco suficiente para encerrar esta etapa de coleta. A fila consolidada do lote 12 chegou a **1.054 registros** e a coleta está pausada. [Resultado do lote 12](06-contrastes-de-autenticacao-e-resolucao.md)

| Estado na pausa | Quantidade |
| --- | ---: |
| Exemplos de treino aprovados na v7 | 415 |
| Propostas validadas que aguardam revisão humana | 639 |
| **Total que conta para o marco** | **1.054** |
| Validação e teste reservados | 11 e 9 |

A fila de referência está em `data/processed/lote-expansao-12/revisao-consolidada/`, com `revisao-acumulada.csv` e `auditoria.json`. A conferência no encerramento confirmou os hashes dos splits v7. O lote 13 foi preservado como rascunho em `data/processed/lote-expansao-13/`. Seus resultados ficam fora dos 1.054 e exigem consolidação, deduplicação e revisão se a coleta for retomada. [Registro parcial do lote 13](07-correlacao-entre-fontes-nativas.md)

## Análise na retomada

1. **Revisar as propostas por incidente.** Conferir se a evidência disponível até a âncora sustenta o veredito e a severidade. Registrar decisões por ID, preservar `precisa_contexto` quando faltarem sinais e conferir a deduplicação entre capturas, rotações e replays.
2. **Auditar cobertura e separar avaliação.** Tabular fonte, veredito, severidade e grupo em cada split. A v7 só tem Apache e autenticação Linux em validação e teste. Identificar amostras independentes para avaliar Sysmon, WAF e Suricata, com negativos difíceis para medir falsos positivos. Preservar CSE-CIC em validação, EchoLake Cloud Data Exfiltration e Organização Y em teste, e Santos/Harrison conforme o [manifesto de reservas](../../configs/datasets/reservas-avaliacao.yaml).
3. **Preparar uma versão candidata ao piloto.** O mínimo documentado é de 500 exemplos de treino aprovados. Faltam 85 aprovações líquidas. Após a revisão e a aprovação dos splits, exportar uma nova versão por grupo e repetir as verificações de schema, IoCs e tokenização no Gemma 4 E4B-it. Registrar os hashes dos splits, do prompt e da configuração. Rodar o baseline e iniciar treino somente com autorização.

## Coleta futura

- **Priorizar lacunas mensuráveis.** Dos 162 casos de `linux_auth` no marco consolidado, 18 têm veredito `malicious` entre aprovados e propostas. Buscar cenários independentes com desfecho observável, como aceite, abertura de sessão e efeito corroborado, e controles com falha seguida de atividade legítima. Para avaliação, buscar controles e positivos de Sysmon, WAF e Suricata em origens independentes do treino.
- **Reaproveitar os artefatos já recebidos.** Retomar o lote 13 a partir dos recibos e localizadores preservados. Conferir os casos de autenticação do AIT v1.1 e DEDALE, os controles DNS/TLS e a cobertura dos recortes Apache e Sysmon. O BOTS v3 possui journals verificados, com inventários de aplicação e autenticação ainda parciais. Consolidar apenas janelas com prova própria e grupos compatíveis com as reservas.
- **Medir rendimento por episódio.** Para novas fontes, começar por um recorte com licença, revisão e digest identificados. Registrar quantidade de grupos e propostas inéditas após deduplicação. Usar esse rendimento para decidir se vale ampliar o download.
