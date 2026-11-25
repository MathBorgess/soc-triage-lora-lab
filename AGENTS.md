# Objetivo do projeto

Conduzir um estudo experimental controlado de LoRA 16-bit (BF16) e QLoRA 4-bit para
normalização e triagem de logs heterogêneos de SOC em JSON estrito. A matriz inicial usa
Gemma 4 E4B-it em modo texto. A meta de engenharia é chegar a um modelo de 3B para uso local e
escalar a abordagem para 7B–8B em nuvem, com triagem confiável e baixa taxa de falsos
positivos. O objetivo do estudo é separar os efeitos da quantização, dos alvos LoRA,
da loss apenas na resposta (`mask_prompt`) e do rank `r`.

## Matriz de ablação oficial

| Rodada | Pesos base | Alvos por bloco | Rank | Loss |
| --- | --- | --- | --- | --- |
| Run 0 | Gemma 4 E4B-it, zero-shot em texto | Sem adaptador | — | — |
| Run 1 | 4-bit | `q_proj`, `v_proj` onde presente | 16 | Apenas resposta |
| Run 2 | 4-bit | `all-linear` | 16 | Apenas resposta |
| Run 3 | BF16 | `all-linear` | 16 | Apenas resposta |
| Run 4 | 4-bit | `all-linear` | 8 e 64 | Apenas resposta |

`all-linear` cobre as projeções de atenção e MLP declaradas nos presets.
Nos blocos com KV compartilhado do Gemma 4, os alvos `k_proj` e `v_proj`
ausentes são dispensados. Os embeddings e as projeções dos embeddings por
camada ficam congelados em todas as rodadas.
Use a revisão indicada nos presets e o template do Gemma com
`enable_thinking=false` na inspeção, no treino e na avaliação.
Use Run 2 como referência para Run 1 (alvos), Run 3 (quantização) e Run 4 (rank).
Mantenha `scale: 2.0` nas duas variantes de rank e `seed: 42` nas rodadas treinadas.

Os presets 2 e 3 têm microbatch e checkpointing diferentes. A comparação isolada da
quantização exige condições equivalentes de treino, mesma revisão de origem dos pesos e
mesmo pré-processamento. Todos os presets usam `mask_prompt: true`. Medir o efeito da
máscara exige um controle pareado com `mask_prompt: false`. O responsável pelo estudo
curará e aprovará os dados, os controles e as condições de treino antes da execução.

## Contrato de dados

O schema oficial está em [schema.py](src/soc_triage/schema.py) e o prompt versionado em
[prompts.py](src/soc_triage/prompts.py). Preserve os campos e enums do contrato.
Quando uma mudança contratual for aprovada, atualize na mesma alteração os testes,
o prompt, o script de curadoria e a versão dos datasets processados.

### Curadoria e prevenção de vazamento

- Referências candidatas incluem `alirezaaminzadeh/soc-alert-attack-dataset`,
  `tegridydev/opensec-triage`, `alirezaaminzadeh/socassist-alerts-synthetic`
  (hold-out/benchmark), `alirezaaminzadeh/soc-agent-traces-100k`,
  `k3nn3dy/blueteam-v8`, OTRF Mordor, EVTX-ATTACK-SAMPLES com `evtx-baseline`,
  AIT-LDS, Loghub e BOTES.
- Reúna pelo menos 500 exemplos de treino aprovados para o primeiro piloto.
  Para o estudo, almeje 2.000–3.000 exemplos limpos, com cerca de 45% maliciosos/suspeitos,
  45% benignos ou administrativos esperados e 10% truncados/ambíguos
  que exijam `null` nos campos ausentes. Use apenas rótulos sustentados pelo log.
- Divida por grupos de cenário, incidente ou origem de ataque. Mantenha todas as
  linhas do grupo no mesmo split e mantenha o hold-out fora do treino e da seleção
  de hiperparâmetros. Almeje 80/10/10 em `train.jsonl`, `valid.jsonl` e `test.jsonl`.
- Antes de gravar em `data/processed/`, valide 100% dos alvos com Pydantic e
  confira todos os IoCs, incluindo `src_ip` e `dst_ip`, contra o log bruto.
- Antes de qualquer treino, rode [02_inspect_tokens.py](scripts/02_inspect_tokens.py)
  com a configuração da rodada e o tokenizer correspondente. Exija zero truncamentos
  na janela de `max_seq_length` para preservar todo o JSON da resposta.

## Hardware e stack

- MacBook Pro M1 Max com 32 GB de memória unificada. Use `uv` e MLX LM sobre Metal.
  Almeje pico de RAM abaixo de aproximadamente 24 GB para evitar swap. Para BF16,
  o preset usa `grad_checkpoint: true` e microbatch menor. Confirme a viabilidade em
  relação ao teto antes de uma rodada completa.
- Google Colab AI Pro com T4/L4 é o ambiente previsto para PyTorch/PEFT/TRL/Unsloth.
  Mantenha scripts, notebooks e dependências dessa stack em `colab/` quando houver
  implementação aprovada. Exclua `bitsandbytes`, `unsloth` e CUDA do projeto principal.
- Mantenha logs reais confidenciais, credenciais, pesos, adaptadores, arquivos
  `.safetensors`, `.gguf` e dumps grandes fora do Git.

## Métricas de sucesso

- **Pydantic Pass Rate ≥ 98%** sobre todas as respostas, exigindo JSON puro e schema válido.
- **IoC Hallucination Rate < 1%** por candidato verificado, com busca literal e
  insensível a maiúsculas. Reporte a cobertura de respostas válidas.
- **Qualidade de triagem** com Macro-F1 para os quatro vereditos e FPR no conjunto
  `benign`/`expected_admin`. Um alerta `malicious`/`suspicious` nesse conjunto é falso positivo.
  Registre como respostas inválidas entram nas métricas de triagem antes de comparar rodadas.
- **Catastrophic forgetting** com perguntas gerais de cibersegurança fora do prompt
  JSON, comparando qualitativamente com o baseline.
- **Recursos** com pico de memória, tempo de treino e tokens/s de cada rodada. Use
  `eval_loss` para diagnóstico junto das métricas de qualidade e custo.

## Fluxo de trabalho

Rode `uv run ruff check .` e `uv run pytest` após mudanças em `src/` ou `tests/`.
Versione os presets em `configs/mlx/` e mantenha a seed fixa em `42`. Registre em
`runs/`, em diretórios exclusivos por execução, as métricas, a configuração efetiva,
as revisões dos pesos, tokenizer e dados, e as versões da stack. Preserve os resultados
das execuções anteriores.
