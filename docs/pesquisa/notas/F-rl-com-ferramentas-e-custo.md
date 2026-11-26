# Tema F — RL com ferramentas e recompensa sensível a custo

> **Nota de 25/11/2026:** esta pesquisa foi encomendada quando o desenho previa um segundo agente, o "Investigador". Pelo ADR 0004, quem investiga com Ferramentas de leitura é o próprio Guardião. Leia "Investigador" como "Guardião com ferramentas" e "SIEM simulado" como "Ambiente de treino".

- **Data da revisão:** 2026-11-25.
- **Executor:** subagente Claude Code (modelo Opus 5.5), por delegação. As fontes foram abertas com WebFetch nesta sessão. Não alterei nenhum repositório.
- **Leitura local (só leitura):** código instalado de `mlx-lm-lora 5.10.2` em `.venv` e logs em `runs/` do `soc-triage-lora-lab`, usados como âncoras de medida.
- **Lacuna de contexto:** não consultei a `mathai-wiki`. O contexto do projeto veio do pedido e do `AGENTS.md` do laboratório.
- **Convenções:**
  - **Status:** peer-reviewed, preprint ou documentação/blog.
  - **Verificado:** URL aberta nesta sessão. "NÃO VERIFICADO" quando não abri.
  - Tudo marcado **(inferência)** é minha leitura, não um resultado das fontes.

---

## 1. GRPO e variantes

### [F-1] Shao, Z.; Wang, P.; Zhu, Q. et al. (2024). DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models. arXiv. — [arXiv:2402.03300](https://arxiv.org/abs/2402.03300) · Preprint (sem venue no arXiv) · Verificado (abs + HTML v3)

**Contribuição**
- Introduz o GRPO, que dispensa o crítico do PPO. A linha de base vem da média das recompensas de um grupo de G saídas. A vantagem é (r − média)/desvio no grupo e se aplica a todos os tokens da saída.
- O KL entra direto na loss, com um estimador não enviesado e β = 0,04. A lr da política é 1e-6. O grupo tem 64 saídas por questão; o HTML renderiza "6464", provável erro de renderização.
- Resultado (Instruct → RL, 7B): GSM8K 82,9 → 88,2 e MATH 46,8 → 51,7. O RL melhora Maj@K mas não Pass@K. Os autores leem isso como o RL tornando a distribuição mais robusta, e não aumentando a capacidade de base.

**Relevância para o Investigador (inferência)**
- O achado Maj@K ≠ Pass@K sugere que o RL vai sobretudo afinar a calibração entre as 4 classes e o uso de ferramentas que o modelo SFT já consegue amostrar. Se o SFT nunca produz trajetórias com investigação útil, o GRPO não as inventa. Isso reforça o warm-start (ver F-2 e F-11).

### [F-2] Guo, D.; Yang, D.; Zhang, H. et al. (DeepSeek-AI) (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. *Nature* 645, 633–638. — [arXiv:2501.12948](https://arxiv.org/abs/2501.12948) · DOI 10.1038/s41586-025-09422-z · **Peer-reviewed (Nature)** · Verificado (journal-ref no arXiv + HTML v2; a página da Nature redirecionou para login)

**Contribuição**
- R1-Zero usa GRPO puro sobre o modelo base. Hiperparâmetros: lr 3e-6, KL 0,001, G = 16, temperatura 1. O modelo de referência é trocado a cada 400 passos.
- As recompensas são só regras: acurácia + formato. Os autores evitaram reward models neurais porque são suscetíveis a reward hacking em RL de larga escala.
- O R1-Zero teve legibilidade ruim e mistura de idiomas. O R1 corrige isso com cold-start SFT (alguns milhares de exemplos) e uma recompensa de consistência de idioma, que custa um pouco de desempenho. O comprimento das respostas cresce durante o RL.

**Relevância para o Investigador (inferência)**
- O Relato já tem verificadores determinísticos: Pydantic, checagem literal de Evidência e rótulo. Mantenha a recompensa 100% por regras. Não use LLM-juiz para "qualidade da investigação".
- O padrão "cold-start pequeno → RL" é o análogo direto de "adaptador SFT do Relato + poucas trajetórias agênticas → GRPO".

### [F-3] Yu, Q.; Zhang, Z.; Zhu, R. et al. (2025). DAPO: An Open-Source LLM Reinforcement Learning System at Scale. NeurIPS 2025 (Main Track). — [arXiv:2503.14476](https://arxiv.org/abs/2503.14476) · [anais NeurIPS](https://papers.nips.cc/paper_files/paper/2025/hash/a4277440d50f1f15d2cb4c14f7e0c0d2-Abstract-Conference.html) · **Peer-reviewed** · Verificado (abs, HTML v2, página dos anais)

**Contribuição**
- **Clip-Higher:** ε_low = 0,2 e ε_high = 0,28, contra o colapso de entropia observado com PPO/GRPO ingênuos.
- **Dynamic Sampling:** descarta grupos com acerto 0 ou 1, que têm vantagem nula, e reamostra até completar o batch.
- **Loss por token:** a média é feita no batch, não por amostra, para não diluir os tokens de respostas longas.
- **Overlong:** filtra amostras truncadas da loss ou aplica punição suave linear numa faixa de 4.096 tokens antes do limite.
- O KL foi removido. Configuração: Qwen2.5-32B, G = 16, 50 pontos no AIME 2024.

**Relevância para o Investigador (inferência)**
- Com 4 classes e um modelo SFT já bom, muitos grupos sairão "todos certos" e terão vantagem zero. O dynamic sampling (ou um filtro equivalente) é quase obrigatório para não desperdiçar geração cara.
- `loss_type="dapo"` já é o default do TRL (ver Infraestrutura).

### [F-4] Liu, Z.; Chen, C.; Li, W.; Qi, P.; Pang, T.; Du, C.; Lee, W. S.; Lin, M. (2025). Understanding R1-Zero-Like Training: A Critical Perspective. COLM 2025. — [arXiv:2503.20783](https://arxiv.org/abs/2503.20783) · **Peer-reviewed (COLM 2025, cabeçalho do PDF v2)** · Verificado (abs, HTML v2, PDF p.1)

**Contribuição**
- Identifica dois vieses do GRPO:
  - **1/|oᵢ| por resposta:** favorece respostas curtas quando a vantagem é positiva e respostas longas quando é negativa. O resultado são erros cada vez mais longos.
  - **Divisão pelo desvio do grupo:** dá peso excessivo a questões quase sempre certas ou quase sempre erradas.
- O Dr. GRPO remove os dois termos e normaliza por uma constante. Isso contém o crescimento do comprimento das respostas incorretas.
- Uma receita mínima com Qwen2.5-Math-7B chega a 43,3% no AIME 2024.

**Relevância para o Investigador (inferência)**
- O custo de tokens entra na recompensa, então um viés de otimização que alonga erros contamina a fronteira custo × erro. Use `dr_grpo` ou `dapo`, nunca `grpo` com 1/|o|.
- Pense em `scale_rewards="none"` ou `"batch"`. Com custos assimétricos, o desvio por grupo distorce a escala da matriz de custo entre alertas.

### [F-5] Zheng, C.; Liu, S.; Li, M. et al. (Qwen) (2025). Group Sequence Policy Optimization. arXiv. — [arXiv:2507.18071](https://arxiv.org/abs/2507.18071) · Preprint · Verificado (abs + HTML v2)

**Contribuição**
- A razão de importância por token do GRPO se apoia num único token amostrado. Isso gera ruído que se acumula com o comprimento e pode levar a colapso irreversível.
- O GSPO usa a razão de verossimilhança da sequência inteira (média geométrica por token) e faz o clipping por resposta. As faixas são 3e-4/4e-4, contra 0,2/0,27 no GRPO.
- O GSPO estabiliza MoE (cerca de 10% dos experts mudam após um update no Qwen3-30B-A3B) sem precisar de Routing Replay. Foi usado no Qwen3.

**Relevância para o Investigador (inferência)**
- O Gemma 4 E4B é denso, então o argumento de MoE não se aplica. A recompensa, porém, é por trajetória, o que torna o nível de sequência coerente.
- Barato de testar como ablação: `importance_sampling_level="sequence"` existe no TRL e no mlx-lm-lora.

### [F-6] Cui, G.; Zhang, Y.; Chen, J. et al. (2025). The Entropy Mechanism of Reinforcement Learning for Reasoning Language Models. arXiv. — [arXiv:2505.22617](https://arxiv.org/abs/2505.22617) · Preprint · Verificado (abs)

**Contribuição**
- A entropia da política cai bruscamente no início do RL sem intervenção, e o desempenho satura junto. A relação empírica proposta é R = −a·e^H + b.
- Mecanismo: a variação da entropia é dirigida pela covariância entre a probabilidade da ação e a variação do logit, proporcional à vantagem.
- Correções propostas: **Clip-Cov** e **KL-Cov**, aplicados aos tokens de alta covariância.

**Relevância para o Investigador (inferência)**
- Num agente que escolhe entre "investigar" e "responder já", o colapso de entropia equivale a fixar cedo uma estratégia (por exemplo, nunca chamar a ferramenta). Monitore a entropia nos tokens de decisão de chamada, não só a média global.

### [F-7] Shao, R.; Li, S. S.; Xin, R. et al. (2025). Spurious Rewards: Rethinking Training Signals in RLVR. arXiv. — [arXiv:2506.10947](https://arxiv.org/abs/2506.10947) · Preprint · Verificado (abs)

**Contribuição**
- Com GRPO, recompensas aleatórias elevaram o Qwen2.5-Math-7B em 21,4 pontos no MATH-500, contra 29,1 com recompensa correta.
- Os autores atribuem o efeito a um viés do clipping, que amplifica comportamentos já favorecidos no pré-treino.
- O efeito depende da família: recompensas espúrias costumam falhar em Llama3 e OLMo2.

**Relevância para o Investigador (inferência)**
- Quase toda a evidência de RL com ferramentas (F-8 a F-15) é em Qwen2.5. Não transfira ganhos esperados para o Gemma 4 sem um controle.
- Inclua um controle barato de **recompensa embaralhada** (mesmo pipeline, rótulos permutados) para separar o efeito "RL/clipping" do efeito "sinal de custo".

---

## 2. RL multi-turno com ferramentas

### [F-8] Jin, B.; Zeng, H.; Yue, Z.; Yoon, J.; Arık, S. Ö.; Wang, D.; Zamani, H.; Han, J. (2025). Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning. COLM 2025. — [arXiv:2503.09516](https://arxiv.org/abs/2503.09516) · **Peer-reviewed (COLM 2025, cabeçalho do PDF v5)** · Verificado (HTML v5 + PDF p.1)

**Contribuição**
- **Rollout multi-turno:** o modelo emite a consulta entre tags de busca, o sistema injeta os resultados (top-3 passagens) entre tags de informação, e a geração continua. O orçamento é de 4 ações.
- **Máscara dos tokens recuperados na loss (ablação):**

  | Modelo (PPO) | EM com máscara | EM sem máscara |
  | --- | --- | --- |
  | Qwen2.5-7B-base | 0,431 | 0,343 |
  | Qwen2.5-3B | 0,303 | 0,262 |

- A recompensa é só EM do resultado, sem recompensa de formato.
- O GRPO converge mais rápido, mas teve colapso de recompensa após muitos passos. O PPO foi mais estável.

**Relevância para o Investigador (inferência)**
- Esta é a referência mais direta para "consultar o SIEM simulado e depois responder". A máscara das observações do SIEM é inegociável.
- A escala de modelo é a mesma do projeto (3B–7B). O alerta sobre a instabilidade do GRPO justifica checkpoints frequentes e monitorar o desvio da recompensa.

### [F-9] Chen, M.; Sun, L.; Li, T. et al. (2025). ReSearch: Learning to Reason with Search for LLMs via Reinforcement Learning. NeurIPS 2025. — [arXiv:2503.19470](https://arxiv.org/abs/2503.19470) · Peer-reviewed (NeurIPS 2025, segundo o comentário do arXiv v3; anais não abertos) · Verificado (abs + HTML v3)

**Contribuição**
- GRPO com G = 5, implementado em verl. Os resultados da busca são excluídos da loss.
- Recompensa: F1 da resposta; 0,1 se F1 = 0 com formato correto; 0 caso contrário.
- Treina só em MuSiQue (19.938 exemplos, 2 épocas) com Qwen2.5-7B/32B. O número médio de buscas por rollout **cresce** ao longo do treino.

**Relevância para o Investigador (inferência)**
- Sem custo de chamada, o RL tende a aumentar as consultas. É o efeito oposto ao "colapso para resposta direta" e mostra que o termo de custo precisa existir **e** estar calibrado.

### [F-10] Qian, C.; Acikgoz, E. C.; He, Q.; Wang, H.; Chen, X.; Hakkani-Tür, D.; Tur, G.; Ji, H. (2025). ToolRL: Reward is All Tool Learning Needs. NeurIPS 2025 (Main Track). — [arXiv:2504.13958](https://arxiv.org/abs/2504.13958) · [anais NeurIPS](https://papers.neurips.cc/paper_files/paper/2025/hash/97c5b2707228e7e3fb67e4ecc2e0e607-Abstract-Conference.html) · **Peer-reviewed** · Verificado (abs, HTML, anais)

**Contribuição**
- **Recompensa:** formato ∈ {0, 1} mais correção fina ∈ [−3, 3], com termos separados para nome da ferramenta, nomes de parâmetros e valores. Recompensas grossas (tudo ou nada) foram piores.
- Uma interpolação suave de formato → correção ajudou. Uma **recompensa de comprimento** do raciocínio não ajudou e derrubou o Qwen2.5-1.5B (46,20% → 33,23%).
- GRPO sem KL e com G = 4, em Qwen2.5 1.5B/3B/7B e Llama-3.2-3B, com 4K exemplos. GRPO a frio superou SFT+GRPO no BFCL (7B: 58,38% vs 39,25%). Os autores atribuem isso a memorização no SFT.

**Relevância para o Investigador (inferência)**
- É contraevidência ao warm-start obrigatório. Só que aqui o modelo já fazia function calling no formato nativo, e no nosso caso o formato de ferramenta do SIEM é novo. Trate o warm-start como **ablação**, não como dogma.
- A decomposição fina sugere pontuar separadamente o veredito, a severidade, a Evidência literal e a CWE, em vez de um 0/1 global.

### [F-11] Feng, J.; Huang, S.; Qu, X. et al. (2025). ReTool: Reinforcement Learning for Strategic Tool Use in LLMs. arXiv. — [arXiv:2504.11536](https://arxiv.org/abs/2504.11536) · Preprint · Verificado (abs + HTML v2)

**Contribuição**
- Cold-start SFT com traços sintéticos que intercalam código, seguido de PPO (VeRL) com o interpretador no laço. A saída do interpretador **é mascarada na loss**.
- A recompensa é só ±1 de acurácia. Os autores omitem de propósito uma recompensa por "código executável" para reduzir reward hacking.
- Com Qwen2.5-32B-Instruct: 67% no AIME em 400 passos, contra 40% em 1.080 passos do RL só-texto. A chamada de código migra para mais cedo e atinge cerca de 98% das questões.

**Relevância para o Investigador (inferência)**
- Não premie "chamou a ferramenta" nem "consulta válida" por si só. Isso é hackeável.
- A tendência de 98% de uso sem custo explícito é o modo de falha "investigar sempre" que o termo de custo precisa conter.

### [F-12] Wang, Z.; Wang, K.; Wang, Q. et al. (2025). RAGEN: Understanding Self-Evolution in LLM Agents via Multi-Turn Reinforcement Learning. arXiv. — [arXiv:2504.20073](https://arxiv.org/abs/2504.20073) · Preprint · Verificado (abs + HTML v2)

**Contribuição**
- Propõe o StarPO (RL em nível de trajetória) e descreve o **Echo Trap**: o desvio da recompensa despenca antes da média, a entropia oscila e a norma do gradiente dispara. O raciocínio vira gabarito repetitivo.
- O StarPO-S mantém só os 25% de prompts com maior variância de recompensa, remove o KL e usa Clip-Higher (0,2/0,28).
- Com recompensas esparsas e atrasadas, o raciocínio multi-turno encolhe (Sokoban: de 307,1 para 89,5 tokens) e aparecem "pensamentos alucinados" com recompensa alta. Os experimentos principais usam Qwen2.5-0.5B-Instruct.

**Relevância para o Investigador (inferência)**
- O desvio da recompensa por grupo, a entropia e a norma do gradiente são os três sinais de alarme a registrar em `runs/`.
- O filtro por variância é um substituto barato do dynamic sampling, compatível com geração lenta.

### [F-13] Dong, G.; Mao, H.; Ma, K. et al. (2025). Agentic Reinforced Policy Optimization (ARPO). arXiv. — [arXiv:2507.19849](https://arxiv.org/abs/2507.19849) · Preprint ("Working on progress") · Verificado (abs + HTML v1)

**Contribuição**
- Observa que a entropia por token sobe logo após o retorno de uma ferramenta. Com base nisso, ramifica rollouts nesses pontos de alta incerteza (rollout adaptativo) e atribui vantagem por passo de ferramenta.
- Recompensa: com formato correto, vale max(Acc + r_M, Acc), onde r_M = 0,1 se usou busca e Python. Acurácia 0 com formato correto vale 0. Formato errado vale −1.
- Faz cold-start SFT (54K) antes do RL. No Qwen2.5-7B, supera o GRPO usando cerca de **metade das chamadas**.

**Relevância para o Investigador (inferência)**
- Ramificar após a observação do SIEM concentra exploração onde a decisão "investigar mais × concluir" é tomada. Isso é útil se a geração for o gargalo, como no M1 Max.

### [F-14] Jiang, D.; Lu, Y.; Li, Z. et al. (2025). VerlTool: Towards Holistic Agentic Reinforcement Learning with Tool Use. arXiv. — [arXiv:2509.01055](https://arxiv.org/abs/2509.01055) · Preprint · Verificado (abs)

**Contribuição**
- Extensão do verl com API unificada de ferramentas (código, busca, SQL, visão), plugins em Python e rollouts assíncronos. O ganho reportado é de cerca de 2× contra rollouts síncronos.
- Formaliza o RL agêntico como trajetórias multi-turno com tokens de observação. Foi avaliado em 6 domínios, com resultados comparáveis a sistemas especializados.

**Relevância para o Investigador (inferência)**
- O ganho de ~2× do modo assíncrono indica quanto a sincronização por turno custa. Por isso aplico um fator de 1,5× de overhead multi-turno na estimativa de tempo.
- Um "SIEM SQL somente-leitura" encaixa no tipo de ferramenta SQL já suportado.

---

## 3. Eficiência e custo na recompensa

### [F-15] Wang, H.; Qian, C.; Zhong, W. et al. (2025). Acting Less is Reasoning More! Teaching Model to Act Efficiently (OTC-PO). arXiv. — [arXiv:2504.14870](https://arxiv.org/abs/2504.14870) · Preprint · Verificado (abs + HTML v2)

**Contribuição**
- **Recompensa final:** α·r_tool·r_φ, onde r_φ é a correção. O produto anula o bônus de eficiência quando a resposta está errada. A forma **aditiva foi instável**: o modelo ganhava recompensa reduzindo chamadas sem acertar.
- **Mínimo de chamadas n\*:** é o menor número de chamadas entre as respostas corretas do grupo. A versão "global", atualizada entre épocas, foi mais estável.
- **Forma de r_tool:** com n\* > 0, r_tool = sin(f(m, n\*)·π/(2n\*)), com pico em m = n\*. Com n\* = 0, r_tool decai em cosseno com m.
- **Resultados (Qwen2.5 3B/7B e Qwen2.5-Math):** até −68,3% de chamadas e +215,4% de "tool productivity" (acertos/chamadas), com acurácia em geral comparável. Houve queda pontual (OTC-PPO, 3B, NQ).

**Relevância para o Investigador (inferência)**
- É o desenho mais próximo do proposto. Ele também dá uma definição de "chamada desnecessária" verificável sem anotação: chamadas acima de n\*.
- Com G = 8 e um modelo de 4B, n\* local é ruidoso, então use o n\* global por alerta.
- O OTC penaliza também chamar **menos** que n\*, o que protege contra o colapso para resposta direta.

### [F-16] Aggarwal, P.; Welleck, S. (2025). L1: Controlling How Long A Reasoning Model Thinks With Reinforcement Learning. COLM 2025. — [arXiv:2503.04697](https://arxiv.org/abs/2503.04697) · Peer-reviewed (COLM 2025, segundo o comentário do arXiv) · Verificado (abs + HTML v2)

**Contribuição**
- O LCPO condiciona a política a um orçamento escrito no prompt.
  - **L1-Exact:** r = 1[acerto] − α·|n_alvo − n_y|, com α = 0,0003.
  - **L1-Max:** r = 1[acerto]·clip(α·(n_alvo − n_y) + δ, 0, 1), com δ = 0,5. Ultrapassar um pouco o orçamento ainda vale mais que errar.
- Uma variante aditiva colapsou para cadeias muito curtas. O modelo base é o DeepScaleR-1.5B.
- Resultado: um único modelo cobre a curva custo × acurácia. A aderência fora do domínio é imperfeita (erro de comprimento de 20–40%).

**Relevância para o Investigador (inferência)**
- Para a fronteira de Pareto, condicione o prompt a um **orçamento de chamadas/tokens ou a um peso λ de custo** e varra λ na inferência. Uma única política treinada substitui K treinos, o que é decisivo dado o custo estimado abaixo.
- A forma multiplicativa com δ garante que errar barato nunca vale mais que acertar um pouco caro.

### [F-17] Hou, B.; Zhang, Y.; Ji, J.; Liu, Y.; Qian, K.; Andreas, J.; Chang, S. (2025). ThinkPrune: Pruning Long Chain-of-Thought of LLMs via Reinforcement Learning. arXiv. — [arXiv:2504.01296](https://arxiv.org/abs/2504.01296) · Preprint · Verificado (abs)

**Contribuição**
- RL com limite rígido de tokens: a resposta truncada recebe recompensa zero. O limite aperta em rodadas sucessivas.
- No DeepSeek-R1-Distill-Qwen-1.5B, o comprimento no AIME24 cai cerca de pela metade, com queda de ~2% de desempenho.

**Relevância para o Investigador (inferência)**
- O corte rígido é uma alternativa simples ao custo por token. Com `enable_thinking=false` e Relato curto (média de 178 tokens gerados no Run 0), o maior risco de custo está nas chamadas e nas observações, não no raciocínio. Um limite iterativo de chamadas (por exemplo 5 → 4 → 3) é o análogo direto.

### [F-18] Fatemi, M.; Rafiee, B.; Tang, M.; Talamadupula, K. (2025). Concise Reasoning via Reinforcement Learning. arXiv (relatório técnico). — [arXiv:2504.05185](https://arxiv.org/abs/2504.05185) · Preprint · Verificado (abs + HTML v3)

**Contribuição**
- Argumenta que o alongamento sob RL é um artefato da minimização da loss quando a recompensa é negativa (problemas insolúveis), e não "raciocínio mais profundo".
- Uma segunda fase de PPO com só 8 problemas resolvíveis reduz o comprimento médio em mais de 54% (1.5B) e 40% (7B), com acurácia média estável.
- No GRPO, grupos com recompensa toda igual deixam só o KL atuando. Isso levou a colapso para menos de 80 tokens em problemas insolúveis.

**Relevância para o Investigador (inferência)**
- Alertas genuinamente ambíguos, em que o modelo sempre erra, empurram para trajetórias longas ou degeneradas. Pense em filtrá-los do RL, ou dar a eles uma utilidade explícita para `suspicious` com `null` justificado.
- Uma fase curta de "concisão" sobre alertas que o modelo já acerta é uma forma barata de baixar custo sem retreinar tudo.

---

## 4. RL em tarefas de segurança

### [F-19] Muzsai, L.; Imolai, D.; Lukács, A. (2025). Improving LLM Agents with Reinforcement Learning on Cryptographic CTF Challenges. arXiv. — [arXiv:2506.02048](https://arxiv.org/abs/2506.02048) · Preprint · Verificado (abs + HTML v2)

**Contribuição**
- GRPO (G = 8, 4 desafios por passo, cerca de 250 passos) com QLoRA num A100 80GB. O modelo é o Llama-3.1-8B com ferramenta Python via MCP, treinado em 5.000 desafios cripto gerados proceduralmente.
- Recompensa: flag correta 1,0; formato 0,1; chamada JSON válida 0,2; execução sem erro 0,5; penalidades para "saída de ferramenta inventada" e flag antes de qualquer ferramenta. O ganho em Pass@8 transfere para picoCTF.
- No início, o modelo **imaginava a saída** em vez de executar. Os números de melhoria são inconsistentes entre seções do próprio artigo.

**Relevância para o Investigador (inferência)**
- Mostra GRPO com ferramentas viável em 8B com QLoRA numa GPU.
- O caso de saídas de ferramenta inventadas ensina que a checagem literal da Evidência deve aceitar só texto vindo de observações **realmente retornadas** pelo SIEM, nunca texto que o próprio modelo escreveu.
- Os bônus de chamada válida e de execução são exatamente o tipo de termo que o ReTool (F-11) evita.

### [F-20] Kong, H.; Hu, D.; Ge, J.; Li, L.; Li, H.; Li, T. (2025). Pentest-R1: Towards Autonomous Penetration Testing Reasoning Optimized via Two-Stage Reinforcement Learning. arXiv. — [arXiv:2508.07382](https://arxiv.org/abs/2508.07382) · Preprint · Verificado (abs + HTML v2)

**Contribuição**
- Duas etapas, ambas com GRPO:
  - **Offline:** cerca de 14K tuplas de walkthroughs reais.
  - **Online:** variante multi-turno com máscara de loss por turno, num ambiente CTF interativo.
- Modelo DeepSeek-R1-0528-Qwen3-8B com LoRA (r = 32), em 2× H100 com Unsloth.
- Recompensa online: +1 pela flag; +0,05 por comando válido e +0,05 por execução bem-sucedida; −0,1 por comando malformado ou falho; −0,2 por flag errada no fim. Resultados: AutoPenBench 24,2% e Cybench 15,0% (sem guia).

**Relevância para o Investigador (inferência)**
- O padrão "RL offline sobre dados estáticos → RL online com ambiente" mapeia para "GRPO single-turn sobre o Relato (já possível no MLX) → GRPO agêntico no Colab".
- Os +0,05 por passo recompensam agir. É o oposto do que queremos quando a ação tem custo.

### [F-21] Simoni, M.; Fontana, A.; Rossolini, G.; Saracino, A. (2025). Improving LLM Reasoning for Vulnerability Detection via Group Relative Policy Optimization. arXiv (under review). — [arXiv:2507.03051](https://arxiv.org/abs/2507.03051) · Preprint · Verificado (abs + HTML v1)

**Contribuição**
- GRPO em LLaMA 3B/8B e Qwen2.5-3B para detecção de vulnerabilidades (DiverseVul, BigVul, CleanVul).
- Recompensa: formato 4, acerto 4, mais termos de raciocínio. A vantagem usa só r − média, sem dividir pelo desvio.
- A soma estática 50/50 levou a **rotular quase tudo como vulnerável**, um reward hacking por colapso de classe. O peso dinâmico formato → acerto corrigiu isso.
- Ganhos sobre SFT de 1–29 pontos de macro-F1. O β do KL mexe no trade-off: β maior deixa o modelo mais conservador (mais VN, mais FN).

**Relevância para o Investigador (inferência)**
- É o análogo mais próximo de "classificação de segurança com RL e assimetria FP/FN" em escala de 3B–8B.
- Dois alertas práticos: (i) uma matriz de custo mal calibrada leva ao colapso numa classe "segura", que no nosso caso provavelmente seria `suspicious`; (ii) o β do KL também é um botão de FP/FN e deve entrar na ablação.

### [F-22] Barnes, J. (2026). OpenSec: Measuring Incident Response Agent Calibration Under Adversarial Evidence. arXiv. — [arXiv:2601.21083](https://arxiv.org/abs/2601.21083) · Preprint · Verificado (abs)

**Contribuição**
- Ambiente de RL de resposta a incidentes com injeção de prompt e pontuação por execução. Métricas: tempo até a primeira contenção, taxa de ação condicionada à evidência (EGAR) e raio de impacto.
- Modelos de fronteira agem cedo demais: GPT-5.2 conteve em 100% dos episódios com 82,5% de FP; Claude Sonnet 4.5, em 62,5% com 45% de FP. A síntese do autor: "the calibration gap is not in detection but in restraint".
- O artigo avalia, mas não treina.

**Relevância para o Investigador (inferência)**
- Dá evidência e métricas prontas (EGAR) para o lado FP da fronteira de Pareto. Também mostra que "agir com evidência suficiente" é mensurável por regra, o que é a base para definir chamada necessária ou desnecessária.
- Como as observações do SIEM podem conter texto adversarial nos logs, convém testar a robustez a injeção nas observações.

---

## Infraestrutura e estimativa de custo

### Tabela de ferramentas

| Ferramenta | Multi-turno com ferramentas? | Hardware | Observações | Fonte |
| --- | --- | --- | --- | --- |
| **mlx-lm-lora 5.10.2** (instalado) | **Não.** O GRPO é single-turn: gera G completions por prompt e pontua o texto com funções de recompensa. Nenhum trainer tem laço de ambiente ou ferramenta (código local inspecionado). | Apple Silicon (M1 Max 32 GB) | `generate_grpo` usa o `BatchGenerator` do mlx_lm com cache de prompt compartilhado, então o grupo é gerado **em lote**. Losses `grpo`/`bnpo`/`dr_grpo`, `epsilon_high` (DAPO), `importance_sampling_level="sequence"` (GSPO), `beta` (0 pula o modelo de referência). Também tem KLPO, PPO e online DPO. Exige escrever o laço multi-turno e a máscara de observação. | [README](https://github.com/Goekdeniz-Guelmez/mlx-lm-lora) · código local `mlx_lm_lora/trainer/grpo_trainer.py` |
| **TRL GRPOTrainer** (docs `main`; PyPI 1.19.0 de 25/11/2026) | **Sim.** `tools=[...]`, `environment_factory` (um ambiente por rollout, métodos públicos viram ferramentas, `reset()`/`get_reward()`, requer `transformers>=5.2.0`), `max_tool_calling_iterations`, `rollout_func` (experimental). O código-fonte zera os tokens de resultado de ferramenta via `tool_mask` (`completion_mask * tool_mask`), e uma máscara de ambiente vinda do `rollout_func` recebe o mesmo tratamento. | GPU CUDA; vLLM `colocate` (default) ou `server` | `loss_type` default `"dapo"`, mais `dr_grpo`, `grpo` (desaconselhado pela doc por viés de comprimento), `bnpo`, `cispo`, `sapo`, `luspo`, `vespo`. `scale_rewards` = `group`/`batch`/`none`. `beta=0.0` e `num_generations=8` por default. `mask_truncated_completions`, `top_entropy_quantile`, `entropy_coef`, `multi_objective_aggregation`. Métricas `tools/call_frequency` e `tools/failure_frequency`. **Gemma 4 tem template de treino prefix-preserving** que trata o canal de pensamento vazio de `enable_thinking=false`. A doc é do `main`; confirmar que 1.19.0 contém tudo isso. | [GRPO Trainer](https://huggingface.co/docs/trl/main/en/grpo_trainer) · [Chat Templates](https://huggingface.co/docs/trl/main/en/chat_templates) · [código](https://raw.githubusercontent.com/huggingface/trl/main/trl/trainer/grpo_trainer.py) · [PyPI](https://pypi.org/project/trl/) |
| **Unsloth GRPO** | **Não documentado** no guia de RL (só recompensas single-prompt). | T4 16 GB, L4 24 GB | Gemma 4: "E4B LoRA requires 17GB VRAM" (a intro diz 10 GB, sem dizer o método). RL documentado só para E2B, em 9 GB. **Gemma 4 é declarado não suportado no `fast_inference` (vLLM) do Unsloth**: usar `fast_inference=False`, o que deixa a geração em HF, mais lenta. Na T4 (fp16) há bug de overflow no caminho de áudio. A doc recomenda ≥300 passos antes de a recompensa subir e ≥500 linhas de dados. | [RL guide](https://unsloth.ai/docs/get-started/reinforcement-learning-rl-guide) · [Gemma 4 train](https://unsloth.ai/docs/models/gemma-4/train) |
| **verl** (HybridFlow, EuroSys 2025) | **Sim.** `rollout.multi_turn`, `ToolAgentLoop`, `BaseTool`/`@function_tool`. `AgentLoopOutput.response_mask` vale 1 para tokens do LLM e 0 para resposta de ferramenta. Backends vLLM e SGLang. | Multi-GPU (Ray, FSDP/Megatron); LoRA RL | GRPO, DAPO, GSPO, DrGRPO (as três últimas via verl-recipe). Não há guia de GPU única. O README cita a aceitação na EuroSys 2025; o DOI ACM 10.1145/3689031.3696075 consta no arXiv, mas a página da ACM retornou 403. | [README](https://github.com/volcengine/verl) · [multi-turn](https://verl.readthedocs.io/en/latest/sglang_multiturn/multiturn.html) · [agent loop](https://verl.readthedocs.io/en/latest/advance/agent_loop.html) · [arXiv:2409.19256](https://arxiv.org/abs/2409.19256) |
| **VerlTool** | **Sim**, sobre o verl. Rollout assíncrono com ~2× de ganho. | GPU | Ferramentas plugáveis (SQL, busca, código). | [arXiv:2509.01055](https://arxiv.org/abs/2509.01055) |
| **OpenRLHF** | **Sim.** Modo multi-turno com `reset()`/`step()` (`--train.agent_func_path`) e servidor de agente compatível com OpenAI. O README **não documenta** a máscara de tokens do ambiente. | Ray + vLLM, multi-GPU | PPO, REINFORCE++, GRPO, RLOO, Dr. GRPO, filtro dinâmico estilo DAPO. Só preprint (arXiv:2405.11143). | [README](https://github.com/OpenRLHF/OpenRLHF) |
| **vLLM** (docs latest, 25/11/2026) | n/a (motor de geração) | CUDA | `Gemma4ForCausalLM` suportado, **com LoRA**. Portanto o modo `vllm` do TRL deve servir o E4B, ao contrário do caminho do Unsloth (inferência: testar). | [Supported models](https://docs.vllm.ai/en/latest/models/supported_models.html) |

**Dados de throughput usados**
- **NVIDIA L4 (especificação oficial):** 24 GB, 300 GB/s, cerca de 121 TFLOPS BF16 denso (242 com esparsidade). [nvidia.com/l4](https://www.nvidia.com/en-us/data-center/l4/)
- **Gemma 4 E2B, pesos QAT W4A16, vLLM 0.33.0, L4** (128 tokens de entrada / 512 de saída), tokens de saída agregados por segundo. Fonte: post comunitário AWS Builder de 06/11/2026, **não oficial**, e o modelo é **menor** que o E4B. [builder.aws.com](https://builder.aws.com/content/3LkJbIXPJxarzoZDc3HWg4ZzBZY/six-serving-engines-on-one-ec2-g6-gemma-4-e2b-on-an-nvidia-l4)

  | Concorrência | tok/s agregados |
  | --- | --- |
  | 1 | 138,8 |
  | 8 | 991 |
  | 64 | 3.715,7 |

- **Unsloth:** cerca de 300 tok/s numa T4 com vLLM. O exemplo não está ligado a um modelo específico (RL guide).
- **Medidas locais (`runs/`):**
  - Run 0 (zero-shot, validação): 537 tokens de prompt e 178 tokens gerados em média; ~25,8–30 tok/s de geração.
  - Smoke Run 2 (QLoRA, batch 1, `max_seq_length` 1024): cerca de 0,2 it/s, isto é, ~5 s por exemplo, com 16,8 GB de pico.
- **Colab AI Pro** (limites de sessão, unidades de computação, disponibilidade de L4): **NÃO VERIFICADO**.

### Estimativa de tempo (toda esta seção é **inferência**)

**Suposições**
- **S1. Episódio** = uma trajetória: prompt → ~3 chamadas ao SIEM → Relato.
  - Tokens gerados: 800 (dado do pedido).
  - Observações: 3 × 300 = 900 tokens, que entram por prefill e não são gerados (suposição).
  - Prompt agêntico: ~800 tokens (o prompt atual tem 537 medidos, mais a descrição das ferramentas).
  - Contexto total por trajetória: ~2.500 tokens.
- **S2. M1 Max:** 25 tok/s sequencial, conforme o pedido. O mlx-lm-lora gera o grupo em lote, mas o ganho de lote para o E4B **não foi medido**. Uso como hipótese 4× (100 tok/s agregados).
- **S3. L4 + vLLM, E4B em BF16, colocado com o treino:** 800 tok/s agregados (faixa de 500 a 1.500), com fator 1,5 de sincronização multi-turno.
  - Base: o E2B W4A16 faz 991 tok/s com 8 sequências e 3.716 com 64.
  - O E4B em BF16 lê cerca de 8 GB por passo de decodificação, contra ~1–1,5 GB do E2B quantizado, a 300 GB/s.
  - No modo colocate, a memória de 24 GB limita o KV cache e, com isso, a concorrência.
- **S4. Ferramenta:** a latência do replay local é desprezível (≪ 1 s por chamada). No M1 Max, o prefill das observações custa ~7.200 tokens por grupo de 8; a 300–500 tok/s (não medido), isso soma +14–24 s por grupo.

**Geração em um passo GRPO**

1. **Um prompt, G = 8:** 8 × 800 = 6.400 tokens gerados.
   - M1 Max sequencial: 6.400 / 25 = **256 s ≈ 4,3 min**, mais 14–24 s de prefill, ≈ 4,6–4,7 min.
   - L4: com só 8 sequências concorrentes, a vazão agregada fica abaixo de S3. Estimo 250–400 tok/s para o E4B (o E2B faz 991), o que dá **≈ 16–26 s**.
2. **Passo típico, 8 prompts × G = 8 = 64 trajetórias:** 51.200 tokens.
   - M1 Max sequencial: 51.200 / 25 = 2.048 s ≈ **34 min**.
   - M1 Max com lote (hipótese de 100 tok/s): 512 s ≈ **8,5 min**.
   - L4 a 800 tok/s: 64 s; com o fator 1,5, ≈ **1,6 min** (faixa de 0,6 a 3 min).

**Geração para ~1.000 episódios** (duas leituras do pedido)

| Leitura | Tokens gerados | M1 Max a 25 tok/s | M1 Max a 100 tok/s (hipótese de lote) | L4 a 800 tok/s × 1,5 |
| --- | --- | --- | --- | --- |
| **A:** 1.000 prompts × G = 8 = 8.000 trajetórias (≈ 1 época sobre os 1.147 alertas de treino) | 6,4 M | 256.000 s ≈ **71 h (~3 dias)** | 64.000 s ≈ **17,8 h** | 12.000 s ≈ **3,3 h** (faixa 1,8–5,3 h) |
| **B:** 1.000 trajetórias no total (125 prompts × 8) | 0,8 M | 32.000 s ≈ **8,9 h** | 8.000 s ≈ **2,2 h** | 1.500 s ≈ **25 min** |

**Atualização da política** (fora do pedido, mas é da mesma ordem que a geração)
- **M1 Max:**
  - Âncora: o smoke Run 2 processa ~5 s por exemplo de ~700 tokens, ou seja, ~140 tok/s de contexto em forward + backward.
  - Uma trajetória de 2.500 tokens leva ~18 s, mais ~6 s de forward para log-probs, ≈ 24 s.
  - Leitura A: 8.000 × 24 s ≈ **53 h**. Leitura B: ≈ **6,7 h**.
- **L4:**
  - Custo por token: cerca de 24–32 GFLOP (forward + backward com LoRA, forward de log-probs, gradient checkpointing; base de ~4B parâmetros ativos).
  - Volume: 20 M tokens × 24–32 GFLOP = 4,8–6,4 × 10¹⁷ FLOP.
  - Com 30% de MFU (~36 TFLOPS efetivos): **≈ 3,7–4,9 h** na leitura A e ~30–40 min na B.

**Totais por época (leitura A)**
- **M1 Max:** 71 + 53 ≈ **124 h (~5 dias)** em geração sequencial, ou ≈ **71 h (~3 dias)** se o lote der 4×.
- **L4:** ≈ **7–8 h** (faixa de 5 a 11 h).

**Multiplicadores que pesam mais que o hardware**
- **Passos mínimos:** a doc do Unsloth sugere ≥300 passos até a recompensa subir. Com 8 prompts por passo, isso dá ~2,1 épocas: **~15–20 h de L4** ou **~1–1,5 semana de M1 Max** por política.
- **Fronteira de Pareto com K políticas** (uma por λ): multiplica por K. Com uma política condicionada ao orçamento (F-16), o fator volta a ~1.
- **Avaliação:** cada passada na validação (177 × 800 tokens = 141.600 tokens) leva ~94 min no M1 Max sequencial e ~3–5 min na L4.

**Veredito de viabilidade (inferência)**
- **MLX local**
  - Viável para:
    - construir e testar o ambiente SIEM e as funções de recompensa;
    - medir o baseline agêntico (zero-shot/SFT) na fronteira;
    - warm-start SFT;
    - um piloto pequeno (leitura B, ~10–15 h), depois de escrever o laço multi-turno com máscara.
  - Inviável como plataforma principal para várias épocas mais a fronteira.
- **Colab L4**
  - Viável com o `environment_factory` do TRL, `tool_mask` e o template Gemma 4 já tratado.
  - Restrições:
    - 24 GB divididos entre treino e vLLM colocado;
    - o Unsloth não acelera a geração do Gemma 4;
    - limites de sessão do Colab não verificados, então checkpoints frequentes.
  - Pela regra do `AGENTS.md`, a stack fica em `colab/` só depois de aprovada.
- **Colab T4**
  - Marginal: 16 GB, fp16 e sem BF16; o E4B LoRA 16-bit (17 GB) não cabe; geração sem vLLM no Unsloth.

---

## Lacunas observadas

- **Nenhum trabalho de GRPO/PPO para triagem de alertas de SOC com LLM e ferramentas foi encontrado.**
  - O mais próximo é offline RL sem LLM ([arXiv:2611.05746](https://arxiv.org/abs/2611.05746), preprint de 03/11/2026, verificado): 74.909 alertas rotulados, restrição de escalonamento benigno. A fração de escalonamento benigno foi 0,000 no RL, 0,007 no autoencoder e 0,041 no Isolation Forest.
  - O OpenSec (F-22) mede excesso de ação mas não treina.
- **Custo assimétrico FP/FN dentro da recompensa de RL de LLM** quase não aparece. O F-21 mostra o colapso de classe, mas não usa matriz de custo explícita.
- **Base de modelos:** a evidência de RL com ferramentas está concentrada em Qwen2.5 3B–7B e QA/matemática (F-8 a F-15). Não achei resultado publicado com Gemma 4, e o F-7 mostra que efeitos de RLVR variam por família.
- **Orçamento de ferramentas:** só o OTC (F-15) define "chamada ótima" de forma operacional, e por grupo. Nenhum trabalho encontrado produz uma **fronteira controlável** custo de ferramenta × erro com uma política condicionada; o L1 (F-16) faz isso só para comprimento.
- **Infraestrutura:** não existe RL multi-turno com ferramentas em MLX (mlx-lm-lora 5.10.2). Não há número de vazão publicado e confiável para o Gemma 4 E4B em L4 com vLLM, só o E2B quantizado num post comunitário.
- **Venues não confirmadas nos anais:** ReSearch (NeurIPS 2025 só pelo comentário do arXiv) e L1 (COLM 2025 só pelo comentário do arXiv). DeepSeek-R1 foi confirmado na Nature pelo journal-ref do arXiv, não pela página da Nature.

## Riscos de desenho (reward hacking, colapso, viés de comprimento)

1. **Colapso para resposta direta.**
   - Se a maioria dos alertas é decidível pela âncora e cada chamada custa, a política aprende a nunca investigar.
   - Evidência: formas aditivas colapsaram no OTC (F-15) e no L1 (F-16).
   - Agravante: o colapso de entropia (F-6) fixa a estratégia cedo.
2. **Investigação excessiva.**
   - Sem custo, o uso de ferramenta cresce (F-9; F-11 chegou a ~98% das questões).
   - Bônus por chamada válida ou execução (F-19, F-20) premiam agir.
3. **Hedge em `suspicious`.**
   - Com 4 classes, se FN custa muito e `suspicious` sai barato, a política converge para `suspicious`. É o análogo do "tudo vulnerável" do F-21 e infla a FPR no conjunto benigno/expected_admin.
4. **Evidência fabricada ou citada à toa.**
   - O modelo pode escrever texto que imita a saída do SIEM (F-19) ou citar linhas irrelevantes para "provar" que a chamada era necessária.
5. **Vazamento temporal no replay.** Uma consulta que escapa do corte na âncora vira atalho de rótulo e infla o acerto.
6. **Viés de comprimento.**
   - A normalização 1/|o| do GRPO alonga os erros (F-4).
   - Recompensas negativas alongam respostas no PPO (F-18).
   - Truncamento com recompensa zero gera ruído (F-3).
   - Isso contamina diretamente o eixo "custo de tokens" da fronteira.
7. **Grupos sem variância.** Com um SFT forte, muitos grupos têm vantagem zero (F-3, F-12, F-18), e a geração cara é desperdiçada.
8. **Instabilidade do GRPO multi-turno.** Colapso tardio de recompensa (F-8) e Echo Trap (F-12).
9. **Ganho espúrio.** Melhoria por viés do clipping, não pelo sinal de custo (F-7).
10. **Dados pequenos** (1.147 alertas). Múltiplas épocas de RL podem sobreajustar a política aos padrões de consulta do replay, em vez de generalizar.

## Recomendações concretas para o desenho da recompensa e do pipeline

1. **Warm-start em duas camadas, como ablação.**
   - **(a)** Partir do melhor adaptador SFT do Relato, que já garante formato e Evidência.
   - **(b)** Somar um SFT curto com algumas centenas de trajetórias agênticas sintéticas, geradas por regra ou por professor e validadas pelo replay, para ensinar a sintaxe de ferramenta. Base: F-2, F-11, F-13, F-20.
   - **(c)** Comparar com GRPO direto a partir de (a). Base: F-10, em que o RL a frio venceu SFT+RL.
   - Critério para seguir ao RL: a política inicial precisa produzir **variância de recompensa** em pelo menos ~30% dos grupos (meta inferida).
2. **Recompensa multiplicativa, com ordenação garantida.**
   - Utilidade da matriz de custo: U(ŷ, y), com U > 0 no acerto e U < 0 nos erros. Por exemplo, FN malicious → benign = −C_FN e FP benign → malicious = −C_FP, com C_FN ≥ C_FP e `suspicious` custando menos que o erro grave, mas não zero.
   - Validade: `gate` = 1 se o JSON é válido no Pydantic **e** toda a Evidência é literal na entrada ou em observações realmente retornadas; 0 caso contrário.
   - Fórmula:
     - Com gate = 0: R = −1.
     - Com gate = 1 e acerto: R = U · r_custo(m, n\*, tokens), com r_custo ∈ [δ, 1] e δ ≈ 0,5, no estilo L1-Max/OTC.
     - Com gate = 1 e erro: R = U, **sem** termo de custo, para não ensinar que investigar é ruim quando se erra.
   - Isso garante que qualquer acerto vale mais que qualquer erro (lições de F-15 e F-16).
3. **"Chamada desnecessária" verificável, em camadas, todas por regra:**
   - **Sempre desnecessária:** consulta duplicada, sintaticamente inválida, fora da janela permitida (bloqueada pelo corte temporal) ou que retorna vazio.
   - **Por anotação no dataset:** marcar em cada alerta o conjunto mínimo de IDs de linha de evidência (gold evidence) e se ele está na âncora ou só no contexto do SIEM. Uma chamada é **necessária** se retorna pelo menos uma linha da gold evidence ainda ausente do contexto. Nos demais casos é desnecessária. Isso é auditável e independe do modelo.
   - **Sem anotação (fallback):** n\* global do OTC, o mínimo de chamadas entre trajetórias corretas daquele alerta ao longo das épocas.
   - **Contra citação gratuita:** só conta como "chamada útil" a que retornou uma linha citada literalmente **e** pertencente à gold evidence.
4. **Contra o colapso para zero chamadas:**
   - estratificar o treino para incluir alertas em que a âncora sozinha é insuficiente (contexto obrigatório);
   - punir também m < n\* (forma senoidal do OTC);
   - registrar `tools/call_frequency` **por estrato**, já que a média global esconde o colapso.

   Contra o excesso de chamadas: `max_tool_calling_iterations` = 4–5 (Search-R1 usou 4; OTC, 3–4) e, se preciso, um corte iterativo 5 → 4 → 3 (F-17).
5. **Fronteira de Pareto com uma política.** Pôr no prompt o peso λ de custo ou o orçamento de chamadas, e amostrar λ por episódio no treino (L1, F-16). Avaliar a varredura de λ no teste. Treinar K políticas fixas só como verificação em 2–3 pontos.
6. **Grupo e filtragem.**
   - G = 8 (default do TRL; usado em F-19). Considerar G = 12–16 na L4 se a variância for baixa (DAPO usou 16).
   - Filtrar grupos de variância zero: dynamic sampling (F-3) ou top-p% por variância (F-12, 25%). No M1 Max, prefira o filtro por variância, que não reamostra.
7. **KL.**
   - Começar com β pequeno (1e-3, como no R1) em vez de 0. O dataset é pequeno, e o KL ajuda a preservar o formato JSON e a calibração do SFT.
   - Tratar β como eixo de ablação, porque desloca FP/FN (F-21).
   - Se houver instabilidade, `sync_ref_model` do TRL.
8. **Máscara de observação obrigatória.**
   - Tokens das respostas do SIEM fora da loss (F-8: +8,8 pontos de EM no 7B). É `tool_mask` no TRL e `response_mask` no verl.
   - Validar com `is_chat_template_prefix_preserving` e o template de treino do Gemma 4 com `enable_thinking=false`.
   - Usar stop tokens que impeçam o modelo de escrever o bloco de resposta de ferramenta.
9. **Normalização por comprimento.**
   - `loss_type="dr_grpo"` ou `"dapo"`, nunca `"grpo"`.
   - `scale_rewards="batch"` ou `"none"` (F-4), para preservar a escala da matriz de custo entre alertas.
   - `mask_truncated_completions=True` (F-3).
   - Custo de tokens medido só sobre tokens **gerados**, não sobre observações. A observação já entra via custo de chamada.
10. **Estabilidade e diagnóstico.**
    - `epsilon_high` ≈ 0,28 (Clip-Higher).
    - Registrar em `runs/`, por passo:
      - entropia;
      - desvio da recompensa por grupo;
      - norma do gradiente;
      - fração de grupos com variância zero;
      - chamadas e tokens por estrato;
      - FPR no conjunto benigno/expected_admin.
    - Testar `importance_sampling_level="sequence"` (F-5) como ablação.
11. **Controles contra ganho espúrio.**
    - Uma rodada com recompensa de rótulo embaralhado (F-7).
    - Avaliar sempre o baseline agêntico zero-shot/SFT nos mesmos λ.
    - Medir a fidelidade literal da Evidência **contra as observações realmente retornadas**.
    - Incluir observações com texto adversarial no replay (F-22).
12. **Sequência de infraestrutura (inferência).**
    - **No MLX:** ambiente SIEM, recompensas, baseline agêntico e piloto de GRPO single-turn sobre o Relato (já suportado).
    - **No Colab L4**, depois de aprovar a stack em `colab/`: GRPO agêntico com TRL (`environment_factory`, `tool_mask`, vLLM `colocate` ou HF generate), em execuções retomáveis por checkpoint.
    - Medir **antes**: tok/s agregados do E4B na L4, tok/s em lote no MLX e tempo de forward + backward de uma trajetória de 2.500 tokens. Isso substitui as hipóteses S2–S3.
