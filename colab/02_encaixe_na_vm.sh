#!/usr/bin/env bash
# Roda na VM do Colab, desacoplado do terminal: instala, baixa o modelo e roda as montagens.
# O andamento fica em /content/estado.txt; cada etapa grava o próprio log em /content.
# Uso (na VM): bash 02_encaixe_na_vm.sh "<modos>" <precisao> <vllm_mem>
set -uo pipefail

MODOS="$1"
PRECISAO="$2"
VLLM_MEM="$3"
MODELO="google/gemma-4-E4B-it"
REVISAO="4ecc2ba63bcac23ba4a767fc87025b1450f84c9c"

estado() { printf '%s %s\n' "$(date -u +%H:%M:%S)" "$*" >> /content/estado.txt; }

estado "instalando"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv > /content/gpu.txt 2>&1
free -m >> /content/gpu.txt
if ! pip install -q -r /content/requirements.txt > /content/instalacao.log 2>&1; then
  estado "falha na instalação"
fi
pip list 2>/dev/null | grep -E "^(torch|vllm|trl|transformers|peft|bitsandbytes) " >> /content/instalacao.log

estado "baixando o modelo"
if ! python -c "from huggingface_hub import snapshot_download as s; print(s('$MODELO', revision='$REVISAO'))" \
  > /content/download.log 2>&1; then
  estado "falha no download"
fi

for modo in $MODOS; do
  estado "montagem $modo"
  python /content/00_teste_de_encaixe.py --modo "$modo" --dados /content/prompts.jsonl \
    --saida "/content/$modo.json" --vllm-mem "$VLLM_MEM" --precisao "$PRECISAO" \
    > "/content/$modo.log" 2>&1
  estado "montagem $modo terminou com código $?"
done
estado "FIM"
