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
