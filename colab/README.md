# Treino no Google Colab

Esta pasta guarda os scripts e as dependências que rodam no Colab (ADR 0005, emendas de
26/11/2026). Nada daqui roda no projeto principal: `bitsandbytes`, `vllm` e CUDA ficam só na VM.

## Regras

- Use o Colab CLI (`google-colab-cli`) e dê sempre um nome à sessão com `-s`.
- Encerre a sessão com `colab stop -s <nome>` ao fim de cada etapa. VM ociosa continua
  consumindo unidades.
- Confira o saldo e a taxa com `colab usage` antes e depois de cada etapa.
- Nenhum token entra na VM por este repositório. O modelo base é público.
- Resultados e checkpoints voltam para `runs/` com `colab download`, fora do Git.

## Teste de encaixe

`00_teste_de_encaixe.py` mede memória, tempo e tokens de alguns passos de GRPO com o Gemma 4
E4B, em quatro montagens: `bf16-vllm`, `4bit-vllm`, `bf16-hf` e `4bit-hf`. Cada montagem roda
num processo próprio. Antes do treino, ele gera uma resposta gulosa para conferir a saída.

`01_rodar_encaixe.sh` faz tudo numa sessão nova e sempre encerra a VM no fim:

```bash
colab/01_rodar_encaixe.sh A100 runs/<execucao>/prompts.jsonl runs/<execucao>/a100 0.5
```

A T4 não tem BF16 e tem 16 GB. Nela, só a montagem `4bit-hf` em FP16 faz sentido, sem vLLM:

```bash
MODOS=4bit-hf REQUISITOS=requirements-t4.txt PRECISAO=fp16 colab/01_rodar_encaixe.sh T4 runs/<execucao>/prompts.jsonl runs/<execucao>/t4
```

O arquivo de prompts tem uma linha JSON por prompt, com o campo `prompt` na forma de mensagens
de chat. Ele sai dos Recortes da v12 e não entra no Git.

## Resultado do teste de encaixe (26/11/2026)

L4, A100 e T4 com RAM alta receberam "503 Service Unavailable" do Colab. Só a T4 padrão alocou.
Resultados da montagem `4bit-hf` em FP16 na T4, com 3 passos de DAPO e LoRA r16 em 258 módulos
(34,9 M parâmetros treináveis):

| Medida | 1 prompt por passo | 2 prompts por passo |
| --- | --- | --- |
| Pico de memória da GPU (nvidia-smi) | 13,3 GB de 15,4 GB | 14,3 GB de 15,4 GB |
| Tempo por passo | 78 a 86 s | 96 a 108 s |
| Respostas por passo | 8, com ~180 tokens | 16, com ~175 tokens |
| RAM da VM | ~2,7 GB de 12,9 GB | ~3,3 GB de 12,9 GB |
| NaN | não | não |

- **FP16:** a resposta gulosa antes do treino saiu em JSON válido, com triagem plausível. O FP16
  não estragou a saída.
- **Gradiente real:** com a recompensa variada, o `grad_norm` ficou entre 0,27 e 0,33.
- **Pesos do LoRA:** nasceram em BF16 e precisaram ir para FP32, por causa do GradScaler do FP16.
- **Custo:** a T4 custou 1,24 unidade por hora. Os testes de 26/11 gastaram 5,63 unidades no
  total, incluindo duas quedas de conexão e uma VM ociosa por uma consulta travada.
- **Limites:** o teste usou respostas curtas, de turno único. Episódios com ferramentas serão
  mais longos, e a folga de memória da T4 é de ~1 GB. A T4 não cabe o E4B em 16 bits, então a
  Run 3 da ablação (BF16) não roda nela.

