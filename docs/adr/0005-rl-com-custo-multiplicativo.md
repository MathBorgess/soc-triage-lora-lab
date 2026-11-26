---
status: accepted
---

# O Guardião aprende quando investigar por RL com custo multiplicativo

Em 26/11/2026, o responsável pelo estudo aceitou o desenho do RL do Guardião com Ferramentas de
leitura (ADR 0004). A base está na [revisão 03](../pesquisa/03-rl-ferramentas-e-medicao.md).

## Decisão

**Recompensa.**

- **Gate:** o Relato precisa ser JSON válido no contrato v2, e toda Evidência precisa estar
  literalmente no Recorte ou numa resposta que as ferramentas realmente devolveram no episódio.
  Sem isso, a recompensa é −1.
- **Acerto:** a utilidade vem de uma Matriz de custo pré-registrada. Perder um malicious é o erro
  mais caro. `suspicious` custa menos que um erro completo, mas nunca zero.
- **Custo de investigação:** só multiplica a recompensa de Relatos corretos, com fator entre 0,5
  e 1. Os tokens contados são só os que o modelo gera.
- **Chamada desnecessária:** definida por regra. Conta a chamada duplicada, inválida ou fora da
  janela permitida, e a que passa do mínimo de chamadas visto entre os Relatos corretos do mesmo
  Recorte.
- **Busca vazia:** uma resposta de ferramenta sem linhas nunca serve como Evidência de benigno.
- **Pré-registro:** a Matriz de custo e 2 ou 3 razões entre o custo de um malicious perdido e o
  de um Falso positivo são fixadas antes do primeiro treino.

**Fronteira de custo.** Uma única política recebe o Peso de custo no prompt, sorteado a cada
episódio do treino. Na avaliação, o Peso de custo varia para traçar a fronteira inteira. Duas ou
três políticas de peso fixo servem para conferir a política condicionada.

**Algoritmo.** Dr. GRPO ou DAPO, nunca o GRPO original. As respostas das ferramentas ficam fora
da loss. Grupos sem variância de recompensa são descartados. O KL fica pequeno e entra só como
ablação. Cada Recorte gera 8 trajetórias.

**Stack.**

- No Mac, com MLX: Ambiente de treino, recompensas, Comparadores, SFT de partida e um piloto de
  turno único.
- No Colab L4, com TRL e vLLM: o GRPO com várias chamadas por episódio. O código fica em
  `colab/`. Esta decisão vale como a implementação aprovada que o AGENTS.md exige para a stack
  do Colab.

**Comparadores.** Com o mesmo custo de investigação, o Guardião treinado por RL precisa superar:

1. o Guardião sem ferramentas;
2. o Direct-Prompt com até 3 chamadas;
3. um controlador externo sem treino, no estilo do HESP;
4. regras ou TF-IDF;
5. a mesma receita de RL com recompensa embaralhada.

**Calibração.** O Risco de falso positivo continua um enum. A calibração dele é medida na
validação. Um calibrador separado fica fora do escopo e entra como limitação declarada.

## Considered Options

- **Custo de chamadas aditivo.** Rejeitada. Colapsa: o modelo aprende a cortar chamadas sem
  acertar (OTC e L1, notas F-15 e F-16).
- **Sem custo de investigação.** Rejeitada. O uso de ferramenta cresce durante o treino até
  quase toda pergunta (ReSearch e ReTool, F-9 e F-11).
- **Uma política por Peso de custo.** Rejeitada. Multiplica o custo de treino, e a política
  condicionada cobre a fronteira inteira (F-16).
- **GRPO original.** Rejeitada. Alonga as respostas erradas (F-3, F-4).
- **RL com várias chamadas no MLX.** Rejeitada. O `mlx-lm-lora` 5.10.2 só faz GRPO de turno
  único, e uma época levaria de 3 a 5 dias no M1 Max, contra 7 a 8 h estimadas numa L4.
- **Calibrador separado.** Adiada. Seria outro modelo a treinar, assinar e auditar.

## Consequences

- O primeiro treino de RL espera o pré-registro da Matriz de custo.
- O diretório `colab/` passa a existir, com dependências próprias. `bitsandbytes`, `unsloth` e
  CUDA continuam fora do projeto principal.
- O treino consome unidades de computação do plano do Colab. Comprar unidades extras é um gasto
  e exige aprovação.
- Uma Matriz de custo mal calibrada pode levar o modelo a responder `suspicious` para tudo
  (F-21). A distribuição dos Vereditos é acompanhada em cada checkpoint.
- O controle com recompensa embaralhada separa o ganho da recompensa do ganho de formato (F-7).
- O Runtime agêntico precisa passar o Peso de custo ao Guardião também em produção.

## Emenda de 26/11/2026: orçamento e uso do Colab

- O teto é o saldo de unidades de computação do plano do Colab do responsável.
- A ordem de execução é:
  1. um piloto curto, para medir a vazão e o consumo reais;
  2. a política condicionada ao Peso de custo;
  3. o controle com recompensa embaralhada;
  4. as políticas de peso fixo, só se sobrar saldo.
- O treino grava checkpoints no Drive a cada cerca de 50 passos, porque a sessão pode cair.
- Nenhuma compra de unidades sem aprovação do responsável.
- A GPU padrão é a L4. A A100 40 GB só entra se o Guardião com vLLM não couber nos 24 GB da L4.
  G4 e H100 ficam fora, porque custam mais por trabalho, e a T4 também, porque não tem BF16.
- O Mac faz o SFT, a avaliação e os Comparadores. O Colab faz só o RL. Outras plataformas, como
  o Kaggle, ficam fora enquanto o saldo bastar.
- As sessões usam `colab new`, `colab exec` e `colab stop`. O checkpoint do adaptador sai da VM
  a cada 30 a 60 minutos com `colab download` para `runs/`, fora do Git. O Drive fica como
  reserva manual.
- O Gemini não gera rótulos, Trajetórias, recompensas nem julgamentos que entrem no treino, porque
  os Termos de Serviço do Google proíbem usar conteúdo gerado pela IA deles para desenvolver
  modelos (H-25). Os créditos de Google Cloud e o pré-pagamento da Gemini API não são ativados.
- Os valores, os limites e as alternativas gratuitas estão na nota
  [H](../pesquisa/notas/H-ai-pro-e-custos-de-computacao.md).

## Emenda 2 de 26/11/2026: treino no Colab, Hugging Face e Gemini

Mais tarde no mesmo dia, o responsável mudou três pontos da emenda anterior:

- **Treino.** Todo o treino do Guardião roda no Colab: o SFT e o RL. O Mac fica com o Ambiente
  de treino, as recompensas, a avaliação local e os Comparadores locais. Isso também evita
  converter o adaptador do SFT do MLX para o PEFT antes do RL.
- **Armazenamento.** Datasets e modelos ficam no Hugging Face Hub, fora do Git. A visibilidade
  de cada repositório é decisão do responsável.
- **Gemini e créditos.** O Gemini e os créditos de Google Cloud do AI Pro passam a poder ser
  usados, e os US$ 10 mensais devem ser usados por inteiro. Isso substitui o item da emenda
  anterior que não ativava os créditos. Os termos continuam valendo: os Termos de Serviço do
  Google proíbem usar conteúdo gerado pela IA do Google para desenvolver modelos (H-25), e os
  termos da Gemini API proíbem desenvolver modelos que concorram com o serviço (H-21). A Gemini
  API paga exige conta de faturamento e pré-pagamento mínimo de US$ 5 (H-20). O uso exato fica
  registrado em ADR próprio.

## Emenda 3 de 26/11/2026: A100 nos testes e ablação no Colab

- As duas tentativas de alocar uma L4 receberam "503 Service Unavailable". O responsável decidiu
  seguir os testes na A100 40 GB enquanto a L4 estiver indisponível. A L4 continua sendo a padrão
  quando voltar e quando o modelo couber.
- A primeira tentativa na A100, às 12:24 UTC, também recebeu "503 Service Unavailable". A falha
  coincide com a issue googlecolab/colabtools#6289, aberta por assinantes que perderam acesso a
  L4, A100 e G4 desde cerca de 16/11/2026, sem resposta do Google em 26/11/2026.
- A matriz de ablação também passa para o Colab, com PEFT. O 4-bit passa a ser o NF4 do
  `bitsandbytes`, e o PiSSA vem do PEFT. O MLX fica para smoke tests e inferência local, e os
  smoke runs antigos do MLX deixam de ser comparáveis com as rodadas novas.
- O uso do Gemini está no ADR 0010, e a publicação no Hugging Face está no ADR 0011.

## Emenda 4 de 26/11/2026: o algoritmo é o DAPO

O responsável escolheu o DAPO, que a decisão original deixava como alternativa ao Dr. GRPO. O
DAPO roda no `GRPOTrainer` do TRL 1.19.0, que já implementa:

- a loss por token (`loss_type="dapo"`);
- o corte assimétrico, com `epsilon_high` de 0,28;
- a exclusão das respostas cortadas da loss (`mask_truncated_completions`);
- a ausência de KL (`beta` 0).

O TRL não repõe os grupos sem variância, como faz a amostragem dinâmica do artigo do DAPO. Esses
grupos não contribuem para o gradiente, e a fração deles é registrada em cada passo.

