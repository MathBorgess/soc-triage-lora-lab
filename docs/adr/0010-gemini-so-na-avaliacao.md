---
status: accepted
---

# O Gemini entra só na avaliação, pela Gemini API paga

Em 26/11/2026, o responsável liberou o Gemini e os créditos de Google Cloud do AI Pro, com os
US$ 10 mensais gastos por inteiro (emenda 2 do ADR 0005), e aceitou usá-los só na avaliação.

## Decisão

A Gemini API paga, descontada dos créditos, tem três usos:

1. **Comparador "Gemini central com log bruto".** Recebe o Recorte inteiro no Teste real e numa
   amostra de harrison. Mede quanto de detecção a arquitetura local perde ou ganha frente a um
   modelo grande na nuvem, e quanto dado sai da máquina para isso. É a referência do eixo de
   governança.
2. **Juiz do ExCyTIn-Bench.** Reabre o ExCyTIn como teste de generalização da política de
   consulta.
3. **Moldes de injeção da Suíte adversarial.** O Gemini propõe moldes, o responsável revisa, e
   os moldes entram só na avaliação.

O Gemini não gera rótulos, Trajetórias, recompensas nem nenhum dado que entre no treino. Para
gastar os US$ 10 do mês, o uso 1 cresce até cobrir harrison inteiro.

## Considered Options

- **Gemini como professor ou rotulador do treino.** Rejeitada. Os Termos de Serviço do Google
  proíbem usar conteúdo gerado pela IA deles para desenvolver modelos (H-25), e os termos da
  Gemini API proíbem desenvolver modelos que concorram com o serviço (H-21). Também contradiz
  o ADR 0009 e mistura a procedência dos dados.
- **Gemini CLI com o login do AI Pro, em lote.** Rejeitada. Segue os termos de consumidor (H-25)
  e não é o caminho documentado para uso automatizado (H-22).
- **Não usar o Gemini.** Rejeitada pelo responsável, que quer os créditos usados.

## Consequences

- O responsável ativa os créditos no Google Developer Program, cria a conta de faturamento e faz
  o pré-pagamento mínimo de US$ 5 no AI Studio (H-20). Nada disso pode ser feito por um agente.
- Só Recortes de datasets públicos vão à API. Logs reais confidenciais nunca vão. Na API paga, os
  prompts não treinam modelos do Google (H-21).
- O custo por chamada e o volume enviado são registrados em `runs/`, como qualquer execução.
- O artigo declara que um Comparador usa um modelo de nuvem e por quê.
