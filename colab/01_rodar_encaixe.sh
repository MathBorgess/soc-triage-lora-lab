#!/usr/bin/env bash
# Roda o teste de encaixe numa sessão nova do Colab e sempre encerra a VM no fim.
# Uso: colab/01_rodar_encaixe.sh <GPU> <prompts.jsonl> <pasta-de-saida> [vllm_mem]
# Variáveis opcionais: MODOS (lista), REQUISITOS (arquivo em colab/), PRECISAO (bf16 ou fp16),
# HIGH_MEM (1 pede a VM com RAM alta), MAX_CONSULTAS (consultas de 60 s) e EXTRA (argumentos
# repassados ao teste, como "--prompts-por-passo 2").
# Exemplo A100: colab/01_rodar_encaixe.sh A100 runs/<execucao>/prompts.jsonl runs/<execucao>/a100 0.5
# Exemplo T4: MODOS=4bit-hf REQUISITOS=requirements-t4.txt PRECISAO=fp16 \
#   colab/01_rodar_encaixe.sh T4 runs/<execucao>/prompts.jsonl runs/<execucao>/t4
#
# Execuções longas pelo `colab exec` perdem a conexão. Por isso todo o trabalho roda na VM,
# desacoplado (02_encaixe_na_vm.sh), e este script só faz consultas curtas.
set -uo pipefail

GPU="$1"
PROMPTS="$2"
SAIDA="$3"
VLLM_MEM="${4:-0.5}"
MODOS="${MODOS:-bf16-vllm 4bit-vllm bf16-hf}"
REQUISITOS="${REQUISITOS:-requirements-encaixe.txt}"
PRECISAO="${PRECISAO:-bf16}"
HIGH_MEM="${HIGH_MEM:-0}"
MAX_CONSULTAS="${MAX_CONSULTAS:-75}"
EXTRA="${EXTRA:-}"
SESSAO="encaixe"
AQUI="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$SAIDA"
log() { printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }
# O timeout local cobre também uma conexão que trava sem cair.
executar() { echo "$1" | timeout 150 colab exec -s "$SESSAO" --timeout 120; }

baixar_resultados() {
  for arquivo in estado.txt gpu.txt instalacao.log download.log vm.log; do
    colab download -s "$SESSAO" "/content/$arquivo" "$SAIDA/$arquivo" > /dev/null 2>&1 \
      || log "sem $arquivo"
  done
  for modo in $MODOS; do
    for extensao in json log; do
      colab download -s "$SESSAO" "/content/$modo.$extensao" "$SAIDA/$modo.$extensao" \
        > /dev/null 2>&1 || log "sem $modo.$extensao"
    done
  done
}

encerrar() {
  log "baixando resultados"
  baixar_resultados
  log "encerrando a sessão $SESSAO"
  colab stop -s "$SESSAO" || true
  colab usage | tee "$SAIDA/usage-depois.txt"
  colab sessions | tee "$SAIDA/sessoes-depois.txt"
}

colab usage | tee "$SAIDA/usage-antes.txt"
log "alocando $GPU"
FORMATO=()
[ "$HIGH_MEM" = "1" ] && FORMATO=(--high-mem)
if ! timeout 600 colab new -s "$SESSAO" --gpu "$GPU" ${FORMATO[@]+"${FORMATO[@]}"}; then
  log "falha ao alocar $GPU"
  colab sessions | tee "$SAIDA/sessoes-depois.txt"
  exit 2
fi
trap encerrar EXIT
trap 'exit 143' TERM INT

colab usage | tee "$SAIDA/usage-com-vm.txt"
colab upload -s "$SESSAO" "$AQUI/00_teste_de_encaixe.py" /content/00_teste_de_encaixe.py
colab upload -s "$SESSAO" "$AQUI/02_encaixe_na_vm.sh" /content/02_encaixe_na_vm.sh
colab upload -s "$SESSAO" "$AQUI/$REQUISITOS" /content/requirements.txt
colab upload -s "$SESSAO" "$PROMPTS" /content/prompts.jsonl

# O disparo também pode perder a conexão. Confirma que o trabalho começou e tenta até 3 vezes;
# a trava em 02_encaixe_na_vm.sh impede que ele rode duas vezes.
iniciado=0
for tentativa in 1 2 3; do
  log "iniciando o trabalho desacoplado na VM (tentativa $tentativa)"
  executar "!setsid nohup bash /content/02_encaixe_na_vm.sh '$MODOS' $PRECISAO $VLLM_MEM '$EXTRA' > /content/vm.log 2>&1 < /dev/null &" \
    || log "o disparo perdeu a conexão"
  sleep 20
  if executar "!test -d /content/.iniciado && echo INICIADO" 2>&1 | grep -q INICIADO; then
    iniciado=1
    break
  fi
done
if [ "$iniciado" != "1" ]; then
  log "o trabalho não iniciou na VM"
  exit 3
fi

falhas=0
sem_estado=0
for _ in $(seq 1 "$MAX_CONSULTAS"); do
  sleep 60
  if ! estado=$(executar "!tail -n 2 /content/estado.txt; free -m | sed -n 2p; nvidia-smi --query-gpu=memory.used --format=csv,noheader" 2>&1); then
    falhas=$((falhas + 1))
    log "consulta falhou ($falhas)"
    [ "$falhas" -ge 5 ] && break
    continue
  fi
  falhas=0
  log "$(echo "$estado" | tr '\n' ' ' | cut -c1-300)" | tee -a "$SAIDA/progresso.txt"
  case "$estado" in
    *"No such file"*)
      sem_estado=$((sem_estado + 1))
      if [ "$sem_estado" -ge 3 ]; then
        log "sem andamento na VM; abortando"
        break
      fi
      ;;
    *) sem_estado=0 ;;
  esac
  case "$estado" in *FIM*) break ;; esac
done
log "fim das consultas"
