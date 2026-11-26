---
status: accepted
---

# O SFT com ferramentas parte de Trajetórias derivadas, sem modelo professor

Em 26/11/2026, o responsável pelo estudo decidiu como o Guardião aprende a chamar Ferramentas de
leitura antes do RL (ADR 0005).

## Decisão

- Cada linha de Contexto de um Recorte da v12 que corresponde a uma ferramenta do catálogo vira
  uma chamada nessa Trajetória derivada.
- A resposta da chamada vem da execução real da ferramenta no Ambiente de treino, não do texto
  curado. Se a resposta divergir da linha de Contexto, o Recorte vai para revisão.
- Recortes em que o Contexto do Projetor basta entram sem nenhuma chamada.
- O Projetor continua escrevendo no Contexto o que não está nos logs, como a linha de base e as
  mudanças aprovadas.
- O catálogo final de ferramentas é o conjunto dos tipos de linha de Contexto que aparecem em pelo
  menos 20 Recortes da v12.

## Considered Options

- **Destilar trajetórias de um modelo maior.** Rejeitada. Exige API paga ou um modelo local de
  27B ou mais, e o Guardião herdaria o estilo e os erros do professor.
- **Escrever trajetórias à mão.** Rejeitada. Não escala para mais de mil Recortes.
- **Pular o SFT e começar direto no RL.** Rejeitada. Um modelo de 4B que não conhece o formato
  das chamadas gera grupos sem variância de recompensa, e o GRPO não aprende.

## Consequences

- O Ambiente de treino e as ferramentas precisam existir antes do SFT com ferramentas.
- O SFT imita as consultas que a curadoria achou úteis, não as melhores. O RL ajusta quando
  chamar.
- As divergências entre a ferramenta e o Contexto curado geram uma fila de revisão, e a taxa de
  divergência é reportada.
- Ferramentas usadas em menos de 20 Recortes saem do catálogo, e o Contexto delas volta a ser
  escrito pelo Projetor.
