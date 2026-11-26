# SOC Triage LoRA Lab

Laboratório de fine-tuning com **Gemma 4 E4B-it em modo texto** para normalizar logs de SOC e
atribuir veredito e severidade em JSON estrito. O [AGENTS.md](AGENTS.md) define a
matriz de ablação, o contrato de dados e os critérios do estudo.

## Fases

| Fase | Entrega | Estado |
| --- | --- | --- |
| 1. Ambiente e Git | Python isolado por `uv`, MLX/Metal, `main` e exclusões de dados e pesos | Bootstrap validado no Apple Silicon |
| 2. Scaffold | Schema Pydantic, prompt versionado, métricas, presets MLX e inspeção de tokens | Código disponível |
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

Esses comandos usam apenas dependências Python. Os testes usam um Gemma 4
sintético com blocos de KV compartilhado para conferir a correspondência entre
alvos PiSSA e adaptadores nativos do MLX. A inspeção dos splits com o tokenizer
oficial, a carga do checkpoint completo e o pico de RAM ainda aguardam medição.

## Inicialização PiSSA

Os sete presets declaram `init_lora_weights: pissa`. A preparação do projeto
decompõe cada projeção-alvo da base original com SVD e separa um adaptador
inicial e uma base residual. Nas variantes 4-bit, a quantização affine com
grupos de 64 é aplicada ao residual. As combinações com DoRA são
experimentais e inicializam as magnitudes a partir dos pesos reconstruídos.
Os presets preservam `dropout: 0.05`. A recomendação dos autores de PiSSA
é dropout zero. Com dropout ativo, a reconstrução inicial vale em avaliação,
sem a máscara estocástica do treino.
[Artigo PiSSA](https://arxiv.org/abs/2404.02948) ·
[Implementação de referência](https://github.com/MuLabPKU/PiSSA#advanced-usage)

Com a revisão BF16 de google/gemma-4-E4B-it indicada no YAML disponível em disco, prepare
somente o preset a ser executado. A preparação local usa o checkpoint
não quantizado, inclusive para as variantes 4-bit.

```sh
make prepare-pissa CONFIG=configs/mlx/run2_qlora_all_linear.yaml \
    PISSA_BASE=/caminho/local/do/gemma-original PISSA_REVISION=sha-da-revisao
```

O resultado fica em `models/pissa/gemma-4-e4b-it/<preset>/` e inclui `base/`,
`init.safetensors` e a revisão de origem. O MLX carrega esse par com
`model` e `resume_adapter_file`. Para servir o adaptador treinado, use
`MODEL=models/pissa/gemma-4-e4b-it/<preset>/base` com o diretório do adaptador.
O backend `gemma4` do MLX usa o ramo de texto e filtra os encoders durante a
carga. A base residual inclui o template Gemma com `enable_thinking=false`.
Use o mesmo modo no Run 0 via
`mlx_lm.server --chat-template-args '{"enable_thinking":false}'`.
SVD e memória de pico do 8B ainda precisam ser medidos.

## Curadoria e pré-treino

A fonte, os rótulos, os grupos de incidentes e os splits são decisões do responsável
pelo estudo. [01_curate_dataset.py](scripts/01_curate_dataset.py) recebe um
manifesto JSON com `train`, `valid` e `test`. Cada split aceita uma fonte ou
uma lista de fontes. Cada fonte indica `group`, `records` (JSONL curado) e
`archive` (arquivo original). Os caminhos são relativos ao manifesto.
O campo `evidence_format` aceita `zip` (padrão), `tar`, `sqlite_events`,
`text` e `csv_records`. No SQLite, o localizador usa o membro `events` e os
IDs originais em `lines`. Em CSV, `lines` usa a posição do registro lógico
após o cabeçalho, começando em 1. Em arquivos com os registros mais recentes primeiro, declare
`reverse_lines: true` na entrada da fonte. Os campos opcionais `dataset`,
`incident` (ID global do incidente) e `anchor_line` entram no CSV de revisão.
O script confere
schema, IoCs, localizadores, duplicatas e isolamento por grupo, arquivo e
incidente identificado. O treino exige veredito humano aprovado. Para exportar
uma versão com todos os splits adjudicados, use `--require-approved`.
[03_evaluate.py](scripts/03_evaluate.py) avalia o Run 0 e os adaptadores treinados (veja [Execução das rodadas](#execução-das-rodadas)).

Cada linha dos splits é produzida por `build_chat_record` e contém mensagens de
`system`, `user` e `assistant`, com o recorte do log em `user` e o JSON-alvo em
`assistant`. Quando os três splits estiverem curados, use o tokenizer da rodada.

```sh
make inspect-tokens CONFIG=configs/mlx/run2_qlora_all_linear.yaml
uv run python scripts/02_inspect_tokens.py --config configs/mlx/run2_qlora_all_linear.yaml \
    --tokenizer /caminho/do/tokenizer
```

O inspetor usa o chat template e o limite do preset. Ele procura o tokenizer
localmente ou no cache. A opção `--allow-tokenizer-download` permite buscar só os
arquivos do tokenizer. Para usar a revisão fixada via Hub, indique
`--tokenizer google/gemma-4-E4B-it --tokenizer-revision <sha-do-preset>`.
O treino deve aguardar a revisão do histograma e zero truncamentos. Os presets
apontam para a v12 (`data/processed/soc-triage-v12/splits`). Cada rodada registra o hash dos três splits em `runs/`.

Após aprovação, os alvos de treino verificam o par PiSSA e inspecionam os
tokens antes do treino. Cada alvo usa o diretório de
adaptador do preset e para se ele já existir. Para repetir uma rodada, registre a
configuração efetiva e escolha um novo diretório. Registre os resultados em
`runs/` com um identificador exclusivo. Para servir um adaptador concluído
localmente, use `make serve-adapter MODEL=<modelo> ADAPTER_PATH=<diretório>`.

### Piloto de curadoria

O [AIT-LDS V2.1](https://zenodo.org/records/19483937) reúne atividade de fundo e
incidentes simulados nos mesmos ambientes. Os rótulos do estudo referenciam
arquivo e linha, o que permite verificar a evidência no evento original. O piloto
usa autenticação Linux e Apache. Russellmitchell fica no treino, Santos na
validação e Harrison no teste.
A licença declarada é CC BY-NC-SA 4.0. O piloto tem escopo de pesquisa não comercial.

Use o testbed como um grupo de desenvolvimento. Preserve arquivo e linha de
origem, grupo, evidência e decisão de revisão em um manifesto local. Uma linha
sem rótulo de ataque é uma candidata à revisão. Marque como `expected_admin`
quando houver evidência de atividade administrativa esperada. Quando o input
sustentar um alerta concreto sem confirmação, use `suspicious`. Se o veredito
depender de informação ausente do input, encaminhe o caso para revisão.

Para uma nova fonte, confira formato real, licença, procedência, qualidade dos
rótulos, diversidade de operações e a unidade de incidente. Separe primeiro
grupos inteiros e amostre os exemplos dentro de cada split. Mantenha capturas
relacionadas, cópias e janelas sobrepostas juntas. Reserve o teste para a
avaliação final. Use a mesma versão do dataset em todas as comparações de
adaptadores. Ao medir o ganho sobre zero-shot, use o baseline da mesma base.

As [reservas para avaliação](configs/datasets/reservas-avaliacao.yaml)
fixam CSE-CIC na validação e EchoLake e Organização Y no teste. Use os IDs
de grupo reservados no manifesto após a curadoria desses recortes.

### Ampliação por incidentes

Após aprovar uma fonte, normalize seus metadados locais para a interface de
[05_propose_dataset.py](scripts/05_propose_dataset.py). O `--help` lista os
campos e sinais aceitos. Use IDs globais de incidente, data e hora com fuso
e localizadores de origem. A fila alterna grupos e incidentes, prioriza
`linux_auth` malicioso e negativos difíceis e encaminha evidência
insuficiente para `precisa_contexto`. O CSV contém rótulos propostos e
uma coluna vazia para a decisão humana.

```sh
uv run --locked python scripts/05_propose_dataset.py --input candidatos.jsonl \
    --output-dir data/processed/revisao-lote-01 --limit 200
uv run --locked python scripts/06_audit_dataset.py \
    --input data/processed/piloto-ait-v2/splits/revisao.csv --target-train 2000
```

Na revisão, confira cada referência e se os sinais se aplicam à âncora.
Registre o alvo no JSONL curado após a aprovação. A
[auditoria de cobertura](scripts/06_audit_dataset.py) conta os aprovados
por fonte, veredito e grupos, indica a falta de `linux_auth` malicioso e
mede o avanço da meta de 2.000 exemplos de treino.

Os [registros de curadoria](docs/curadoria/01-evidencia-e-vies.md) documentam
decisões de rotulagem e controles de viés. A coleta foi pausada após o [marco de 1.000
registros para revisão](docs/curadoria/08-marco-de-1000-e-proximos-passos.md).
O marco reúne 415 exemplos aprovados e 639 propostas. O mesmo registro indica
os próximos passos de análise e coleta.

Para consolidar propostas revisáveis de várias fontes, use
[07_merge_review_queue.py](scripts/07_merge_review_queue.py). Passe um
`--source` por JSON de origem e o CSV da versão atual em `--reference`.
O relatório usa 500 como meta do primeiro piloto e conta somente
`human_verdict` de treino como aprovado. O CSV conserva os localizadores
e evita misturar propostas com grupos ou incidentes reservados.

## Execução das rodadas

Todas as rodadas usam a v12 (1.147 / 177 / 166 exemplos), o prompt `v1` e o template do Gemma com
`enable_thinking=false`. A validação serve para depurar e escolher o ponto de parada. O **teste só
roda uma vez por rodada, no fim** (`SPLIT=test`). Cada execução grava um diretório exclusivo em `runs/`
(fora do Git) com a configuração efetiva, os hashes dos dados e dos pesos, as versões da stack e as métricas.

1. **Confira o prompt.** `make check-prompt` verifica, só com o tokenizer, que o prompt de geração
   é o prefixo exato do que o treino mascara (0 divergências nos 177 exemplos da validação).
2. **Run 0 (zero-shot).** `make eval-run0` avalia o Gemma BF16 na validação e grava
   `runs/run0-valid-<data>/`. Gera com temperatura 0 e `max_tokens` 512 (o maior alvo tem 289 tokens).
   Cada resposta é validada como JSON puro no schema Pydantic e os IoCs são buscados no log bruto.
3. **Prepare o PiSSA** do preset (`make prepare-pissa`, seção acima). É o passo mais pesado: carrega
   o checkpoint BF16 de 16 GB e faz SVD das projeções-alvo.
4. **Treino curto.** `make smoke RUN_ID=smoke-run2 CONFIG=configs/mlx/run2_qlora_all_linear.yaml`
   treina 20 iterações (`SMOKE_ITERS`) e mede pico de RAM e tokens/s. Confirme o pico abaixo de ~24 GB
   antes da rodada completa; no Run 3 (BF16) isso ainda não foi medido.
5. **Rodada completa.** `make train-run2` (ou o alvo do preset). O treinador
   [08_train.py](scripts/08_train.py) roda o `mlx_lm.lora` no mesmo processo e grava `treino-metricas.jsonl`
   (losses, tokens/s, pico de memória) e `treino-resumo.json`.
6. **Avalie o adaptador.** `make eval-adapter RUN_ID=run2-valid CONFIG=configs/mlx/run2_qlora_all_linear.yaml`.

Métricas de `metricas.json`, com o `ioc_hallucination_rate` agregado por candidato verificado:
`pydantic_pass_rate` (meta ≥ 98%), `ioc_hallucination_rate` (meta < 1%, com cobertura de respostas
válidas), `triage_strict` e `triage_valid_only` (Macro-F1 nos quatro vereditos e FPR em
`benign`/`expected_admin`) e o detalhamento por modalidade. Em `triage_strict`, uma resposta inválida
conta como erro de triagem e não como falso positivo. `triage_valid_only` descarta as inválidas e
deve ser lido junto da cobertura. A validação e o teste têm poucos exemplos por célula
(veja [docs/curadoria/10-distribuicao-de-splits.md](docs/curadoria/10-distribuicao-de-splits.md)),
então Macro-F1 por modalidade tem intervalos largos.

O treino usa `mlx_lm.lora` 0.32.2, cuja função `run` descarta o callback recebido. Por isso o
`08_train.py` repete os passos dela. Reavalie esse trecho ao atualizar o `mlx-lm`.

## Como interpretar a matriz

- **Alvos e rank.** Use Run 2 como referência. Run 1 usa `q_proj` e `v_proj`
  onde esta última existe. O Gemma 4 E4B tem 18 blocos com KV compartilhado entre
  os 42 blocos. O Run 2 usa as projeções de atenção e MLP existentes e mantém
  congeladas as projeções dos embeddings por camada. Run 4 usa os mesmos
  alvos do Run 2 e varia a capacidade.
  Com PiSSA, qualquer alteração dos alvos ou do rank também muda os componentes
  removidos da base residual.
  O MLX multiplica a atualização LoRA diretamente por `scale`. Os ranks 8 e 64
  correspondem a alpha 16 e 128 na convenção `scale = alpha / r`.
  [Implementação LoRA do MLX LM](https://github.com/ml-explore/mlx-lm/blob/v0.32.2/mlx_lm/tuner/lora.py)
- **Quantização.** Run 2 usa base 4-bit e Run 3 usa base BF16. Nos presets atuais,
  os 4-bit usam microbatch 1, acumulação de 16 e 2.000 microsteps (o microbatch 4 não cabe
  na GPU de 26,8 GB). O Run 3 usa microbatch 2, acumulação de 4 e 500 microsteps. Ambos rendem
  125 atualizações, com 16 exemplos por atualização no Run 2 e 8 no Run 3. O Run 3 também usa gradient checkpointing,
  o que afeta tempo e memória. Para isolar quantização em uma comparação aprovada,
  controle a linhagem dos pesos, os microbatches, a acumulação, a ordem dos dados
  e o checkpointing. Fixe as revisões e o tokenizer antes de coletar resultados.
  [Treinador do MLX LM](https://github.com/ml-explore/mlx-lm/blob/v0.32.2/mlx_lm/tuner/trainer.py)
- **Loss e baseline.** Todos os presets treinam com `mask_prompt: true`. Medir o efeito
  da máscara requer uma rodada pareada com `mask_prompt: false`. Run 0 avalia o
  Gemma 4 E4B-it zero-shot no mesmo hold-out e com o mesmo prompt e parâmetros de
  geração. O baseline quantizado é um controle possível para medir a adaptação sobre
  a mesma base 4-bit, sujeito à aprovação do desenho.
- **DoRA e QDoRA.** A extensão exploratória da matriz usa os presets
  [DoRA BF16](configs/mlx/run5_dora_bf16.yaml) e [QDoRA 4-bit](configs/mlx/run5_qdora_4bit.yaml).
  DoRA adapta magnitude e direção dos pesos. No MLX, ambos usam
  `fine_tune_type: dora`. A versão quantizada usa o checkpoint base de 4 bits.
  Compare DoRA com Run 3 e QDoRA com Run 2 para medir a troca de adaptador com
  os demais controles do respectivo preset fixos. A comparação entre os dois
  presets DoRA ainda inclui diferenças de lote e checkpointing. O QDoRA
  dequantiza as projeções adaptadas no forward e calcula a norma com uma
  matriz densa. O pico de memória com pesos 8B ainda precisa ser medido.
  Após aprovação do dataset e do treino, os alvos `train-run5-dora` e `train-run5-qdora`
  executam a inspeção de tokens antes do CLI de treino.
  [Artigo DoRA](https://arxiv.org/abs/2402.09353) ·
  [Implementação no MLX LM](https://github.com/ml-explore/mlx-lm/blob/v0.32.2/mlx_lm/tuner/dora.py)
