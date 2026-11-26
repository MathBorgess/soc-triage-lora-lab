---
status: accepted
---

# A Matriz de custo é pré-registrada, e o Peso de custo fica fixo na Liberação

Em 26/11/2026, o responsável pelo estudo fixou os valores que o ADR 0005 deixou para o
pré-registro. A unidade é o custo de um Falso positivo `suspicious`, que vale 1. R é o custo de
perder um malicious.

## Decisão

**Matriz de custo** (linha: Veredito de referência; coluna: Veredito do Relato):

| Referência \ Relato | malicious | suspicious | benign | expected_admin |
| --- | --- | --- | --- | --- |
| malicious | 0 | 1 | R | R |
| suspicious | 0,5 | 0 | R/2 | R/2 |
| benign | 1,5 | 1 | 0 | 0,1 |
| expected_admin | 1,5 | 1 | 0,1 | 0 |

**Recompensa.**

- Relato que falha no gate do ADR 0005: −1.
- Relato errado: −custo/R.
- Relato certo: entre 0,5 e 1, conforme o custo de investigação.

Assim, qualquer Relato certo vale mais que qualquer Relato errado, e perder um malicious vale
tanto quanto um Relato inválido.

**Razões.** O treino usa só R = 10. R = 3 e R = 30 entram só na avaliação, como custo esperado
da mesma política. Com R = 10 e probabilidade calibrada, o limiar de Elkan para emitir Alerta fica
perto de 0,09.

**Peso de custo em produção.** O valor é escolhido na validação pelo menor custo esperado de erro
com R = 10. Entre valores cujo custo de erro não difere com significância, vence o de menor custo
de investigação. O valor fica gravado no manifesto da Liberação, e mudar o valor exige uma
Liberação nova. O Diário de inferências registra o valor usado em cada Relato.

## Considered Options

- **Treinar uma política por razão R.** Rejeitada. Triplica o treino, e o custo esperado em
  outras razões já mostra a sensibilidade da mesma política.
- **Custo igual para todo Falso positivo.** Rejeitada. Um malicious falso pesa mais na fila do
  analista do que um suspicious falso.
- **Custo zero para `suspicious` quando a referência é malicious.** Rejeitada. Empurra o modelo
  para responder `suspicious` em tudo (F-21).
- **Peso de custo ajustável na máquina, sem nova Liberação.** Rejeitada. O Relato deixaria de ser
  reexecutável a partir do que a Liberação garante.

## Consequences

- A matriz fica fixa antes do primeiro treino. Mudá-la depois exige um novo pré-registro
  declarado no artigo.
- O Validador e o Diário passam a ler o Peso de custo do manifesto da Liberação.
- A confusão entre benign e expected_admin custa pouco na recompensa, mas continua contando no
  Macro-F1.
