# Objetivo do projeto

O laboratório ensina o Gemma 4 E4B-it, em modo texto, a triar logs heterogêneos de SOC em JSON
estrito, e sustenta um único artigo. Ele tem duas partes, sobre os mesmos dados curados:

- **Estudo de ablação (contrato v1).** Separa os efeitos da quantização, dos alvos LoRA, da
  loss apenas na resposta (`mask_prompt`) e do rank `r`, com LoRA BF16 e QLoRA 4-bit.
- **Guardião (contrato v2).** Agente que lê um Recorte, consulta logs locais com Ferramentas de
  leitura e emite um único Relato. Ele relata e nunca age. É treinado por SFT e depois por RL,
  com recompensa que pesa o custo de errar contra o custo de investigar. Roda na máquina
  monitorada e envia ao SOC só a Remessa.

O resultado principal do artigo é a Carga no analista, junto com auditabilidade, supervisão
humana e governança dos dados na origem. Os malicious perdidos são uma restrição em toda medida.
A meta de engenharia é rodar o Guardião na máquina monitorada com o E4B, com o E2B como plano B
de latência.

Use os termos do [GLOSSARY.md](GLOSSARY.md). Antes de mudar dados, contrato, treino, recompensa
ou runtime do Guardião, leia os ADRs em [docs/adr/](docs/adr/) e o desenho em
[docs/arquitetura/01-runtime-agentico.md](docs/arquitetura/01-runtime-agentico.md).

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

O schema oficial do contrato v1 está em [schema.py](src/soc_triage/schema.py) e o prompt
versionado em [prompts.py](src/soc_triage/prompts.py). O contrato v2 está definido no
[ADR 0001](docs/adr/0001-guardiao-contrato-v2-sobre-recortes.md) e ainda não tem código.
Preserve os campos e enums de cada contrato. Quando uma mudança contratual for aprovada,
atualize na mesma alteração os testes, o prompt, o script de curadoria e a versão dos datasets
processados.

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
  Ambientes de RL e de avaliação seguem os splits da v12 ([ADR 0007](docs/adr/0007-ambiente-ait-segue-os-splits-da-v12.md)).
- Mutações e Exemplos sintéticos ficam fora do Teste real. Os do opensec-triage entram no
  treino com teto de um para um, aprovados por Família, e a seleção usa só a validação real
  ([ADR 0002](docs/adr/0002-opensec-por-familia-e-teste-real.md)).
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
- O Mac roda o SFT, o Ambiente de treino, as recompensas, os Comparadores e o piloto de RL
  de turno único. O RL com várias chamadas de ferramenta por episódio roda no Google Colab
  AI Pro com L4, usando TRL e vLLM ([ADR 0005](docs/adr/0005-rl-com-custo-multiplicativo.md)).
  Mantenha scripts, notebooks e dependências do Colab em `colab/`. Exclua `bitsandbytes`,
  `unsloth` e CUDA do projeto principal. Unidades de computação além do plano são gasto e
  exigem aprovação do responsável.
- Mantenha logs reais confidenciais, credenciais, pesos, adaptadores, arquivos
  `.safetensors`, `.gguf` e dumps grandes fora do Git. A chave de assinatura da Liberação e
  os dados do Estudo com analistas também ficam fora do Git e do wiki.

## Métricas de sucesso

- **Pydantic Pass Rate ≥ 98%** sobre todas as respostas, exigindo JSON puro e schema válido.
- **IoC Hallucination Rate < 1%** por candidato verificado, com busca literal e
  insensível a maiúsculas. Reporte a cobertura de respostas válidas.
- **Qualidade de triagem** com Macro-F1 para os quatro vereditos e FPR no conjunto
  `benign`/`expected_admin`. Um alerta `malicious`/`suspicious` nesse conjunto é falso positivo.
  Registre como respostas inválidas entram nas métricas de triagem antes de comparar rodadas.
- **Rival e Comparadores.** No Teste real, o Guardião precisa superar o Rival: Macro-F1 maior,
  FPR igual ou menor e não mais malicious perdidos. Com o mesmo custo de investigação, o
  Guardião treinado por RL precisa superar os Comparadores do ADR 0005.
- **Carga no analista, auditabilidade e governança** com as métricas da seção "Métricas" do
  desenho do runtime. Afirme carga cognitiva só com o Estudo com analistas aprovado pelo CEP
  ([ADR 0006](docs/adr/0006-nenhum-relato-fecha-sozinho.md)).
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
