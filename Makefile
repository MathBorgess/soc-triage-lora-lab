.DEFAULT_GOAL := help

UV_RUN := uv run --locked
CONFIG ?= configs/mlx/run1_qlora_attn.yaml
PORT ?= 8080
TRAIN_TARGETS := train-run1 train-run2 train-run3 train-run4-r8 train-run4-r64

.PHONY: help setup check-mlx lint test inspect-tokens serve-adapter $(TRAIN_TARGETS)

help:
	@printf '%s\n' 'setup check-mlx lint test inspect-tokens' '$(TRAIN_TARGETS) serve-adapter'

setup:
	uv sync --locked

check-mlx:
	$(UV_RUN) python -c 'import mlx.core as mx; assert mx.metal.is_available(); print(mx.default_device())'
	$(UV_RUN) mlx_lm.lora --help

lint:
	$(UV_RUN) ruff check .

test:
	$(UV_RUN) pytest -v

inspect-tokens:
	$(UV_RUN) python scripts/02_inspect_tokens.py --config "$(CONFIG)"

train-run1: PRESET := run1_qlora_attn
train-run2: PRESET := run2_qlora_all_linear
train-run3: PRESET := run3_lora_bf16
train-run4-r8: PRESET := run4_qlora_r8
train-run4-r64: PRESET := run4_qlora_r64

$(TRAIN_TARGETS):
	$(UV_RUN) python scripts/02_inspect_tokens.py --config "configs/mlx/$(PRESET).yaml"
	mkdir "adapters/$(PRESET)"
	$(UV_RUN) mlx_lm.lora --config "configs/mlx/$(PRESET).yaml"

serve-adapter:
	@test -n "$(MODEL)" && test -n "$(ADAPTER_PATH)" || { \
		printf '%s\n' 'Informe MODEL e ADAPTER_PATH.'; exit 2; }
	@test -f "$(ADAPTER_PATH)/adapters.safetensors" || { \
		printf '%s\n' 'Arquivo adapters.safetensors ausente em ADAPTER_PATH.'; exit 2; }
	$(UV_RUN) mlx_lm.server --host 127.0.0.1 --port "$(PORT)" \
		--model "$(MODEL)" --adapter-path "$(ADAPTER_PATH)"
