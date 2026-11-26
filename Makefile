SHELL := /bin/bash
.SHELLFLAGS := -eo pipefail -c
.DEFAULT_GOAL := help

UV_RUN := uv run --locked
CONFIG ?= configs/mlx/run1_qlora_attn.yaml
PORT ?= 8080
GEMMA ?= google/gemma-4-E4B-it
GEMMA_REVISION ?= 4ecc2ba63bcac23ba4a767fc87025b1450f84c9c
SPLIT ?= valid
STAMP := $(shell date +%Y%m%d-%H%M)
SMOKE_ITERS ?= 20
TRAIN_TARGETS := train-run1 train-run2 train-run3 train-run4-r8 train-run4-r64 \
                 train-run5-dora train-run5-qdora

.PHONY: help setup check-mlx lint test prepare-pissa inspect-tokens check-prompt \
        eval-run0 eval-adapter smoke serve-adapter reproduzir-v12 tipos-de-contexto reprojetar-v12 \
        $(TRAIN_TARGETS)

help:
	@printf '%s\n' 'setup check-mlx lint test prepare-pissa inspect-tokens check-prompt' \
		'eval-run0 smoke eval-adapter' '$(TRAIN_TARGETS) serve-adapter' \
		'reproduzir-v12 tipos-de-contexto reprojetar-v12'

setup:
	uv sync --locked

check-mlx:
	$(UV_RUN) python -c 'import mlx.core as mx; assert mx.metal.is_available(); print(mx.default_device())'
	$(UV_RUN) mlx_lm.lora --help

# Guardião: reprodução da v12 pelo Projetor e tipos de linha de Contexto (ADR 0009).
# RAIZ_DADOS é a pasta com data/raw e data/processed (padrão: a raiz do repositório).
RAIZ_DADOS ?= .

reproduzir-v12:
	$(UV_RUN) python scripts/09_reproduzir_v12.py --raiz-dados "$(RAIZ_DADOS)" \
		--relatorio docs/curadoria/11-reproducao-da-v12.md --tabela docs/curadoria/11-reproducao-da-v12.csv

tipos-de-contexto:
	$(UV_RUN) python scripts/10_tipos_de_contexto.py --raiz-dados "$(RAIZ_DADOS)" \
		--relatorio docs/curadoria/12-tipos-de-contexto-da-v12.md

# Reprojeção da v12 no formato canônico (ADR 0012). VERSAO_V2 é uma pasta nova em data/processed.
VERSAO_V2 ?= guardiao-v2-r01

reprojetar-v12:
	$(UV_RUN) python scripts/11_reprojetar_v12.py --raiz-dados "$(RAIZ_DADOS)" --versao "$(VERSAO_V2)" \
		--relatorio docs/curadoria/13-reprojecao-v2.md

lint:
	$(UV_RUN) ruff check .

test:
	$(UV_RUN) pytest -v

prepare-pissa:
	$(UV_RUN) python scripts/04_prepare_pissa.py --config "$(CONFIG)" \
		--base "$(PISSA_BASE)" --revision "$(PISSA_REVISION)"

inspect-tokens:
	$(UV_RUN) python scripts/02_inspect_tokens.py --config "$(CONFIG)"

# Confere que o prompt de geração é o prefixo exato do prompt do treino (só o tokenizer).
check-prompt:
	$(UV_RUN) python scripts/03_evaluate.py --run-id check --check-prompt \
		--model "$(GEMMA)" --revision "$(GEMMA_REVISION)"

# Run 0: Gemma zero-shot, sem adaptador. SPLIT=valid (padrão) ou SPLIT=test (avaliação final).
eval-run0:
	$(UV_RUN) python scripts/03_evaluate.py --run-id "$(or $(RUN_ID),run0-$(SPLIT)-$(STAMP))" \
		--model "$(GEMMA)" --revision "$(GEMMA_REVISION)" --split "$(SPLIT)"

# Rodada treinada: CONFIG é o preset; o adaptador vem do adapter_path dele.
eval-adapter:
	$(UV_RUN) python scripts/03_evaluate.py --run-id "$(RUN_ID)" --preset "$(CONFIG)" --split "$(SPLIT)"

# Treino curto (SMOKE_ITERS) para medir pico de RAM e tokens/s antes da rodada completa.
smoke:
	@test -n "$(RUN_ID)" || { printf '%s\n' 'Informe RUN_ID.'; exit 2; }
	$(UV_RUN) python scripts/04_prepare_pissa.py --check --config "$(CONFIG)"
	$(UV_RUN) python scripts/02_inspect_tokens.py --config "$(CONFIG)"
	$(UV_RUN) python scripts/08_train.py --config "$(CONFIG)" --run-id "$(RUN_ID)" \
		--iters "$(SMOKE_ITERS)" --steps-per-report 5 --steps-per-eval "$(SMOKE_ITERS)" \
		--val-batches 5 --save-every "$(SMOKE_ITERS)" --adapter-path "adapters/smoke-$(RUN_ID)"

train-run1: PRESET := run1_qlora_attn
train-run2: PRESET := run2_qlora_all_linear
train-run3: PRESET := run3_lora_bf16
train-run4-r8: PRESET := run4_qlora_r8
train-run4-r64: PRESET := run4_qlora_r64
train-run5-dora: PRESET := run5_dora_bf16
train-run5-qdora: PRESET := run5_qdora_4bit

$(TRAIN_TARGETS):
	$(UV_RUN) python scripts/04_prepare_pissa.py --check --config "configs/mlx/$(PRESET).yaml"
	$(UV_RUN) python scripts/02_inspect_tokens.py --config "configs/mlx/$(PRESET).yaml"
	$(UV_RUN) python scripts/08_train.py --config "configs/mlx/$(PRESET).yaml" \
		--run-id "$(or $(RUN_ID),$(PRESET)-$(STAMP))"

serve-adapter:
	@test -n "$(MODEL)" && test -n "$(ADAPTER_PATH)" || { \
		printf '%s\n' 'Informe MODEL e ADAPTER_PATH.'; exit 2; }
	@test -f "$(ADAPTER_PATH)/adapters.safetensors" || { \
		printf '%s\n' 'Arquivo adapters.safetensors ausente em ADAPTER_PATH.'; exit 2; }
	$(UV_RUN) python scripts/04_prepare_pissa.py --serve-model "$(MODEL)" \
		--config "$(ADAPTER_PATH)/adapter_config.json"
	$(UV_RUN) mlx_lm.server --host 127.0.0.1 --port "$(PORT)" \
		--model "$(MODEL)" --adapter-path "$(ADAPTER_PATH)"
