# SOC Triage LoRA Lab

Laboratório de fine-tuning com **Qwen2.5-7B-Instruct** para normalizar logs de SOC e
atribuir veredito e severidade em JSON estrito. O [AGENTS.md](AGENTS.md) define a
matriz de ablação, o contrato de dados e os critérios do estudo.

## Fases

| Fase | Entrega | Estado |
| --- | --- | --- |
| 1. Ambiente e Git | Python isolado por `uv`, MLX/Metal, `main` e exclusões de dados e pesos | Bootstrap validado no Apple Silicon |
| 2. Scaffold | Schema Pydantic, prompt versionado, métricas, cinco presets MLX e inspeção de tokens | Código disponível |
| 3. Protocolo | Matriz, regras de curadoria, prevenção de vazamento e metodologia | Registrado em [AGENTS.md](AGENTS.md) |
| 4. Validação | Metal, CLI LoRA, compatibilidade YAML, Ruff e pytest | Executada no bootstrap |
| Sprint de dados e ablação | Curadoria, baseline, treinamento e avaliação | Depende da curadoria e aprovação do responsável |

## Validação local

Use macOS Apple Silicon, Python 3.12 e `uv`. O projeto aceita Python >=3.11 e <3.13.
O [lockfile](uv.lock) fixa o ambiente. `mlx-lm[train]` fornece o treinador oficial
`mlx_lm.lora`, usado por todos os presets. O pacote independente
[`mlx-lm-lora`](https://github.com/Goekdeniz-Guelmez/mlx-lm-lora) é instalado no grupo
`mlx-lora-extension` junto do ambiente padrão.

```sh
make setup
make check-mlx
make lint
make test
```

Esses comandos usam apenas dependências Python. A validação dos presets executou a
leitura dos YAMLs pelo CLI e aplicou as projeções em um Qwen2 sintético de dois blocos,
sem carregar os pesos 7B. A carga completa e o pico de RAM em treino ainda precisam
ser medidos.

## Curadoria e pré-treino

O [lote 12 de curadoria](docs/curadoria/lote-12/README.md) registra o marco de 1.000
registros para revisão, com o índice público das propostas e um roteiro para adjudicação.

A fonte, os rótulos, os grupos de incidentes e os splits são decisões do responsável
pelo estudo. Os scripts [01_curate_dataset.py](scripts/01_curate_dataset.py) e
[03_evaluate.py](scripts/03_evaluate.py) expõem interfaces CLI (`--help`) para a sprint
seguinte. A curadoria e as chamadas de avaliação ainda precisam ser implementadas.

Cada linha dos splits é produzida por `build_chat_record` e contém mensagens de
`system`, `user` e `assistant`, com o log bruto em `user` e o JSON-alvo em
`assistant`. Quando os três splits estiverem curados, use o tokenizer da rodada.

```sh
make inspect-tokens CONFIG=configs/mlx/run2_qlora_all_linear.yaml
uv run python scripts/02_inspect_tokens.py --config configs/mlx/run2_qlora_all_linear.yaml \
    --tokenizer /caminho/do/tokenizer
```

O inspetor usa o chat template e o limite do preset. Ele procura o tokenizer
localmente ou no cache. A opção `--allow-tokenizer-download` permite buscar só os
arquivos do tokenizer. O treino deve aguardar a revisão do histograma e zero
truncamentos.

Após aprovação, os alvos `train-run1`, `train-run2`, `train-run3`, `train-run4-r8` e
`train-run4-r64` rodam a inspeção antes do treino. Cada alvo usa o diretório de
adaptador do preset e para se ele já existir. Para repetir uma rodada, registre a
configuração efetiva e escolha um novo diretório. Registre os resultados em
`runs/` com um identificador exclusivo. Para servir um adaptador concluído
localmente, use `make serve-adapter MODEL=<modelo> ADAPTER_PATH=<diretório>`.

## Como interpretar a matriz

- **Alvos e rank.** Use Run 2 como referência. Run 1 troca as sete projeções por
  `q_proj` e `v_proj`. Run 4 usa os mesmos alvos do Run 2 e varia a capacidade.
  O MLX multiplica a atualização LoRA diretamente por `scale`. Os ranks 8 e 64
  correspondem a alpha 16 e 128 na convenção `scale = alpha / r`.
  [Implementação LoRA do MLX LM](https://github.com/ml-explore/mlx-lm/blob/v0.32.2/mlx_lm/tuner/lora.py)
- **Quantização.** Run 2 usa base 4-bit e Run 3 usa base BF16. Nos presets atuais,
  500 microsteps com acumulação de 4 rendem 125 atualizações, com 16 exemplos por
  atualização no Run 2 e 8 no Run 3. O Run 3 também usa gradient checkpointing,
  o que afeta tempo e memória. Para isolar quantização em uma comparação aprovada,
  controle a linhagem dos pesos, os microbatches, a acumulação, a ordem dos dados
  e o checkpointing. Fixe as revisões e o tokenizer antes de coletar resultados.
  [Treinador do MLX LM](https://github.com/ml-explore/mlx-lm/blob/v0.32.2/mlx_lm/tuner/trainer.py)
- **Loss e baseline.** Todos os presets treinam com `mask_prompt: true`. Medir o efeito
  da máscara requer uma rodada pareada com `mask_prompt: false`. Run 0 avalia o
  Qwen2.5-7B-Instruct zero-shot no mesmo hold-out e com o mesmo prompt e parâmetros de
  geração. O baseline quantizado é um controle possível para medir a adaptação sobre
  a mesma base 4-bit, sujeito à aprovação do desenho.
