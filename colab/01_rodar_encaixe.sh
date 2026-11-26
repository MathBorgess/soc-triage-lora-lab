#!/usr/bin/env bash
# Roda o teste de encaixe numa sessão nova do Colab e sempre encerra a VM no fim.
# Uso: colab/01_rodar_encaixe.sh <GPU> <prompts.jsonl> <pasta-de-saida> [vllm_mem]
# Exemplo: colab/01_rodar_encaixe.sh A100 runs/<execucao>/prompts.jsonl runs/<execucao>/a100 0.5
set -uo pipefail

GPU="$1"
PROMPTS="$2"
SAIDA="$3"
VLLM_MEM="${4:-0.5}"
SESSAO="encaixe"
AQUI="$(cd "$(dirname "$0")" && pwd)"
MODELO="google/gemma-4-E4B-it"
REVISAO="4ecc2ba63bcac23ba4a767fc87025b1450f84c9c"

mkdir -p "$SAIDA"
log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }

encerrar() {
  log "encerrando a sessão $SESSAO"
  colab stop -s "$SESSAO" || true
  colab usage | tee "$SAIDA/usage-depois.txt"
  colab sessions | tee "$SAIDA/sessoes-depois.txt"
}

colab usage | tee "$SAIDA/usage-antes.txt"
log "alocando $GPU"
if ! timeout 600 colab new -s "$SESSAO" --gpu "$GPU"; then
  log "falha ao alocar $GPU"
  colab sessions | tee "$SAIDA/sessoes-depois.txt"
  exit 2
fi
trap encerrar EXIT
trap 'exit 143' TERM INT

colab usage | tee "$SAIDA/usage-com-vm.txt"
colab upload -s "$SESSAO" "$AQUI/00_teste_de_encaixe.py" /content/00_teste_de_encaixe.py
colab upload -s "$SESSAO" "$AQUI/requirements-encaixe.txt" /content/requirements-encaixe.txt
colab upload -s "$SESSAO" "$PROMPTS" /content/prompts.jsonl

executar() { echo "$1" | colab exec -s "$SESSAO" --timeout 1500; }

log "instalando dependências"
executar '!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv && pip install -q -r /content/requirements-encaixe.txt 2>&1 | tail -5 && pip list 2>/dev/null | grep -E "^(torch|vllm|trl|transformers|peft|bitsandbytes) "' \
  | tee "$SAIDA/instalacao.txt"

log "baixando o modelo"
executar "!python -c \"from huggingface_hub import snapshot_download as s; print(s('$MODELO', revision='$REVISAO'))\"" \
  | tee "$SAIDA/download.txt"

for modo in bf16-vllm 4bit-vllm bf16-hf; do
  log "montagem $modo"
  executar "!python /content/00_teste_de_encaixe.py --modo $modo --dados /content/prompts.jsonl --saida /content/$modo.json --vllm-mem $VLLM_MEM 2>&1 | tail -60" \
    | tee "$SAIDA/$modo.txt"
  colab download -s "$SESSAO" "/content/$modo.json" "$SAIDA/$modo.json" || log "sem relatório de $modo"
  colab usage | tee -a "$SAIDA/usage-por-montagem.txt"
done
log "fim"
