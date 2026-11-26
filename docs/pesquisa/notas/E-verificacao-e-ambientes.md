# Tema E — Verificação de afirmações, RL em defesa cibernética e ambientes

> **Nota de 25/11/2026:** pelo ADR 0004, o "Investigador" citado aqui é o próprio Guardião com Ferramentas de leitura. A afirmação 6 se refere a um resumo colado pelo responsável, não a uma fonte.

**Data:** 25/11/2026. **Executor:** Claude Code (subagente), modelo `claude-opus-5-5`.
**Método:** leitura das fontes primárias (arXiv abs/HTML, anais, repositórios oficiais, Zenodo, Hugging Face) via WebFetch. Dois PDFs pequenos (a dissertação da AUB, 650 KB, e o artigo de Elkan, 94 KB) foram convertidos com `pdftotext` no scratchpad. Nenhum repositório foi alterado. Fiz uma leitura somente-leitura de `configs/datasets/` e `docs/curadoria/` do `soc-triage-lora-lab` para avaliar o risco de contaminação.
**Lacuna de contexto:** não consultei o `mathai-wiki`, porque a tarefa era só de pesquisa e foi delegada. Este arquivo não deve ser tratado como fonte de preferências nem do estado atual do trabalho.
**Convenções:** "Verificado" quer dizer que a URL foi aberta nesta sessão. **NÃO VERIFICADO** quer dizer que não abri a página ou que ela bloqueou o acesso. Afirmações marcadas como *inferência* são minhas e não vêm da fonte.

---

## 1. Verificação das afirmações

| # | Afirmação (como recebida) | Veredito | O que a fonte diz | Onde |
|---|---|---|---|---|
| 1a | Tsegai et al. (2610.10608): o Self-Refine transformou 73 descartes corretos em escalonamentos falsos, e os FP foram de 8 para 65 | **PARCIAL** | Na revisão, o Self-Refine mudou 95 decisões. Consertou 16 e estragou 79. Das mudanças, 73 foram de descarte para escalonamento, e os FP subiram de 8 para 65 (+57). O artigo **não** diz que os 73 eram todos descartes corretos. O F1 caiu de 0,665 para 0,550, e 74 das 95 reversões aconteceram sem nenhum registro novo. | §IV-C |
| 1b | O CoVe converteu ataques reais em descartes | **CONFIRMADA** | O CoVe mudou 157 decisões, com 25 consertos e 132 erros. Foram 79 escalonamentos convertidos em descartes, os TP caíram de 121 para 67 e o F1 foi de 0,669 para 0,371. | §IV-C |
| 1c | "Empty-retrieval bias" | **PARCIAL** (o fenômeno se confirma, o termo não) | O artigo fala em "empty retrieval" e "no-record", não em "bias". Finding 3: buscas vazias estão fortemente associadas ao descarte de ataques. Taxa de descarte de ataque com 0 registros contra ≥1 registro: ReAct 98,6% vs 30,3%, Self-Refine 96,2% vs 37,6%, Direct-Prompt 80,0% vs 27,6%. Dos 602 FN, 211 não recuperaram nenhum registro. Para alertas benignos, a variação foi de no máximo 2,8 pp. Correlação de postos de 0,383. | §IV-C |
| 1d | Remover o Judge do AIDA derruba o F1 de 0,952 para 0,895 | **CONFIRMADA, com ressalva** | Os números estão na Tabela II, mas valem para o **subconjunto de 300 alertas** (54 ataques). O IC95% pareado da diferença é [0,008; 0,131]. Nos 1.247 alertas, o AIDA completo tem F1 de 0,958. O ganho do Adversary não foi significativo. | §VI-C, Tab. II |
| 1e | Gastar mais tokens/compute por alerta não melhora a triagem | **CONFIRMADA** | Finding 2 (citação literal abaixo). Os autores ressalvam que isso não prova que computação extra seja prejudicial em si. | §IV-B, Fig. 2, §VIII |
| 1f | Arquiteturas agênticas verbosas têm F1 inferior a prompts diretos bem estruturados | **PARCIAL** (falsa como generalização) | Entre as 5 abordagens estudadas com GPT-4.1, o Direct-Prompt (5.075 tokens, 3 chamadas) teve o maior F1 (0,744). Mas o AIDA, que é multiagente e gasta cerca de 33.942 tokens, chegou a 0,958. A tese do artigo é que a estrutura da investigação importa mais que o volume de computação. O artigo não diz que agentes verbosos perdem para prompts diretos. | §IV-B, §VI-A |
| 2 | Khanna et al. (2607.28460): o CoT degrada a calibração do token de rótulo; usam um calibrador separado; ganho de +43,0 pp no recall benigno e +18,3 pp no malicioso em pontos de alta precisão | **PARCIAL** | (a) A degradação é **argumentada de forma qualitativa**: sem ECE e sem curva de calibração com e sem CoT. (b) O calibrador existe: um Nemotron-3-Nano-30B com LoRA lê a detecção, o raciocínio completo e o rótulo, e responde "correct" ou "incorrect". (c) No teste, o recall benigno foi de 64,8% contra 21,8% (+43,0 pp) e o malicioso de 53,0% contra 34,7% (+18,3 pp). Isso vale na faixa de alta confiança, cujos limiares foram ajustados na validação para 98% de precisão (benigno) e 99% (malicioso). No teste, a precisão benigna ficou em **90,8%**, abaixo da meta. O resumo escreve "%", mas o corpo do texto diz pp. | §3.5, §4.3, Tab. 1, Tab. 3 |
| 3 | Mustafa et al. (RG 391041569, 2025): grafos de processos + modelos destilados (DistilBERT, TinyLlama, RoBERTa), com 91,7% de precisão e 97% de recall na filtragem de FPs de HIDS | **PARCIAL**. O venue foi encontrado. Os números do artigo são **NÃO VERIFICADOS**: aparecem na dissertação precursora, mas são de outro modelo, não do melhor. | **Venue:** AINA 2025, *LNDECT* vol. 248, pp. 432–443, Springer, DOI 10.1007/978-3-031-87772-8_37 (revisado por pares). O texto do capítulo é pago e não foi lido. **Dissertação de mestrado na AUB (2024), do mesmo autor, orientada por Chehab:** um "Execution Graph" por processo Windows alertado (Sysmon → Winlogbeat → Elasticsearch, com regras do SOC), seguido de um "Graph Contextualizer". São cerca de 700 casos reais de uma empresa (≈550 FP e ≈150 TP), com split 70/15/15. Sete modelos com menos de 7B passaram por fine-tuning com cabeça de classificação: GPTNeo, DistilBERT, TinyLlama, GPT2, RoBERTa, DeepSeek e Phi. **Os valores 0,917/0,97 são do DistilBERT.** O melhor modelo foi o TinyLlama, com P 0,981, R 0,994 e F2 0,99, num teste de cerca de 108 casos. Chamar os modelos de "destilados" está errado, porque só o DistilBERT é. *Inferência:* 0,917/0,97 batem com a média macro das duas classes na matriz de confusão do DistilBERT. | Dissertação §4.1, §5.1, §5.3 (Fig. 6 e a tabela seguinte, que são imagens) |
| 4 | DoLLM (2503.18487): Flow Sequentializer e tokenizer aprendível; supera classificadores tabulares em mais de 35% de F1 | **PARCIAL** | O 2503.18487 é um artigo de arquitetura e oportunidades (Zhang et al.), e o DoLLM é o estudo de caso (§IV). O artigo original do DoLLM é o 2405.07638. O Flow Sequentializer (ordenação, binning de frequência igual, montagem vertical) e o **Flow Tokenizer aprendível** se confirmam, com backbone Llama2-7b-chat. O ganho de F1 é de **"pelo menos 35,1%"** num trace NetFlow real de uma operadora Top-3. As baselines são XGBoost, AutoEncoder, LSTM e Transformer; só o XGBoost é um classificador tabular clássico. Em zero-shot, o ganho é de até 24%. O texto não diz se o ganho é absoluto ou relativo, e os valores só aparecem na Fig. 5. O 2405.07638 relata outros números: até 33,3% em zero-shot e ≥20,6% no ISP. | 2503.18487 §IV-A, §IV-B, Fig. 5; 2405.07638 resumo |
| 5 | ADÉ (2509.16749): valida regras em corpora históricos (retro-hunting) antes de promover; faz mutações automáticas de ameaças | **PARCIAL** | O ADÉ (*Autonomous Detection Engineer*, da Sublime Security) gera regras MQL para **e-mail**. O pipeline checa a sintaxe, testa a regra na amostra original e roda caças em dados históricos de e-mail (retro-hunt). Depois, um revisor humano aprova. **As mutações automáticas não foram feitas:** aparecem só como trabalho futuro. A robustez é medida por um escore estático de fragilidade da regra. | Descrição do pipeline do ADÉ e trabalhos futuros (seção exata não identificada) |
| 6 | Ensembles heterogêneos de SLMs (7B–9B, como Qwen3.5 9B ou Gemma-3n + Llama-3.3) com votação cortam o FPR pela metade frente a um único modelo gigante | **NÃO CONFIRMADA** | A única fonte encontrada é Saju & Azim. O ensemble usa voto majoritário entre GPT-4o-mini, Gemma-3n-E4B-it e **Llama-3.3-70B**. Não são SLMs de 7–9B, e não há Qwen3.5 9B. O FPR do ensemble é 0,120. Comparações: o melhor modelo isolado (GPT-4o-mini) tem 0,153, uma redução relativa de cerca de 22%. O Llama-3.3-70B tem 0,246; contra ele o FPR cai para cerca de metade, mas ele é **membro** do ensemble. O GPT-4o tem 0,469 e o Qwen3-Next-80B tem 0,776. O recall do ensemble (0,708) é menor que o de todos os membros. AdaBoost e XGBoost têm FPR menor (0,040 e 0,046), mas com recall baixo. Os dados são 20 mil logs de SIEM com rótulo critical/non-critical; a rotulagem não é descrita e os dados não são públicos. Duas buscas adicionais não acharam outra fonte. | Tabela de detecção (rotulada como Tabela 1 e citada como "Tabela 2" no texto) |

Citação literal (1e): *"Greater computational cost does not correspond to better triage quality."* (Tsegai et al., §IV-B).

---

## 2. Fichas

### Grupo A — Fontes das afirmações verificadas

### [E-1] Tsegai, Kantchelian, Yao, Gao (2026). From Investigation Failures to Reliable SOC Agents: Understanding and Improving LLM-Based Alert Triage. arXiv:2610.10608.
Link: https://arxiv.org/abs/2610.10608 (HTML: https://arxiv.org/html/2610.10608) · Status: preprint. Uma versão curta ("Benchmarking LLM Agents for SOC Alert Triage: Performance and Failure Modes", de Tsegai e Gao) é pôster no workshop *Agents in the Wild* da NeurIPS 2026: https://neurips.cc/virtual/2026/168137 · Verificado em 25/11/2026. O OpenReview bloqueou o acesso.
- **Contribuição:**
  - O ALERT-BENCH reproduz a telemetria do AIT-LDSv2 (cenário russellmitchell, 4 dias) num **Wazuh** ao vivo. São 1.247 alertas (225 de ataque e 1.022 benignos), com rótulos por evento no padrão AIT-ADS, escondidos do agente. Há 6.235 investigações com GPT-4.1, e todas as 5 abordagens deixaram passar ≥40,4% dos alertas de ataque.
  - As ferramentas usam **MCP**: `get_wazuh_alerts`, `search_security_events`, `get_wazuh_alert_summary`, `analyze_alert_patterns` e um inventário de hosts. O orçamento de chamadas é de 3 (Direct), 5 (ReAct), 7 (Self-Refine), 10 (CoVe) ou 3×5 (Self-Consistency). O AIDA faz no máximo 5 chamadas por rodada, em até 3 rodadas.
  - O AIDA usa Strategist, Adversary em contexto separado, Judge e um Investigation Ledger append-only, e exige evidência mais forte para descartar. Resultados: F1 de 0,958, FNR caindo de 40,4% para 3,1%, 18,4% de alertas escalados, 4,3 chamadas, cerca de 33,9 mil tokens e cerca de US$0,109 por alerta. Modelos abertos dentro do AIDA (Tab. III, 300 alertas): Llama 3.1 8B 0,098; Llama 3.1 70B 0,656; GPT-OSS 120B 0,717; Gemma4 31B 0,777; **Qwen3.5 9B 0,952** (os valores de P e R são idênticos aos da linha do GPT-4.1 na Tab. II, então vale conferir no PDF). No wardbeck (337 alertas, 5,93% de ataques), o F1 foi de 0,927. Não há anúncio de liberação de código nem de dados.
- **Relevância para o Investigador (inferência):**
  - Este é o desenho de ambiente mais próximo do Investigador: alerta, consultas somente-leitura, descarte ou escalonamento, e ground truth por alerta. O viés de busca vazia é um modo de falha que a recompensa precisa punir de forma explícita.
  - O scaffold importa tanto quanto o tamanho do modelo: 9B chegou a 0,952 e 8B a 0,098. O Gemma 4 E4B não foi testado.

### [E-2] Khanna et al. (2026). Cybersecurity Detection Classification with Reasoning-enabled Language Models. arXiv:2607.28460.
Link: https://arxiv.org/abs/2607.28460 (HTML: https://arxiv.org/html/2607.28460) · Status: preprint · Verificado em 25/11/2026.
- **Contribuição:**
  - O artigo treina um classificador de triagem com CoT sobre 388.336/59.162/42.686 detecções Windows rotuladas por humanos num SOC comercial, em janelas de 8/2/1 semanas consecutivas. Combina otimização automática de prompt, self-training e **GRPO** com recompensa binária verificável (formato correto e rótulo certo). Não há custo assimétrico de FP/FN nem penalidade de tokens. São 8.000 passos de 48 prompts × 16 rollouts. A base é o Nemotron-3-Nano-30B, um MoE com 3B ativos.
  - Um calibrador separado (LoRA, rank 32) lê o raciocínio completo. Um juiz de confiança sem treino zera o recall de alta confiança. A acurácia de teste é de 82,6%.
- **Relevância para o Investigador (inferência):**
  - É o caso mais próximo de **RL aplicado à triagem de SOC**, embora sem ferramentas. Se o Investigador precisar de probabilidades para decidir por custo (ver Elkan, [E-19]), a confiança deve vir de um calibrador ou de uma pontuação própria, e não do logprob do rótulo depois do raciocínio.
  - O orçamento de RL do artigo está ordens de grandeza acima do que cabe num M1 Max.

### [E-3] Mustafa, Trad, Chehab (2025). Leveraging Large Language Models for Reducing False Positives and Prioritizing Alerts in Intrusion Detection Systems. AINA 2025, LNDECT 248, pp. 432–443, Springer.
Link: https://api.crossref.org/works/10.1007/978-3-031-87772-8_37 (metadados). Dissertação precursora: https://scholarworks.aub.edu.lb/items/4020f743-b0bf-4391-9934-93ed02fbb918/full · Status: revisado por pares (conferência). Dissertação: mestrado, AUB, 2024 · Verificado: os metadados e a dissertação foram abertos. **O texto do capítulo é NÃO VERIFICADO**, porque o Springer exige login e o ResearchGate retornou 403.
- **Contribuição (pela dissertação):**
  - Constrói um grafo de execução por processo Windows alertado e o transforma em texto com o "Graph Contextualizer", para treinar classificadores TP/FP. Os dados são cerca de 700 casos de um SOC real.
  - Compara 7 modelos com menos de 7B. O TinyLlama ficou em primeiro (F2 0,99) e o DistilBERT teve P 0,917 e R 0,97. O teste tem cerca de 108 casos, sem intervalo de confiança.
- **Relevância para o Investigador (inferência):**
  - O contexto de processo (cadeia pai/filho) é exatamente o tipo de evidência que o Investigador buscaria com ferramentas, em vez de recebê-lo pré-montado.
  - A amostra pequena e privada faz deste trabalho um indício fraco, não uma baseline.

### [E-4] Zhang, Meng, Li, Tan, Zhang (2025). Large Language Models powered Malicious Traffic Detection: Architecture, Opportunities and Case Study. arXiv:2503.18487. E Li et al. (2024). DoLLM. arXiv:2405.07638.
Links: https://arxiv.org/abs/2503.18487, https://arxiv.org/html/2503.18487, https://arxiv.org/abs/2405.07638 · Status: preprints. O campo de comentários do 2503.18487 diz só "accepted", sem nomear o venue · Verificado em 25/11/2026.
- **Contribuição:**
  - Descreve três papéis para o LLM no tráfego de rede: classificador, codificador e preditor. O estudo de caso é a detecção de DDoS do tipo carpet-bombing, com fluxos sequencializados e um tokenizer aprendível que projeta os fluxos no espaço do Llama2-7B, com uma MLP por cima.
  - O F1 supera XGBoost, AutoEncoder, LSTM e Transformer. Os números divergem entre os dois artigos (ver afirmação 4).
- **Relevância para o Investigador (inferência):**
  - Baixa. É uma modalidade (NetFlow) e um paradigma (embedding de entrada) diferentes. Serve só como referência para codificar contexto não textual.

### [E-5] Bertiger, Filar, Luthra, Meschiari, Mitchell, Scholten, Sharath (2025). Evaluating LLM Generated Detection Rules in Cybersecurity. CAMLIS 2025 (preprint no arXiv:2509.16749).
Link: https://arxiv.org/abs/2509.16749 (HTML: https://arxiv.org/html/2509.16749) · Status: aceito na CAMLIS 2025, conferência aplicada. A versão lida é o preprint · Verificado em 25/11/2026.
- **Contribuição:**
  - Propõe uma avaliação por holdout: cada regra humana sai da base de conhecimento, e o ADÉ reescreve a regra a partir de um exemplo verdadeiro-positivo. São cerca de 45 mil e-mails em 14 dias e 11 regras relatadas.
  - Usa três métricas: precisão ajustada por detecções únicas, custo por pass@k (US$1,51 a US$5,13 por regra) e robustez como 1 menos a fragilidade. Os autores prometem abrir o benchmark, mas não há URL.
- **Relevância para o Investigador (inferência):**
  - O "custo até passar" pass@k é um precedente de métrica econômica para agentes de segurança. O retro-hunt também é um análogo da validação em dados históricos antes de promover uma política.

### [E-6] Saju, Azim (2026). Toward Autonomous SOC Operations: End-to-End LLM Framework for Threat Detection, Query Generation, and Resolution in Security Operations. PMLR 318 (Canadian AI 2026), pp. 422–433. arXiv:2604.27321.
Links: https://arxiv.org/abs/2604.27321, https://arxiv.org/html/2604.27321, https://proceedings.mlr.press/v318/saju26a.html · Status: revisado por pares. O PMLR tem o mesmo título, os mesmos autores e o mesmo FPR de 0,120, mas a página não nomeia os modelos · Verificado em 25/11/2026.
- **Contribuição:**
  - Combina por voto um ensemble de 3 LLMs para classificar severidade crítica ou não crítica (os números estão na afirmação 6). Também gera consultas para QRadar e SecOps (SQM) e faz resolução apoiada por evidência.
- **Relevância para o Investigador (inferência):**
  - Não sustenta o uso de ensembles de SLMs para cortar o FPR pela metade. A geração de consultas presa à sintaxe da plataforma é útil para desenhar ferramentas de consulta seguras.

### Grupo B — Agentes de SOC treinados com RL ou com recompensa sensível a custo

### [E-7] Zloof, Shuster, Zilberman, Frydman, Singh, Murilo, Shabtai, Elovici, Puzis (2026). I2C-GRPO: Insight Importance Checklist for Reinforcement Learning in a Multi-Agent DDoS Alert Triage Workflow. arXiv:2611.17534.
Link: https://arxiv.org/abs/2611.17534 (HTML: https://arxiv.org/html/2611.17534) · Status: preprint. O HTML usa um template de periódico (*Applied Soft Computing*), mas o arXiv não tem journal-ref · Verificado em 25/11/2026.
- **Contribuição:**
  - Treina com **GRPO** só o agente de triagem (Qwen3-4B-Instruct-2507), num fluxo de 4 agentes. Os outros consultam um banco de PCAP indexado e um Neo4j somente-leitura via Cypher. O problema é tratado como **bandit contextual de um passo** sobre prefixos fixos gerados pelo GPT-5-mini (off-policy).
  - A recompensa mede a cobertura de um checklist de "insights" ranqueados por um painel de LLMs, com um Gemma 4 31B como avaliador. No teste fora do domínio (CSE-CIC-IDS2018, média de 3 seeds), o F1 foi de 0,869 e o FPR de 4,9%, contra 16,4% do GPT-5-mini.
  - Os autores admitem que a recompensa é **insensível a custo**: não pune achados redundantes nem perguntas extras. O código ainda vai ser liberado.
- **Relevância para o Investigador (inferência):**
  - Mostra que GRPO com um modelo de 4B é viável para triagem com ferramentas, e o formato bandit sobre prefixos barateia os rollouts, o que interessa no Mac.
  - O CSE-CIC-IDS2018 também está no dataset do Guardião (reserva de validação de 14/02/2018), então há risco de sobreposição de família.

### [E-8] Barnes (2026). OpenSec: Measuring Incident Response Agent Calibration Under Adversarial Evidence. arXiv:2601.21083.
Links: https://arxiv.org/abs/2601.21083, https://arxiv.org/html/2601.21083, https://github.com/jbarnes850/opensec-env · Status: preprint · Verificado em 25/11/2026.
- **Contribuição:**
  - É um ambiente de RL de "controle duplo", compatível com OpenEnv: o defensor investiga logs em SQLite enquanto um atacante roteirizado avança na kill chain, e há evidências com injeção de prompt. A recompensa determinística soma atribuição (+1 por campo certo, −0,5 por desconhecido), contenção (+1 por ação certa, **−0,5 por FP**), injeção (−2 por violação) e eficiência (−0,1 por passo). A assimetria não foi testada por ablação. São 160 seeds de treino e 60 de avaliação.
  - Com modelos de fronteira, o GPT-5.2 conteve 100% dos episódios com 82,5% de FP, e o Sonnet 4.5 conteve 62,5% com 45% de FP.
  - No apêndice A, o Qwen3-4B treinado com **GDPO** num A100 terminou com FP de 0,70 e entregou relatório em só 25% dos episódios. Não há baseline sem treino. O autor conclui que RL direto nessa recompensa composta não basta e sugere aquecimento com SFT e currículo.
- **Relevância para o Investigador (inferência):**
  - É o único precedente público de recompensa com penalidade de FP, custo por passo e injeção, e serve de alerta sobre RL multicomponente num modelo pequeno.
  - As ações de contenção não fazem parte do escopo somente-leitura do Investigador.

### [E-9] Ghifiardi, Rachman (2026). Constraint-Aware Evaluation of Reinforcement Learning and Unsupervised Anomaly Detection for Security Operations Alert Triage. arXiv:2611.05746.
Link: https://arxiv.org/abs/2611.05746 · Status: preprint · Verificado (só o resumo) em 25/11/2026.
- **Contribuição:**
  - Formaliza a triagem como decisão sob restrição: capacidade dos analistas, custos de erro desiguais e limite de escalonamento de benignos. Compara RL offline sobre embeddings de alertas, Isolation Forest e autoencoder em 74.909 alertas de produção rotulados por analistas, com split temporal.
  - A fração de benignos escalados foi de 0,000 (RL), 0,007 (AE) e 0,041 (IF). O resumo não diz se a restrição entra no objetivo de treino.
- **Relevância para o Investigador (inferência):**
  - Modelar o problema como "escalar sob restrição de carga" em vez de classificação é coerente com a recompensa planejada, e a métrica de "fração de benignos escalados" vale reportar.

### [E-10] Vallabhaneni, Cagwin, Wild (2026). SENTINEL-RL: Offloading Topological Reasoning from LLM Agents in the Security Operations Center. arXiv:2609.04159.
Link: https://arxiv.org/abs/2609.04159 · Status: preprint · Verificado (só o resumo) em 25/11/2026.
- **Contribuição:**
  - Uma política **PPO** escolhe entre ações investigativas restritas a partir de um estado codificado por GAT do grafo de autenticação, com dados LANL. O LLM só narra as recomendações, e um crítico as revisa. No hold-out, a precisão foi de 0,91 e o recall de 0,87.
- **Relevância para o Investigador (inferência):**
  - É uma alternativa de arquitetura: RL num controlador pequeno, com o LLM só como redator. Isso sugere uma ablação "política de consulta aprendida contra LLM que decide sozinho".

### [E-11] Wang et al. (2025). Acting Less is Reasoning More! Teaching Model to Act Efficiently (OTC-PO). arXiv:2504.14870.
Link: https://arxiv.org/abs/2504.14870 · Status: o arXiv não lista venue. Os resultados de busca apontam NeurIPS 2025, mas a página da NeurIPS não foi aberta: **NÃO VERIFICADO** · Verificado (arXiv) em 25/11/2026.
- **Contribuição:**
  - A recompensa combina acerto e número de chamadas de ferramenta em relação ao mínimo necessário. Foi implementada em PPO e GRPO, e o artigo define "tool productivity" como acertos por chamada. Em QA com Qwen-2.5, as chamadas caíram até 68,3% e a produtividade subiu até 215,4%, com acurácia comparável.
- **Relevância para o Investigador (inferência):**
  - Dá a forma da penalidade de chamadas desnecessárias. Em SOC, porém, cortar chamadas pode agravar o viés de busca vazia [E-1], então a penalidade deve valer só quando a decisão está certa, e nunca abaixo de um mínimo de evidência.

### [E-12] Liu, Wang (2026). HESP: Separating What to Probe from When to Stop in Local LLM Alert-Triage Agents. arXiv:2609.33446.
Link: https://arxiv.org/abs/2609.33446 · Status: preprint · Verificado (só o resumo) em 25/11/2026. O código está em github.com/lzwhehe/HESP, mas o repositório e a licença são **NÃO VERIFICADOS**.
- **Contribuição:**
  - Um controlador externo ao LLM mantém hipóteses concorrentes, escolhe probes somente-leitura por ganho de informação por custo e decide quando parar. Foram 7.272 episódios auditados com modelos de 7B a 72B. O Qwen2.5-7B subiu de 0,125 para 1,000 em conclusão verificada, e o Llama-3.1-8B subiu de 0 para 0,917 com a parada feita pelo controlador. Não há treino.
- **Relevância para o Investigador (inferência):**
  - Separa duas falhas que a recompensa precisa medir à parte: o que consultar e quando parar. Também serve de baseline sem RL para modelos locais.

### [E-13] Wei et al. (2025). CORTEX: Collaborative LLM Agents for High-Stakes Alert Triage. arXiv:2510.00311.
Links: https://arxiv.org/abs/2510.00311, https://arxiv.org/html/2510.00311 · Status: preprint · Verificado em 25/11/2026.
- **Contribuição:**
  - Usa agentes de comportamento, evidência e raciocínio com ferramentas como `getUserRecord`, `getAssetRecord`, `searchBehaviorEvents` e `runStructuredQuery`. O FPR foi de 14,2%, contra 24,9% de um agente único com ferramentas. Os autores dizem liberar "milhares de traces" de investigação, mas **sem URL nem licença**. Não há RL.
- **Relevância para o Investigador (inferência):**
  - O vocabulário de ferramentas de usuário e ativo cobre o contexto organizacional que falta ao ALERT-BENCH (§VII de [E-1]). Os traces seriam ótimos para SFT de aquecimento, mas não estão disponíveis.

### [E-14] Muzammil, Reddy, Kamalakrishnan, Ahmadi, Ul Hassan (2026). Effective and Efficient Threat Hunting with Small Language Models. RAID 2026 (arXiv:2512.06660).
Link: https://arxiv.org/abs/2512.06660 · Status: o arXiv indica RAID 2026, revisado por pares · Verificado (só o resumo) em 25/11/2026.
- **Contribuição:**
  - Gera KQL com SLMs. O fine-tuning LoRA com raciocínio **não superou** o prompting. Um SLM rascunha e um LLM barato refina, chegando a 0,987 de sintaxe e 0,906 de acurácia com schema válido, a um custo 9,5 a 14 vezes menor que GPT-4o ou GPT-5.
- **Relevância para o Investigador (inferência):**
  - Se as ferramentas aceitarem consultas livres, um modelo de 4B tende a errar a sintaxe. Ferramentas parametrizadas, como no ALERT-BENCH, reduzem esse ruído de recompensa.

### [E-15] Zhao et al. (2025). Information-Dense Reasoning for Efficient and Auditable Security Alert Triage (AIDR). arXiv:2512.08169.
Link: https://arxiv.org/abs/2512.08169 · Status: preprint · Verificado (só o resumo) em 25/11/2026.
- **Contribuição:**
  - Comprime as cadeias de raciocínio e usa especialistas LoRA locais com saída em JSON pronto para SOAR. Relata 68% menos tokens e 40,6% menos latência que o CoT.
- **Relevância para o Investigador (inferência):**
  - Oferece uma alternativa ao custo de tokens na recompensa: comprimir o raciocínio por supervisão em vez de penalizar por RL.

### Grupo C — Operações cibernéticas autônomas com RL (defensores azuis)

### [E-16] TTCP CAGE (2024). CAGE Challenge 4 sobre CybORG (Standen et al., 2022).
Links: https://github.com/cage-challenge/cage-challenge-4, https://github.com/cage-challenge/CybORG · Status: repositórios de desafio. O artigo da AAAI 2025 (Kiely et al.) retornou bloqueio de bot e o da AI Magazine retornou 403: **ambos NÃO VERIFICADOS** · Verificado (repositórios) em 25/11/2026.
- **Contribuição:**
  - Tem 5 agentes azuis em rede segmentada, com missão em 3 fases. A recompensa é **só de penalidades**: falha de trabalho de usuários "green", falha de acesso a serviço e impacto ou acesso do red. Os pesos mudam com a fase, por exemplo −10 na zona crítica durante a missão ativa.
  - As ações têm duração em ticks: Monitor 1, Analyse 2, Remove 3, Restore 5. As ações disruptivas custam indiretamente por bloquear os green, que também **geram falsos alertas**.
  - A avaliação usa 100 episódios de 500 passos contra um red de estado finito. O CybORG tem licença MIT. O CC4 traz um LICENSE.txt cujo tipo não verifiquei.
- **Relevância para o Investigador (inferência):**
  - Modela o "custo de ação" como dano à disponibilidade, e não como um custo fixo. Para o Investigador somente-leitura, o equivalente é o custo do escalonamento falso, que consome tempo de analista, e não a chamada em si.

### [E-17] Wolk et al. (2022). Beyond CAGE: Investigating Generalization of Learned Autonomous Network Defense Policies. Workshop RL4RealLife, NeurIPS 2022 (arXiv:2211.15557).
Link: https://arxiv.org/abs/2211.15557 · Status: workshop revisado por pares · Verificado em 25/11/2026.
- **Contribuição:**
  - Testa hierarquia, ensemble, máscara de ações e transferência no CAGE 2. O desempenho **caiu diante de um atacante não visto no treino**, mesmo sendo esse atacante menos eficiente.
- **Relevância para o Investigador (inferência):**
  - Políticas treinadas tendem a sobreajustar ao "estilo" dos ataques do ambiente. É preciso reservar cenários e famílias de ataque inteiros para teste, e não só alertas.

### [E-18] Bates, Mavroudis, Hicks (2023). Reward Shaping for Happier Autonomous Cyber Security Agents. arXiv:2310.13565.
Link: https://arxiv.org/abs/2310.13565 · Status: o arXiv não lista venue. Os resultados de busca apontam um registro ACM (DOI 10.1145/3605764.3623916, pp. 221–232), mas o venue não foi confirmado numa página aberta: **venue NÃO VERIFICADO** · Verificado (arXiv) em 25/11/2026.
- **Contribuição:**
  - Os agentes de deep RL em defesa de rede são sensíveis à magnitude das penalidades e à proporção entre elas. O artigo testa recompensas positivas somadas às penalidades e curiosidade intrínseca, que parece pouco útil em monitoramento de alto nível.
- **Relevância para o Investigador (inferência):**
  - A razão c_FN/c_FP e o peso do custo de ferramenta vão mudar o comportamento aprendido, não só a métrica. Convém pré-registrar duas ou três razões e reportar todas.

### [E-19] Ambientes ACO adicionais: CyberBattleSim (Microsoft, 2021), Yawning Titan (Dstl, 2022) e o survey de Palmer et al. (2023/2024).
Links: https://github.com/microsoft/CyberBattleSim, https://github.com/dstl/YAWNING-TITAN, https://arxiv.org/abs/2310.07745 · Status: repositórios (MIT nos dois); survey em preprint de 89 páginas · Verificado em 25/11/2026.
- **Contribuição:**
  - O CyberBattleSim é uma simulação abstrata de movimento lateral. O defensor padrão é estocástico ("scan and reimage") e tem uma restrição de SLA (`maintain_sla`). Os autores apontam espaços de ação grandes e falta de memória como desafios. O Yawning Titan é só defensivo, em grafo, e foi **arquivado em 13/03/2025**.
  - O survey lista dimensionalidade, ações multidiscretas e explorabilidade adversarial como problemas em aberto. O NASim (https://github.com/Jjschwartz/NetworkAttackSimulator, MIT) é ofensivo e foi descartado.
- **Relevância para o Investigador (inferência):**
  - Nenhum desses ambientes usa logs nem LLM. Servem de referência conceitual (SLA como restrição de disponibilidade), não de ambiente de treino.

### Grupo D — Aprendizado sensível a custo em IDS

### [E-20] Elkan (2001). The Foundations of Cost-Sensitive Learning. IJCAI 2001.
Link: https://cseweb.ucsd.edu/~elkan/rescale.pdf · Status: revisado por pares · Verificado em 25/11/2026 (PDF convertido localmente).
- **Contribuição:**
  - Define condições de "razoabilidade" para a matriz de custos. Do ponto de vista da decisão, uma matriz 2×2 tem **um só grau de liberdade**, que é o limiar ótimo (eq. 2). O texto extraído da equação ficou ilegível; na forma usual, p* = (c10 − c00) / (c10 − c00 + c01 − c11).
  - Prova como rebalancear o treino para mudar o limiar efetivo, mas recomenda treinar com a distribuição real e **decidir explicitamente com probabilidades estimadas**.
- **Relevância para o Investigador (inferência):**
  - Se o Relato traz uma probabilidade calibrada, o custo FP/FN pode ficar no limiar, sem retreinar. A recompensa de RL pode cuidar só do custo de investigação. A calibração depois do CoT é justamente o problema de [E-2].

### [E-21] Lee, Fan, Miller, Stolfo, Zadok (2002). Toward Cost-Sensitive Modeling for Intrusion Detection and Response. Journal of Computer Security 10(1–2):5–22.
Link: https://www.fsl.cs.sunysb.edu/docs/cost-jcs-lee/jcs_lee.pdf · Status: revisado por pares · Verificado em 25/11/2026 (PDF convertido localmente).
- **Contribuição:**
  - Separa custo de dano (DCost), de resposta (RCost) e operacional (OpCost). Define o custo consequente por desfecho: FN custa DCost, FP custa RCost mais uma penalidade, TP custa RCost mais o dano parcial já ocorrido, e TN custa 0.
  - Só vale responder quando RCost ≤ DCost. Os valores de DCost e RCost são atribuídos por categoria da taxonomia do DARPA 1998 (Tab. 1). O **custo operacional de extrair atributos** entra no modelo.
- **Relevância para o Investigador (inferência):**
  - O OpCost é o análogo direto do custo de chamadas de ferramenta. A matriz consequente dá uma forma justificável para a recompensa, com dano dependente da severidade e resposta proporcional.

### [E-22] Axelsson (2000). The Base-Rate Fallacy and the Difficulty of Intrusion Detection. ACM TISSEC 3(3):186–205.
Link: https://www.profsandhu.com/cs6393_s20/p186-axelsson.pdf · Status: revisado por pares · Verificado em 25/11/2026 (PDF convertido localmente).
- **Contribuição:**
  - Com bases realistas, o fator que limita um IDS é a taxa de falsos alarmes, e não a de detecção. Nas premissas do artigo, um P(intrusão | alarme) de cerca de 66% exige uma taxa de falso alarme da ordem de 1×10⁻⁵ (§5.3).
- **Relevância para o Investigador (inferência):**
  - A avaliação deve ocorrer em prevalência realista (5,93% no wardbeck, 18% no russellmitchell) e reportar a precisão do escalonamento, e não só o F1 balanceado.

*Não aberto:* Gaffney & Ulvila (2001), "Evaluation of intrusion detectors: a decision theory approach", IEEE S&P. Só o registro bibliográfico apareceu numa busca: **NÃO VERIFICADO**.

### Grupo E — Benchmarks e ambientes

### [E-23] Wu et al. (2026). ExCyTIn-Bench: Evaluating LLM agents on Cyber Threat Investigation. ICML 2026, PMLR 306:136937–136980 (arXiv:2507.14201).
Links: https://arxiv.org/abs/2507.14201, https://arxiv.org/html/2507.14201, https://proceedings.mlr.press/v306/wu26bd.html, https://github.com/microsoft/SecRL, https://huggingface.co/datasets/anandmudgerikar/excytin-bench, https://huggingface.co/datasets/anandmudgerikar/excytin-bench/blob/main/TRANSPARENCY_DOC.md, https://github.com/microsoft/ACESEvals · Status: revisado por pares (ICML 2026) · Verificado em 25/11/2026.
- **Contribuição:**
  - Usa 8 incidentes de ataque simulados no tenant de demonstração "Alpine Ski House" (logs de agosto de 2024) e 57 tabelas Sentinel em MySQL. A introdução fala em 59 tabelas. Em média, cada incidente tem 45 tabelas, 364,7 mil linhas e 0,447 GB; o log completo de 44 dias tem 61 tabelas, 14,3 milhões de linhas e 18 GB. São 7.542 perguntas geradas de grafos de investigação; o HF expõe 418 de treino e 589 de teste. As ações são SQL livre ou envio de resposta, com até 25 passos. A recompensa é 1 para resposta certa, ou crédito parcial por passos intermediários com decaimento γ=0,4, e quem julga é o **GPT-4o**.
  - Os melhores modelos foram Claude-Opus-4.5 (0,606) e GPT-5.1 (0,582). Entre os abertos: Qwen-3-32B 0,182 e Phi-4-14B 0,085. Modelos de 7–8B foram omitidos porque se pareciam com o Phi-4.
  - Houve só um fine-tune **preliminar** do GPT-4o, que foi de 0,293 para 0,298 em média e **piorou nos incidentes reservados** (38: de 0,364 para 0,091; 34: de 0,293 para 0,241). O RL fica como trabalho futuro. Não achei sucessor com resultado de RL publicado.
  - O README do SecRL indica o ACESEvals para benchmark e treino com RLVR (nota de 26/08/2026). A página do ACES, porém, descreve só avaliação: rótulo "use for fine-tuning" no conjunto de treino e o gpt-5.4 com 0,813, ou 0,886 com raciocínio alto.
- **Relevância para o Investigador (inferência):**
  - É o melhor ambiente **pronto e executável**, com perguntas investigativas multi-passo e recompensa verificável. Mas é QA de ataque, não triagem: não há alertas benignos nem veredito por alerta, então não mede FP. Serve para testar se a política de consulta generaliza, não para a recompensa de triagem.

### [E-24] Debenedetti et al. (2024). AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. NeurIPS 2024 D&B (segundo o BibTeX do repositório; o arXiv não lista venue).
Links: https://arxiv.org/abs/2406.13352, https://github.com/ethz-spylab/agentdojo · Status: o BibTeX indica revisão por pares; o arXiv está na v3 · Verificado em 25/11/2026.
- **Contribuição:**
  - Tem 97 tarefas e 629 casos de segurança com ataques e defesas extensíveis, sob licença MIT. A API ainda está instável, segundo o README.
- **Relevância para o Investigador (inferência):**
  - Serve de modelo para uma suite própria em que o "Registro não confiável" traz injeções dentro dos resultados das ferramentas. Não há tarefas de SOC prontas.

### [E-25] Wang et al. (2026). CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale. ICLR 2026 (segundo o BibTeX do repositório; arXiv:2506.02548).
Link: https://github.com/sunblaze-ucb/cybergym · Status: o BibTeX indica revisão por pares; a página do arXiv não foi aberta · Verificado (repositório) em 25/11/2026.
- **Contribuição:**
  - O agente reproduz vulnerabilidades com PoC verificado por exit codes nas versões vulnerável e corrigida. A licença é Apache-2.0, e o benchmark tem cerca de 240 GB de dados (cerca de 10 TB no servidor completo).
- **Relevância para o Investigador (inferência):**
  - Baixa. É uma tarefa ofensiva e o tamanho é incompatível com a regra de não baixar arquivos grandes e com o Mac.

### [E-26] SecAlertBench (sem autores nem venue confirmados na página).
Link: https://github.com/Dxsssu/SecAlertBench · Status: repositório com o artigo associado ("SecAlertBench: Evaluating LLMs for Tier-1 Alert Triage in SOCs"); **venue NÃO VERIFICADO** · Verificado em 25/11/2026.
- **Contribuição:**
  - São 8.322 alertas de IDS/IPS e WAF de 3 SOCs empresariais (2.496 de ataque), com rótulo binário por alerta. Os IPs foram aleatorizados e os timestamps removidos. Com 16 LLMs, o FPR médio foi de 44,13%. A licença não foi declarada.
- **Relevância para o Investigador (inferência):**
  - É uma baseline single-shot externa para o Guardião, sobretudo em WAF. Sem ferramentas e sem timestamps, não serve para investigação.

### [E-27] Landauer et al. (2022/2023). AIT Log Data Set V2.0 e AIT Alert Data Set (AIT-ADS).
Links: https://zenodo.org/records/5789064, https://zenodo.org/records/8263181 · Status: datasets publicados. O artigo do AIT-ADS não foi aberto · Verificado em 25/11/2026.
- **Contribuição:**
  - O AIT-LDSv2 tem 8 cenários e 130,6 GB comprimidos, sob **CC BY-NC-SA 4.0**. O AIT-ADS tem 2.655.821 alertas Wazuh, Suricata e AMiner (96,2 MB), sob **CC BY 4.0**, com `labels.csv` marcando as janelas das fases de ataque.
- **Relevância para o Investigador (inferência):**
  - É a base que permite **reconstruir o ALERT-BENCH localmente** com os dados já baixados. A cláusula NC limita uso comercial de derivados, o que importa para consultoria, e a cláusula SA vale para qualquer dataset derivado publicado.

### [E-28] Benchmarks adjacentes sem uso direto: CTI-REALM (Chakraborty et al., 2026, arXiv:2603.13517) e SOC-bench (Cai et al., 2026, arXiv:2603.28998).
Links: https://arxiv.org/abs/2603.13517, https://arxiv.org/abs/2603.28998 · Status: preprints · Verificado (resumos) em 25/11/2026.
- **Contribuição:**
  - O CTI-REALM avalia geração de regras KQL e Sigma a partir de relatórios de CTI, com recompensa de trajetória (Opus 4.6 com 0,637). Está disponível como domínio do ACES.
  - O SOC-bench é só um desenho conceitual de 5 tarefas azuis num cenário de ransomware, sem código.
- **Relevância para o Investigador (inferência):**
  - Nenhum dos dois tem veredito por alerta. O SOC-bench mostra que ainda falta um benchmark azul multitarefa executável.

---

## 3. Ambientes candidatos

| Nome | Licença | Disponível? | Ferramentas | Ground truth | Riscos |
|---|---|---|---|---|---|
| **ExCyTIn-Bench** (microsoft/SecRL) | Código MIT. Dados: o card do HF diz CDLA-Permissive-2.0, mas o TRANSPARENCY_DOC diz MIT e "research purposes only" (**conflito**) | Sim. MySQL 9.0 em Docker com 8 containers: cerca de 10 GB para 8 incidentes e cerca de 33 GB com todos os ataques. 418 perguntas de treino e 589 de teste no HF | SQL livre sobre ~57 tabelas Sentinel e envio de resposta; até 25 passos | Por **pergunta** (resposta e caminho no grafo), com crédito parcial γ=0,4 julgado pelo GPT-4o. Sem veredito por alerta e **sem benignos** | Juiz LLM externo, o que adiciona custo e ruído na recompensa. É QA, não triagem. Público desde 2025; os autores afirmam ausência no pré-treino, mas não mediram. O fine-tune sobreajustou aos incidentes de treino. 8 containers MySQL não cabem no Colima de 2 GiB (inferência) |
| **ACES / ACESEvals**, domínio Excytin | MIT | Sim. Usa inspect_ai e Docker, com cerca de 280 MB de dados baixados na primeira execução | `sql_query` via react ou ponte MCP | O mesmo do ExCyTIn. Modo "insane" sem tabelas de alerta | Exige endpoint de LLM compatível com OpenAI. A página não documenta pipeline de RL |
| **ALERT-BENCH** (Tsegai et al.) | **Não liberado.** Insumos: AIT-LDSv2 CC BY-NC-SA 4.0 e AIT-ADS CC BY 4.0 | **Não.** Nenhum repositório encontrado; é reconstruível com Wazuh e AIT | 4 ferramentas MCP somente-leitura (alertas por regra/host/janela, busca por entidade, agregação, padrões raros) e inventário de hosts | **Por alerta** (ataque ou benigno) via rotulagem por evento do AIT-ADS. 1.247 alertas no russellmitchell e 337 no wardbeck | **Contaminação alta com o Guardião.** **Correção de 26/11/2026:** o `validacao.json` da v12 põe os oito cenários nos splits. Treino: fox, russellmitchell, wardbeck, wheeler e wilson. Validação: santos e shaw. Teste: harrison. Não há cenário livre (ADR 0007). Licença NC. Falta contexto organizacional. Público desde 2022 |
| **OpenSec** | Código sem licença declarada. Seeds no HF com licença não verificada | Sim. Python ≥3.11 e SQLite; a avaliação usa OpenRouter | `query_logs`, `fetch_email`, `fetch_alert`, `submit_report` e também **ações de contenção** (`isolate_host`, `block_domain`, `reset_user`) | Por episódio (seed com verdade e linha do tempo). Recompensa determinística com FP −0,5, injeção −2 e passo −0,1 | Kill chain estreita (phish, credencial, movimento lateral, exfiltração). Seeds provavelmente sintéticos. Licença indefinida. O RL preliminar não melhorou |
| **AgentDojo** | MIT | Sim (pip) | Ferramentas das suites (e-mail, banco, viagem); formato **NÃO VERIFICADO** | Checagem de utilidade e de segurança por tarefa (97 tarefas e 629 casos) | Fora do domínio de SOC; exige uma suite própria; API instável |
| **CyberGym** | Apache-2.0 | Tecnicamente sim, mas com cerca de 240 GB | Repositório vulnerável e submissão de PoC | Exit codes nas versões vulnerável e corrigida | Tarefa ofensiva; tamanho inviável; pertinência baixa |
| **SecAlertBench** | Não declarada | Sim (GitHub) | Nenhuma (classificação estática) | Rótulo binário por alerta (8.322) | Sem ferramentas, sem timestamps e com IPs aleatorizados; anotação não descrita |
| **CTI-REALM** | Via ACES (MIT); o arXiv não tem link próprio | Parcial (via ACES) | KQL, ATT&CK e Sigma | Detecções esperadas e recompensa de trajetória | Outra tarefa (geração de regras); centrado em Azure |
| **CybORG / CAGE 4** | CybORG MIT; LICENSE.txt do CC4 com tipo não verificado | Sim | Ações discretas de rede (Monitor, Analyse, Remove, Restore, Block e Decoy) | Penalidades por fase (impacto do red, disrupção dos green) | Abstrato, sem logs e sem LLM; vale só como referência de recompensa |
| **HESP** (ambiente controlado) | Código no GitHub, licença **NÃO VERIFICADA** | Declarado no arXiv (repositório não aberto) | Probes somente-leitura | Episódios auditados | O resumo não descreve o ambiente |
| **CORTEX** (traces) | Não encontrada | **Não** (sem URL) | `getUserRecord`, `getAssetRecord`, `searchBehaviorEvents`, `runStructuredQuery` | Adjudicação final do analista por trace | Indisponível |

**Melhor candidato (inferência):**
1. **Para treinar:** reconstruir um ambiente no estilo ALERT-BENCH sobre o AIT-ADS e o AIT-LDSv2, que já estão locais. É o único caminho com veredito por alerta, benignos reais, ferramentas somente-leitura e as mesmas modalidades do Guardião (Suricata e Wazuh/auth). **Correção de 26/11/2026:** não há cenário livre. O treino usa os cenários do split de treino da v12, a seleção usa santos e shaw, e a avaliação usa harrison (ADR 0007).
2. **Para generalização externa:** o ExCyTIn-Bench via ACES, que é o melhor ambiente pronto e revisado por pares.
3. **Para injeção:** uma suite no estilo AgentDojo, ou o OpenSec com as ações de contenção desligadas.

---

## Lacunas observadas

1. **Não encontrei trabalho publicado que treine, com RL, um agente LLM de investigação de SOC com recompensa sensível a custo (FP/FN assimétrico e custo de ferramenta) sobre telemetria de SIEM.** Os mais próximos são:
   - o I2C-GRPO, com recompensa insensível a custo, só DDoS e formato bandit off-policy;
   - o OpenSec, cujo RL é preliminar e não reduziu FP;
   - Khanna et al., que usam GRPO sem ferramentas e com recompensa binária;
   - o SENTINEL-RL, cuja política PPO não é um LLM.
2. **Falta um ambiente liberado que tenha ao mesmo tempo veredito por alerta, alertas benignos e SIEM executável.** O ALERT-BENCH não foi liberado. O código do I2C-GRPO foi prometido, e os traces do CORTEX não têm URL. O ExCyTIn é executável, mas não tem benignos.
3. **A contaminação não foi medida** em nenhum dos ambientes. O AIT-LDS é público desde 2022 e o ExCyTIn desde 2025. No ALERT-BENCH, a sobreposição de cenários com o dataset do Guardião é um risco concreto deste projeto.
4. **A calibração de agentes com ferramentas não foi estudada.** O único estudo de calibração pós-CoT [E-2] é de um classificador sem ferramentas, e mesmo ele não mede ECE.
5. **Modelos pequenos foram pouco avaliados em triagem agêntica.** O Llama 3.1 8B fracassou (0,098) e o Qwen3.5 9B foi bem (0,952), ambos no AIDA. O **Gemma 4 E4B não foi testado** em nenhum ambiente encontrado.
6. A literatura de operações cibernéticas autônomas usa simuladores abstratos. A transferência de suas lições de reward shaping para agentes LLM que leem logs não foi demonstrada.
7. **Itens não verificados:**
   - o texto do capítulo AINA 2025 (paywall);
   - os artigos do CC4 na AAAI 2025 e na AI Magazine (bloqueio e 403);
   - a página do OpenReview do Alert-Bench (verificação de navegador);
   - Gaffney & Ulvila (2001);
   - o venue de OTC-PO e de Bates et al.;
   - a licença do HESP e o formato das ferramentas do AgentDojo.

## O que isso implica para o desenho do Investigador

*Tudo nesta seção é inferência a partir das fontes acima.*

1. **Recompensa em duas camadas.** O custo FP/FN deve ficar numa matriz explícita, no estilo de Lee et al. [E-21]: dano por severidade, custo de escalonamento falso e TN igual a 0. O custo de investigação deve ser um termo à parte, como o OpCost [E-21] ou o OTC [E-11]. Convém pré-registrar duas ou três razões c_FN/c_FP, porque a política muda com elas [E-18], e reportar o custo esperado no ponto de operação, além do F1 [E-22].
2. **Punir descarte sem evidência.** Um descarte só deve receber recompensa integral quando citar registros realmente recuperados. Uma busca vazia não conta como evidência de benignidade [E-1, §IV-C]. A penalidade de chamadas deve valer só para decisões corretas e só acima de um mínimo de consultas, para não incentivar descartes rápidos.
3. **Nada de revisão no mesmo contexto.** O Self-Refine e o CoVe pioraram a triagem [E-1]. Se houver um verificador, ele deve ter contexto separado e decidir com base no ledger de evidências, como o Judge do AIDA, cuja remoção custou cerca de 0,057 de F1 no subconjunto.
4. **Separar decisão de confiança.** O logprob do rótulo depois do raciocínio não é confiável [E-2]. Para usar o limiar de Elkan [E-20], o Relato precisa de uma probabilidade treinada (calibrador ou pontuação própria). Sem isso, o "risco de falso positivo" do contrato vira texto livre.
5. **Viabilidade no M1 Max.** O RL on-policy com rollouts de ferramenta é caro: Khanna usou 8.000 passos × 768 rollouts. Um caminho prático é o seguinte:
   - aquecer com SFT ou rejection sampling sobre trajetórias do professor;
   - fazer GRPO em formato bandit sobre prefixos fixos [E-7];
   - deixar o RL completo para o Colab;
   - rodar um incidente ou cenário por vez para respeitar o Colima de 2 GiB, ou exportar as tabelas para SQLite ou DuckDB (inferência).
6. **Ferramentas parametrizadas, não consultas livres.** Use o padrão de 4 ferramentas MCP do ALERT-BENCH, somente-leitura e com a janela ancorada no alerta. Modelos de 4B erram a sintaxe de consultas livres [E-14], e isso polui a recompensa. Trate toda saída de ferramenta como "Registro não confiável" e teste injeção [E-8, E-24].
7. **Avaliação e contaminação.**
   - Treine nos cenários AIT do split de treino da v12, selecione em santos e shaw e avalie em harrison. **Correção de 26/11/2026:** santos está na validação da v12, não reservado (ADR 0007).
   - Reporte russellmitchell e wardbeck à parte, só para comparar com o AIDA, marcando que estão contaminados se o Investigador partir do Guardião.
   - Use o ExCyTIn como teste fora da distribuição para a política de consulta.
   - Reserve cenários e famílias de ataque inteiros, e não alertas soltos [E-17, E-23].
8. **Baselines obrigatórias:**
   - o Guardião single-shot;
   - um Direct-Prompt com 3 chamadas, a melhor das 5 abordagens no ALERT-BENCH;
   - um controlador externo sem treino, no estilo HESP [E-12].
   O ganho do RL precisa superar essas três a custo igual.
9. **Não usar a afirmação 6.** Não há evidência de que um ensemble de SLMs corte o FPR pela metade. Se ensembles entrarem no estudo, devem ser uma hipótese própria, com o custo de inferência somado.
