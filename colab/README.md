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
E4B, em três montagens: `bf16-vllm`, `4bit-vllm` e `bf16-hf`. Cada montagem roda num processo
próprio.

```bash
colab new -s encaixe --gpu L4
colab upload -s encaixe colab/00_teste_de_encaixe.py /content/00_teste_de_encaixe.py
colab upload -s encaixe colab/requirements-encaixe.txt /content/requirements-encaixe.txt
colab upload -s encaixe <prompts.jsonl> /content/prompts.jsonl
echo '!pip install -q -r /content/requirements-encaixe.txt' | colab exec -s encaixe
echo '!python /content/00_teste_de_encaixe.py --modo bf16-vllm --dados /content/prompts.jsonl --saida /content/bf16-vllm.json' | colab exec -s encaixe
colab download -s encaixe /content/bf16-vllm.json runs/<pasta-da-execucao>/bf16-vllm.json
colab stop -s encaixe
```

O arquivo de prompts tem uma linha JSON por prompt, com o campo `prompt` na forma de mensagens
de chat. Ele sai dos Recortes da v12 e não entra no Git.
