#!/usr/bin/env bash
# Roda o teste de encaixe numa sessão nova do Colab e sempre encerra a VM no fim.
# Uso: colab/01_rodar_encaixe.sh <GPU> <prompts.jsonl> <pasta-de-saida> [vllm_mem]
# Variáveis opcionais: MODOS (lista), REQUISITOS (arquivo em colab/), PRECISAO (bf16 ou fp16),
# HIGH_MEM (1 pede a VM com RAM alta) e MAX_CONSULTAS (consultas de 30 s por montagem).
# Exemplo A100: colab/01_rodar_encaixe.sh A100 runs/<execucao>/prompts.jsonl runs/<execucao>/a100 0.5
# Exemplo T4: MODOS=4bit-hf REQUISITOS=requirements-t4.txt PRECISAO=fp16 \
#   colab/01_rodar_encaixe.sh T4 runs/<execucao>/prompts.jsonl runs/<execucao>/t4
set -uo pipefail

GPU="$1"
PROMPTS="$2"
SAIDA="$3"
VLLM_MEM="${4:-0.5}"
MODOS="${MODOS:-bf16-vllm 4bit-vllm bf16-hf}"
REQUISITOS="${REQUISITOS:-requirements-encaixe.txt}"
PRECISAO="${PRECISAO:-bf16}"
HIGH_MEM="${HIGH_MEM:-0}"
MAX_CONSULTAS="${MAX_CONSULTAS:-60}"
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
FORMATO=()
[ "$HIGH_MEM" = "1" ] && FORMATO=(--high-mem)
if ! timeout 600 colab new -s "$SESSAO" --gpu "$GPU" "${FORMATO[@]}"; then
  log "falha ao alocar $GPU"
  colab sessions | tee "$SAIDA/sessoes-depois.txt"
  exit 2
fi
trap encerrar EXIT
trap 'exit 143' TERM INT

colab usage | tee "$SAIDA/usage-com-vm.txt"
colab upload -s "$SESSAO" "$AQUI/00_teste_de_encaixe.py" /content/00_teste_de_encaixe.py
colab upload -s "$SESSAO" "$AQUI/$REQUISITOS" /content/requirements.txt
colab upload -s "$SESSAO" "$PROMPTS" /content/prompts.jsonl

executar() { echo "$1" | colab exec -s "$SESSAO" --timeout 1500; }

log "instalando dependências"
executar '!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv && pip install -q -r /content/requirements.txt 2>&1 | tail -5 && pip list 2>/dev/null | grep -E "^(torch|vllm|trl|transformers|peft|bitsandbytes) "' \
  | tee "$SAIDA/instalacao.txt"

log "baixando o modelo"
executar "!python -c \"from huggingface_hub import snapshot_download as s; print(s('$MODELO', revision='$REVISAO'))\"" \
  | tee "$SAIDA/download.txt"

# O treino roda em segundo plano na VM. Uma conexão sem saída por alguns minutos cai, então o
# script consulta o progresso a cada 30 s em vez de esperar o fim de um único exec.
for modo in $MODOS; do
  log "montagem $modo"
  executar "!nohup python /content/00_teste_de_encaixe.py --modo $modo --dados /content/prompts.jsonl --saida /content/$modo.json --vllm-mem $VLLM_MEM --precisao $PRECISAO > /content/$modo.log 2>&1 &"
  falhas=0
  for _ in $(seq 1 "$MAX_CONSULTAS"); do
    sleep 30
    if ! estado=$(executar "!test -f /content/$modo.json && echo PRONTO; pgrep -f '[0]0_teste_de_encaixe' > /dev/null || echo PARADO; free -m | sed -n 2p; nvidia-smi --query-gpu=memory.used --format=csv,noheader; tail -n 2 /content/$modo.log" 2>&1); then
      falhas=$((falhas + 1))
      log "consulta falhou ($falhas)"
      [ "$falhas" -ge 3 ] && break
      continue
    fi
    falhas=0
    printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$(echo "$estado" | tr '\n' ' ' | cut -c1-400)" | tee -a "$SAIDA/$modo-progresso.txt"
    case "$estado" in *PRONTO* | *PARADO*) break ;; esac
  done
  colab download -s "$SESSAO" "/content/$modo.json" "$SAIDA/$modo.json" || log "sem relatório de $modo"
  colab download -s "$SESSAO" "/content/$modo.log" "$SAIDA/$modo.log" || log "sem log de $modo"
  colab usage | tee -a "$SAIDA/usage-por-montagem.txt"
done
log "fim"
