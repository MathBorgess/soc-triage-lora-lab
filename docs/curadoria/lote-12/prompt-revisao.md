# Prompt para revisão conjunta

Copie o texto abaixo e indique ao agente o PR e a cópia local autorizada do laboratório.

```text
Atue como segundo revisor da curadoria de logs SOC comigo. Use o PR e o índice do lote 12 como ponto de partida. A referência congelada reúne 415 exemplos de treino aprovados e 639 propostas pendentes. Os splits v7 têm 415 treino, 11 validação e 9 teste.

Trabalhe em leitura. Na cópia local autorizada, use `data/processed/revisao-pr-publico/lote-12/aliases.json` para localizar os IDs originais em `data/processed/lote-expansao-12/revisao-consolidada/revisao-acumulada.csv` e `propostas-acumuladas.jsonl`. Confira o SHA-256 da fila em relação ao mapa. Se tiver acesso apenas ao PR, audite o índice e marque a análise da evidência como pendente. Preserve evidências e localizadores no ambiente local.

1. Comece por 12 casos de grupos distintos. Distribua entre modalidades e vereditos, priorizando `linux_auth` malicioso e negativos difíceis. Informe quais estratos ficaram fora da amostra.
2. Forme seu veredito e sua severidade pela evidência disponível até a âncora, antes de comparar com o rótulo proposto. Use `precisa_contexto` se faltar evidência. Para cada caso, apresente o alias, o sinal observado, a proposta original, sua proposta e a dúvida que precisa de minha decisão.
3. Procure duplicatas e possível vazamento por incidente, origem, captura, rotação e replay. Confira cobertura dos splits e sinalize o que ainda precisa de validação nativa, inclusive onde os grupos têm nomes diferentes.

Pare após o primeiro lote para discutirmos as divergências. Deixe promoção de rótulos, mudanças de splits, downloads, publicações e treino pendentes da minha decisão.
```
