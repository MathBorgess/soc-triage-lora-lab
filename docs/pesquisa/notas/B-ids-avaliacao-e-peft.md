# Tema B — ML para detecção de intrusão, armadilhas de avaliação e fine-tuning eficiente

> Revisão feita em 2026-11-25 por Claude Code (modelo `claude-opus-5-5`, subagente de pesquisa).
> Escopo: o projeto `soc-triage-lora-lab` e a fase "Guardião". Não li o repositório nem a wiki `mathai-wiki`; o contexto veio só do briefing.
> Convenções: "Verificado: sim" quer dizer que abri a URL citada nesta sessão. Venue e ano vêm dessa página. Quando o venue vem só do campo *comments* do arXiv, a entrada diz isso.
> Os números das fontes aparecem no formato original, com ponto decimal. Os bullets "Relevância" são **inferências** minhas, não afirmações das fontes.

---

## 1. Armadilhas de ML em segurança e em IDS

### [B-1] Sommer, R.; Paxson, V. (2010). Outside the Closed World: On Using Machine Learning for Network Intrusion Detection. 2010 IEEE Symposium on Security and Privacy (S&P).
- Link: https://www.icir.org/robin/papers/oakland10-ml.pdf (texto completo) · https://archive.cps-vo.org/node/15082 (metadados, DOI 10.1109/SP.2010.25). Status: peer-reviewed. Verificado: sim. A página do IEEE Xplore não carregou, então o venue saiu do registro CPS-VO.
- Contribuição:
  - Argumenta que a detecção de anomalias por ML quase não é usada em operação real, porque achar ataques é um problema diferente dos casos em que o ML funciona bem. O ML é bom em achar coisas parecidas com o que já viu, não ataques realmente novos.
  - Lista cinco características do domínio: custo de erro muito alto, falta de dados de treino, *semantic gap* entre a saída e sua interpretação operacional, variabilidade enorme da entrada e dificuldade de fazer avaliação sólida.
  - Propõe diretrizes para pesquisas futuras em detecção de anomalias.
- Relevância para o Guardião (inferência):
  - O Relato com Evidência literal e o rationale atacam o *semantic gap*. A classe `expected_admin` trata a variabilidade do benigno. A FPR como métrica central segue o argumento do custo de erro.
  - O artigo deve evitar dizer que o modelo "detecta ataques novos". Melhor descrever a tarefa como triagem de padrões e reportar à parte o desempenho em grupos de cenário nunca vistos.

### [B-2] Arp, D.; Quiring, E.; Pendlebury, F.; Warnecke, A.; Pierazzi, F.; Wressnegger, C.; Cavallaro, L.; Rieck, K. (2022). Dos and Don'ts of Machine Learning in Computer Security. 31st USENIX Security Symposium.
- Link: https://www.usenix.org/conference/usenixsecurity22/presentation/arp · https://arxiv.org/abs/2010.09470 · https://dodo-mlsec.org/ (lista dos pitfalls, site dos autores). Status: peer-reviewed (a página da USENIX indica Distinguished Paper Award). Verificado: sim.
- Contribuição:
  - Define dez pitfalls: sampling bias, label inaccuracy, data snooping, spurious correlations, biased parameter selection, inappropriate baseline, inappropriate performance measures, base rate fallacy, lab-only evaluation e inappropriate threat model.
  - Analisa 30 artigos de conferências de segurança de primeira linha, publicados em 10 anos, e conclui que os pitfalls são comuns. Uma análise empírica mostra como cada um gera resultados irreais.
  - Dá recomendações para cada pitfall e lista problemas em aberto.
- Relevância para o Guardião (inferência):
  - O rival (rank 8, 30 iterações, Macro-F1 0,954 em 55 exemplos sintéticos da mesma família do treino) cai em *lab-only evaluation* e *sampling bias*. Medir a superioridade só no teste real segue essa recomendação diretamente.
  - Pitfalls que ainda estão abertos no protocolo: *inappropriate baseline* (faltam baselines simples, como TF-IDF+LR e regras, no teste real); *base rate fallacy* (o teste usa a proporção de desenho 45/45/10, não a prevalência de um SOC); *spurious correlations* (IDs pseudonimizados, nomes de host e cenários podem virar atalhos).

### [B-3] Pendlebury, F.; Pierazzi, F.; Jordaney, R.; Kinder, J.; Cavallaro, L. (2019). TESSERACT: Eliminating Experimental Bias in Malware Classification across Space and Time. 28th USENIX Security Symposium, pp. 729–746.
- Link: https://www.usenix.org/conference/usenixsecurity19/presentation/pendlebury · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Mostra que F1 perto de 0.99 em classificação de malware Android vem de dois vieses. O viés espacial é uma distribuição de treino e teste que não representa o uso real. O viés temporal é um split no tempo que cria configurações impossíveis.
  - Propõe restrições de espaço e tempo, uma métrica de robustez esperada no uso real e a avaliação de mitigações de *time decay*, como active learning.
  - Avalia três classificadores em 129K aplicativos coletados em três anos. O desempenho reportado antes estava enviesado.
- Relevância para o Guardião (inferência):
  - O split por grupo de incidente evita vazamento entre splits, mas **não** controla o viés temporal. Onde houver datas, vale um hold-out temporal ou por fonte, com cenários mais recentes ou de fonte não vista no teste.
  - A proporção 45/45/10 é uma escolha de desenho. Ela produz viés espacial se for lida como desempenho operacional, então convém reportar também a precisão projetada para prevalências realistas.

### [B-4] Engelen, G.; Rimmer, V.; Joosen, W. (2021). Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study. IEEE Security and Privacy Workshops (SPW) 2021, pp. 7–12.
- Link: https://imec-publications.be/entities/publication/de3203e3-50c3-4fc3-b93e-065b1bf16765/full (metadados, DOI 10.1109/SPW53761.2021.00009) · https://lirias.kuleuven.be/retrieve/713070 (PDF, abstract). Status: peer-reviewed (workshop; o nome do arquivo indica WTMC). Verificado: sim
- Contribuição:
  - Reexamina o CICIDS2017 e seu pipeline de coleta. Acha problemas na geração de tráfego, na construção de fluxos, na extração de features e na rotulagem.
  - Depois da correção, mais de 20% dos traces originais foram reconstruídos ou rerrotulados. Os benchmarks de ML no dataset corrigido mudam bastante.
  - Recomenda formas de prever e evitar esses problemas de coleta.
- Relevância para o Guardião (inferência):
  - Sustenta a decisão de curar à mão e conferir IoCs contra o log bruto. Rótulos herdados de fontes públicas (Mordor, EVTX-ATTACK-SAMPLES, opensec-triage) não devem ser aceitos sem auditoria.
  - Para o artigo de governança, registrar a proveniência do rótulo em cada exemplo (herdado, corrigido ou criado) é uma contribuição auditável.

### [B-5] Flood, R.; Engelen, G.; Aspinall, D.; Desmet, L. (2024). Bad Design Smells in Benchmark NIDS Datasets. 9th IEEE European Symposium on Security and Privacy (EuroS&P).
- Link: https://detlearsom.github.io/pubs/BadSmells-EuroSP24-finaldraft.pdf (texto) · https://detlearsom.github.io/ (venue; distinguished paper award). Status: peer-reviewed. Verificado: sim. O venue saiu da página do grupo dos autores; o IEEE Xplore não carregou.
- Contribuição:
  - Analisa à mão sete datasets de NIDS muito citados e acha seis *data design smells*: pouca diversidade de dados, features muito dependentes entre si, ground truth pouco clara, colapso de tráfego, diversidade artificial e rótulos errados. Para cada smell, propõe uma heurística que mede sua prevalência.
  - Exemplos concretos: ataques contra portas fechadas, rótulos vazando por features e milhões de fluxos quase duplicados. Também revisa 38 artigos que usam esses datasets e mostra que os smells podem minar resultados publicados.
- Relevância para o Guardião (inferência):
  - Os smells *diversidade artificial* e *rótulo vazando por features* descrevem bem o opensec-triage, cujo card admite que TF-IDF+LR acerta 100% de um split. As heurísticas podem virar checagens no script de auditoria do dataset: quase-duplicatas entre splits, sondas de vazamento de rótulo e diversidade por modalidade.

### [B-6] Layeghy, S.; Gallagher, M.; Portmann, M. (2021). Benchmarking the Benchmark — Analysis of Synthetic NIDS Datasets. arXiv.
- Link: https://arxiv.org/abs/2104.09029 · Status: preprint. A página lista o DOI relacionado 10.1016/j.jisa.2023.103689, o que sugere publicação em periódico, mas não confirmei. Verificado: sim
- Contribuição:
  - Compara estatísticas do tráfego benigno de três datasets sintéticos de NIDS com dois reais (rede universitária e ISP de porte médio).
  - Os dois reais se parecem entre si, e os três sintéticos também. Porém a maioria das features difere bastante entre os dois grupos, então o desempenho medido em sintéticos pode não se transferir para redes reais.
- Relevância para o Guardião (inferência):
  - Apoia o teto de sintéticos e a decisão de medir só no teste real. Antes de misturar, vale medir a distância de distribuição entre Recortes sintéticos e reais (comprimento, campos presentes, vocabulário por modalidade) e reportá-la no artigo.

### [B-7] Le, V.-H.; Zhang, H. (2022). Log-based Anomaly Detection with Deep Learning: How Far Are We? 44th International Conference on Software Engineering (ICSE 2022).
- Link: https://arxiv.org/abs/2202.04301 · Status: peer-reviewed (venue tirado do campo *comments* do arXiv). Verificado: sim
- Contribuição:
  - Reavalia cinco modelos de deep learning em quatro datasets públicos de log. Muitos desses modelos reportavam F-measure acima de 0.9 no HDFS.
  - Mostra que cinco fatores mudam muito os resultados: a seleção dos dados de treino, o agrupamento dos dados, a distribuição de classes, o ruído e a detecção precoce. Nenhum modelo vai bem em todas as condições.
- Relevância para o Guardião (inferência):
  - O "Recorte" (janela que termina na linha-âncora) é uma escolha de agrupamento. Convém uma análise de sensibilidade ao tamanho da janela e à escolha da âncora, além de métricas por modalidade (sysmon, linux_auth, apache, suricata, waf).
  - Reportar a distribuição de classes do teste por modalidade é condição para comparar com o rival.

### [B-8] Atif, M. E.; Ali, M. H. (2026). A Three-Axis Stress Test of LLM vs Classical ML for Network Intrusion Detection under Distribution Shift and Adversarial Evasion. arXiv.
- Link: https://arxiv.org/abs/2609.13511 · Status: preprint (recente, sem revisão por pares) · Verificado: sim
- Contribuição:
  - Compara XGBoost e RoBERTa-LoRA em duas redes NetFlow v2 coletadas de forma independente. Os dois empatam no mesmo dataset.
  - Na troca de dataset, o XGBoost vence por 15 pontos de F1 e 25 de balanced accuracy. O RoBERTa-LoRA chega a FPR de 0.78 na rede-alvo, apesar de um F1 moderado. Na evasão adversarial, o RoBERTa-LoRA vence por cerca de 17 pontos de F1.
  - Uma ablação de vazamento de features mostra que o sinal de vazamento está espalhado pela representação, e que a transferência entre as redes depende muito da direção.
- Relevância para o Guardião (inferência):
  - É evidência direta de que paridade no mesmo dataset pode esconder um colapso de FPR sob mudança de distribuição. Isso reforça a FPR em `benign`/`expected_admin` no teste real e sugere uma avaliação cruzada por fonte (treinar em algumas fontes, testar em fonte retida).
  - Ressalva: o modelo é um encoder com LoRA, não um LLM gerativo com saída JSON.

## 2. Fine-tuning eficiente (PEFT)

### [B-9] Hu, E. J.; Shen, Y.; Wallis, P.; Allen-Zhu, Z.; Li, Y.; Wang, S.; Wang, L.; Chen, W. (2022). LoRA: Low-Rank Adaptation of Large Language Models. ICLR 2022 (poster).
- Link: https://arxiv.org/abs/2106.09685 · https://iclr.cc/virtual/2022/poster/6319 · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Congela os pesos pré-treinados e injeta matrizes treináveis de baixo rank em cada camada do Transformer.
  - Comparado ao fine-tuning completo do GPT-3 175B com Adam, reduz os parâmetros treináveis em 10.000 vezes e a memória de GPU em 3 vezes, sem latência extra na inferência. Iguala ou supera o fine-tuning completo em RoBERTa, DeBERTa, GPT-2 e GPT-3.
- Relevância para o Guardião (inferência):
  - A configuração clássica (LoRA em query e value, citada como prática padrão em [B-10]) é a da Run 1. Logo, Run 1 contra Run 2 replica uma comparação conhecida, em vez de testar uma hipótese nova.

### [B-10] Dettmers, T.; Pagnoni, A.; Holtzman, A.; Zettlemoyer, L. (2023). QLoRA: Efficient Finetuning of Quantized LLMs. NeurIPS 2023 (Main Conference Track).
- Link: https://arxiv.org/abs/2305.14314 · https://proceedings.neurips.cc/paper_files/paper/2023/hash/1feb87871436031bdc0f2beaa62a049b-Abstract-Conference.html · Status: peer-reviewed · Verificado: sim (li o texto do PDF)
- Contribuição:
  - Introduz NF4, double quantization e paged optimizers, o que permite fazer fine-tuning de 65B numa GPU de 48 GB. O texto relata mais de 1.000 modelos treinados.
  - Seção 4 e Figura 2: LoRA só em query/value **não** replica o fine-tuning completo. LoRA em todas as camadas lineares do bloco é necessário. O Apêndice A diz que o rank r não se relaciona com o desempenho final quando todas as camadas são adaptadas.
  - Com NF4, o QLoRA 4-bit iguala o fine-tuning completo 16-bit e o LoRA 16-bit em benchmarks acadêmicos.
- Relevância para o Guardião (inferência):
  - Prevê Run 2 > Run 1, Run 2 ≈ Run 3 e pouco efeito de r na Run 4. A matriz vira um teste de replicação dessas afirmações numa tarefa de saída estruturada em segurança, com modelo de cerca de 4B.
  - **Cautela:** a paridade 4-bit foi mostrada com NF4 (bitsandbytes). A quantização 4-bit do MLX usa outro esquema (inferência minha sobre a stack). A paridade pode não se transferir, e o artigo deve dizer isso.

### [B-11] Liu, S.-Y.; Wang, C.-Y.; Yin, H.; Molchanov, P.; Wang, Y.-C. F.; Cheng, K.-T.; Chen, M.-H. (2024). DoRA: Weight-Decomposed Low-Rank Adaptation. ICML 2024 (Oral).
- Link: https://arxiv.org/abs/2402.09353 · Status: peer-reviewed (venue tirado do campo *comments* do arXiv) · Verificado: sim
- Contribuição:
  - Decompõe cada peso pré-treinado em magnitude e direção e aplica LoRA só na direção, buscando a capacidade do fine-tuning completo com mais estabilidade.
  - Supera o LoRA de forma consistente em LLaMA, LLaVA e VL-BART, em raciocínio de senso comum, instruction tuning visual e tarefas de imagem/vídeo-texto.
- Relevância para o Guardião (inferência):
  - Não há evidência para saída JSON estrita nem para segurança. Espera-se ganho pequeno, e uma única seed (42) não basta para separar efeitos pequenos de ruído. As rodadas DoRA/QDoRA precisam de várias seeds ou de intervalos de confiança.

### [B-12] Meng, F.; Wang, Z.; Zhang, M. (2024). PiSSA: Principal Singular Values and Singular Vectors Adaptation of Large Language Models. NeurIPS 2024 (spotlight).
- Link: https://arxiv.org/abs/2404.02948 · Status: peer-reviewed (venue tirado do campo *comments* do arXiv) · Verificado: sim
- Contribuição:
  - Inicializa A e B com os valores e vetores singulares principais de W. O resíduo fica congelado, e a convergência é mais rápida que no LoRA. O teste cobre 12 modelos de 184M a 70B.
  - No GSM8K, o Mistral-7B chega a 72.86% com PiSSA contra 67.7% com LoRA. O QPiSSA tem erro de quantização menor que o QLoRA no começo do treino: o LLaMA-3-70B chega a 86.05% contra 81.73%.
- Relevância para o Guardião (inferência):
  - O PiSSA muda a base (W vira resíduo + componentes principais). O adaptador não vale sobre os pesos originais. Para auditar, é preciso versionar o modelo residual, o procedimento de SVD e sua seed.
  - Como o QPiSSA reduz o erro de quantização, o efeito do PiSSA interage com o eixo 4-bit/BF16. A rodada PiSSA precisa fixar a precisão de forma explícita, senão o efeito fica confundido.

### [B-13] Biderman, D.; Portes, J.; Gonzalez Ortiz, J. J.; Paul, M.; Greengard, P.; Jennings, C.; King, D.; Havens, S.; Chiley, V.; Frankle, J.; Blakeney, C.; Cunningham, J. P. (2024). LoRA Learns Less and Forgets Less. Transactions on Machine Learning Research (TMLR), Featured Certification.
- Link: https://arxiv.org/abs/2405.09673 · https://arxiv.org/html/2405.09673v2 · Status: peer-reviewed (venue tirado do campo *comments* do arXiv) · Verificado: sim
- Contribuição:
  - Em código e matemática, com instruction fine-tuning (cerca de 100K pares) e continued pretraining (20B tokens), o LoRA rende menos que o fine-tuning completo, mas esquece menos. Também esquece menos que weight decay e dropout.
  - Seção 4.7: adaptar só a atenção rende menos que MLP ou "all", e a maior parte do ganho vem do MLP. As recomendações são α = 2r e varrer o learning rate (o melhor LR do LoRA fica cerca de uma ordem de grandeza acima do do fine-tuning completo).
  - O desempenho segue o rank: em Code IFT, r=16 chega a HumanEval 0.358 contra 0.498 com r=256. A perturbação do fine-tuning completo tem rank 10 a 100 vezes maior que as configurações típicas de LoRA.
- Relevância para o Guardião (inferência):
  - Confirma Run 2 (all-linear) como referência. `scale: 2.0` equivale a α/r = 2 se o MLX multiplica a saída do LoRA por `scale` (inferência sobre a stack), o que segue a recomendação α = 2r.
  - **Desafia a Run 4 como está:** o LR ótimo depende do rank. Sem ajustar o LR por rank no valid, o efeito de r fica confundido com o LR. Os dados do artigo (100K pares) são muito maiores que 1.147 exemplos, então extrapolar o ganho de rank alto é incerto.

### [B-14] Shi, Z.; Yang, A. X.; Wu, B.; Aitchison, L.; Yilmaz, E.; Lipani, A. (2024). Instruction Tuning With Loss Over Instructions. NeurIPS 2024.
- Link: https://arxiv.org/abs/2405.14394 · Status: peer-reviewed (venue tirado do campo *comments* do arXiv) · Verificado: sim
- Contribuição:
  - Propõe Instruction Modelling (IM), que aplica a loss também à instrução e ao prompt. Testa em 21 benchmarks.
  - O ganho é maior quando as instruções são longas e as saídas curtas, e quando há poucos exemplos (regime da Superficial Alignment Hypothesis). Os autores atribuem o ganho a menos overfitting. No melhor caso, o resultado no AlpacaEval 1.0 mais que dobra.
- Relevância para o Guardião (inferência):
  - O projeto tem entrada longa (janela de log + prompt versionado), saída JSON relativamente curta e cerca de 1,1k exemplos, justamente as condições em que o IM ajudou. Usar `mask_prompt: true` em **todas** as rodadas pode não ser o ponto ótimo. O controle pareado com `mask_prompt: false` tem justificativa na literatura e deveria ter prioridade.
  - Hipótese a testar: a loss sobre o log pode aumentar a memorização de IDs e IoCs do treino. Medir a alucinação de IoC nas duas condições.

### [B-15] Huerta-Enochian, M.; Ko, S. Y. (2024). Instruction Fine-Tuning: Does Prompt Loss Matter? EMNLP 2024.
- Link: https://arxiv.org/abs/2401.13586 · Status: peer-reviewed (venue tirado do campo *comments* do arXiv, versão camera-ready) · Verificado: sim
- Contribuição:
  - Estuda o prompt loss weight (PLW). Com dados de completions curtas, o desempenho tem relação quadrática negativa e estatisticamente significativa com o PLW.
  - PLW pequeno (cerca de 0.01 a 0.5) foi melhor em múltipla escolha e geração curta. PLW perto de 1 foi melhor em geração longa. Os autores criticam a remoção do parâmetro na API da OpenAI.
- Relevância para o Guardião (inferência):
  - A comparação binária `mask_prompt` true/false testa só os extremos (PLW 0 contra 1), e o ótimo pode estar no meio. Se a stack MLX não aceita PLW fracionário, isso deve constar como limitação. Não está claro se a saída JSON do Guardião conta como completion "curta" ou "longa".

## 3. LLMs especializados em segurança e LLMs para triagem/IDS

### [B-16] Xu, H.; Wang, S.; Li, N.; Wang, K.; Zhao, Y.; Chen, K.; Yu, T.; Liu, Y.; Wang, H. (2024/2025). Large Language Models for Cyber Security: A Systematic Literature Review. ACM Transactions on Software Engineering and Methodology (TOSEM), aceito.
- Link: https://arxiv.org/abs/2405.04760 · Status: peer-reviewed (aceito, conforme o campo *comments* do arXiv v5, set. 2025) · Verificado: sim (só o abstract)
- Contribuição:
  - Coleta mais de 40.000 artigos e analisa 185 de venues de segurança e engenharia de software.
  - Mapeia aplicações (detecção de vulnerabilidades, análise de malware, detecção de intrusão de rede), tendências por arquitetura (encoder, encoder-decoder, decoder) e técnicas de adaptação (fine-tuning, prompting, augmentation externa), além do crescimento de agentes.
- Relevância para o Guardião (inferência):
  - Serve para posicionar o trabalho relacionado. Não verifiquei no texto completo se o survey trata de armadilhas de avaliação, que seria a lacuna a explorar no artigo.

### [B-17] Kassianik, P.; Saglam, B.; Chen, A.; Nelson, B.; Vellore, A.; et al. (2025). Llama-3.1-FoundationAI-SecurityLLM-Base-8B Technical Report. arXiv.
- Link: https://arxiv.org/abs/2504.21039 · https://arxiv.org/html/2504.21039 · Status: relatório técnico (preprint) · Verificado: sim
- Contribuição:
  - Foundation-Sec-8B: continued pretraining do Llama 3.1-8B num corpus de segurança de cerca de 5.1B tokens (Figura 2 e Seção 3.3).
  - Na Tabela 1, contra o Llama 3.1-8B: +6.26% em CTIBench-MCQA, +14.29% em CTIBench-RCM, 0.0% em CyberMetric-500 e −1.63% em SecBench. Chega perto do Llama 3.1-70B em algumas tarefas.
  - O relatório não descreve descontaminação dos benchmarks contra o corpus, só deduplicação interna por n-gramas.
- Relevância para o Guardião (inferência):
  - O pré-treino de domínio dá ganhos irregulares, e os benchmarks de múltipla escolha não medem triagem de log. Isso apoia a escolha de uma base geral com LoRA da tarefa.
  - Para a fase 7–8B em nuvem, é uma base candidata. Antes, é preciso checar a contaminação com fontes públicas de log.

### [B-18] Khanna, A.; Nandan, M.; Popa, C. V.; et al. (2026). Cybersecurity Detection Classification with Reasoning-enabled Language Models. arXiv.
- Link: https://arxiv.org/abs/2607.28460 · Status: preprint · Verificado: sim (só o abstract; a página não mostra afiliações)
- Contribuição:
  - Treina um classificador de triagem com chain-of-thought sobre detecções reais de endpoint Windows rotuladas por humanos. Usa otimização automática de prompt, self-training e RL com recompensas verificáveis. Um modelo de 30B ajustado chega a 82.6% de acurácia no teste.
  - O CoT degrada as probabilidades do token de rótulo usadas na triagem automática. Por isso os autores treinam um calibrador separado que lê o raciocínio inteiro.
  - No ponto de alta confiança, o recall benigno sobe 43.0% e o malicioso 18.3% em relação a um classificador de rótulo direto. Um juiz de confiança sem treino leva o recall de alta confiança a zero. O modelo ajustado supera modelos de fronteira de uso geral.
- Relevância para o Guardião (inferência):
  - O Guardião gera rationale e veredito juntos. A ordem dos campos no JSON (veredito antes ou depois do rationale) pode afetar a calibração do veredito, e isso merece ser medido.
  - O artigo não reporta FPR, então o foco do projeto em FPR no benigno é um diferencial. O resultado apoia a tese de treino direcionado em vez de escala.

## 4. Benchmarks e avaliação de LLMs em tarefas de SOC/CTI

### [B-19] Alam, M. T.; Bhusal, D.; Nguyen, L.; Rastogi, N. (2024). CTIBench: A Benchmark for Evaluating LLMs in Cyber Threat Intelligence. NeurIPS 2024, Datasets and Benchmarks Track.
- Link: https://proceedings.neurips.cc/paper_files/paper/2024/hash/5acd3c628aa1819fbf07c39ef73e7285-Abstract.html · https://arxiv.org/html/2406.07599v3 · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Cinco tarefas:
    - CTI-MCQ: cerca de 2.500 questões geradas pelo GPT-4o e revisadas à mão.
    - CTI-RCM: 1.000 CVEs de 2024, mapeando CVE para CWE.
    - CTI-VSP: 1.000 CVEs, prevendo o vetor CVSS v3, com avaliação por MAD.
    - CTI-ATE: 60 malwares, extração de técnicas com Micro-F1.
    - CTI-TAA: 50 relatórios, atribuição de ator.
  - Escolhe amostras posteriores ao cutoff dos modelos para reduzir contaminação. Na CTI-TAA, a maioria dos modelos foi melhor em relatórios anteriores ao cutoff, o que os autores leem como sinal de memorização.
  - O ChatGPT-4 liderou CTI-MCQ (71.0%) e CTI-RCM (72.0%). Os modelos tendem a superestimar o CVSS, e prompts de raciocínio não melhoraram a CTI-MCQ de forma consistente.
- Relevância para o Guardião (inferência):
  - A CTI-RCM é a referência externa mais próxima da Hipótese de vulnerabilidade (CWE de lista fechada). Porém CVEs de 2024 provavelmente são anteriores ao cutoff do Gemma 4, o que traz risco de contaminação.
  - O desenho "pós-cutoff" serve de modelo: reservar parte do teste a logs e cenários publicados depois do cutoff da base.

### [B-20] Deason, L.; et al. (23 autores, incluindo Saxe, J. e Krasser, S.) (2025). CyberSOCEval: Benchmarking LLMs Capabilities for Malware Analysis and Threat Intelligence Reasoning. arXiv (parte do CyberSecEval 4).
- Link: https://arxiv.org/abs/2509.20166 · https://arxiv.org/html/2509.20166v2 · Status: preprint · Verificado: sim
- Contribuição:
  - Malware Analysis: 609 pares pergunta-resposta tirados de relatórios do Hybrid Analysis (detonações reais no CrowdStrike Falcon Sandbox). As perguntas foram geradas pelo Llama 3.2 90B e validadas por especialistas. A acurácia fica entre cerca de 23% e 34%.
  - Threat Intelligence Reasoning: 588 pares tirados de 45 relatórios, com acurácia entre cerca de 43% e 53%. Modelos de raciocínio com test-time scaling ganham menos aqui que em código e matemática.
  - A Seção 5.4 admite que modelos Llama podem ser favorecidos, porque as perguntas foram geradas por modelos da mesma família. O artigo não discute contaminação de treino.
- Relevância para o Guardião (inferência):
  - Mostra o risco de viés do gerador. Se exemplos sintéticos ou juízes vêm de uma família próxima da base (Gemma), a comparação fica enviesada. Registrar o modelo gerador de cada sintético é requisito de auditoria.
  - Os escores absolutos baixos de modelos grandes indicam que Macro-F1 alto de um modelo de 4B no próprio teste exige controles fortes antes de ser comparado entre estudos.

### [B-21] Mezzi, E.; Massacci, F.; Tuma, K. (2025). Large Language Models Are Unreliable for Cyber Threat Intelligence. arXiv.
- Link: https://arxiv.org/abs/2503.23175 · https://arxiv.org/html/2503.23175v2 · Status: preprint. A página lista um DOI Springer relacionado (10.1007/978-3-032-00627-1_17), mas não confirmei o venue. Verificado: sim
- Contribuição:
  - Avalia GPT-4o, Gemini-1.5-pro e Mistral-large-2 em 350 relatórios de CTI, com zero-shot, few-shot e fine-tuning, medindo consistência e confiança. Os modelos são inconsistentes e confiantes demais em relatórios de tamanho real.
  - Tabela 6 (gpt4o): o fine-tuning piorou a calibração na maioria das entidades. Na geração de CVE, o ECE/Brier foi de 0.15/0.29 (zero-shot) para 0.91/0.98 (fine-tuned). Na extração de CVE, melhorou (0.28 para 0.18).
- Relevância para o Guardião (inferência):
  - O fine-tuning pode aumentar a acurácia e piorar a calibração. Se o "risco de falso positivo" do Guardião for um número ou uma categoria, ele precisa de métrica de calibração (ECE/Brier ou curva risco-cobertura) por rodada, não só de validade no schema.

## 5. Dados sintéticos para treino

### [B-22] Li, Z.; Zhu, H.; Lu, Z.; Yin, M. (2023). Synthetic Data Generation with Large Language Models for Text Classification: Potential and Limitations. EMNLP 2023.
- Link: https://arxiv.org/abs/2310.07849 · Status: peer-reviewed (venue tirado do campo *comments* do arXiv) · Verificado: sim (só o abstract)
- Contribuição:
  - Dados sintéticos gerados por LLM têm eficácia irregular entre tarefas de classificação de texto.
  - A subjetividade, tanto da tarefa quanto da instância, tem associação negativa com o desempenho de modelos treinados com dados sintéticos.
- Relevância para o Guardião (inferência):
  - Separar `suspicious` de `benign` e de `expected_admin` depende do contexto, ou seja, é subjetivo. Os sintéticos tendem a ajudar menos justamente nas classes que definem a FPR. Isso apoia o teto 1:1 e sugere uma ablação da proporção (0, 0.25, 0.5, 1:1) medida só no valid real.
  - Ressalva: o estudo não é de segurança, e eu li só o abstract.

---

## Fontes abertas e não incluídas como entrada (limite de 22)

- Apruzzese, G. et al. *The Role of Machine Learning in Cybersecurity*. ACM DTRAP v.4, DOI 10.1145/3545574 (https://arxiv.org/abs/2206.09707; metadados de venue via https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3545574). Semente verificada. Visão geral do descompasso entre pesquisa e prática, com dois estudos de caso industriais.
- Kapoor, S.; Narayanan, A. *Leakage and the reproducibility crisis in machine-learning-based science*. Patterns 4(9):100804, 2023 (https://collaborate.princeton.edu/en/publications/leakage-and-the-reproducibility-crisis-in-machine-learning-based-/). Taxonomia de 8 tipos de vazamento e "model info sheets". Útil para a seção de governança do artigo.
- Wu, Y. et al. *ExCyTIn-Bench*. ICML 2026, PMLR v.306 (https://proceedings.mlr.press/v306/wu26bd.html). 57 tabelas de log, 7.542 perguntas e melhor recompensa de 0.606. O ground truth fica ancorado em grafos de investigação, num desenho parecido com o da Evidência literal.
- Yu, Y.-C. et al. *Primus: A Pioneering Collection of Open-Source Datasets for Cybersecurity LLM Training*. EMNLP 2025 (https://arxiv.org/abs/2502.11191). +15.9% agregado em benchmarks depois do pré-treino contínuo.
- Tihanyi, N. et al. *CyberMetric* (https://arxiv.org/abs/2402.07688). Preprint; questões geradas pelo GPT-3.5 com RAG e cerca de 200 h de validação humana.
- Goldschmidt, P.; Chudá, D. *Network Intrusion Datasets: A Survey, Limitations, and Recommendations*. Computers & Security 156 (2025) 104510 (https://arxiv.org/abs/2502.06688). Revisão de 89 datasets de NIDS.
- Zhao, G. et al. *Information-Dense Reasoning for Efficient and Auditable Security Alert Triage* (https://arxiv.org/abs/2512.08169). Preprint; experts LoRA on-premises que geram JSON, com promessa de auditabilidade. O abstract não dá a acurácia.
- Aghaei, E. et al. *SecureBERT* (https://arxiv.org/abs/2204.02685). A página não informa o venue.
- Tejero-Fernández, J. J.; Sánchez-Macián, A. *Evaluating Language Models For Threat Detection in IoT Security Logs* (https://arxiv.org/abs/2507.02390). Preprint; o abstract não traz números.
- Não abertos, logo NÃO VERIFICADOS: SecEval, SECURE (arXiv 2405.20441, só visto em resultado de busca) e o CyberSecEval original.

## Lacunas observadas

1. **Não achei estudo revisado por pares** com LoRA/QLoRA em LLM pequeno (≤4B) para triagem multimodal de logs de SOC com saída JSON estrita, dados reais curados e split por grupo. Os trabalhos de LLM para IDS ou logs encontrados usam fluxos tabulares serializados ou datasets públicos com avaliação no mesmo dataset ([B-8] é a exceção, com encoder).
2. **Loss só na resposta em tarefas de extração estruturada:** [B-14] e [B-15] estudam benchmarks gerais. Não achei nada sobre segurança ou JSON, nem sobre o efeito da máscara na alucinação de entidades (IoCs).
3. **Calibração em triagem de SOC:** só [B-18] (30B, sem FPR) e [B-21] (CTI, modelos grandes via API). Nada com modelos pequenos locais, nem com a confiança como campo do JSON.
4. **Proporção sintético:real em fine-tuning de segurança:** não achei estudo que varie a proporção e meça no teste real. [B-6] e [B-22] só dão evidência indireta.
5. **Viés temporal em LLMs para triagem de log:** [B-3] é sobre malware Android e classificadores clássicos. Nada equivalente para LLM e logs.
6. **DoRA/PiSSA fora de benchmarks gerais:** não achei avaliação em segurança nem em saída estruturada. Também não verifiquei replicações independentes dos ganhos sobre LoRA.
7. **Detalhes de arquitetura do Gemma 4** (KV compartilhado, embeddings por camada) e onde aplicar LoRA nele: não procurei e não achei.
8. **Contaminação de fontes públicas de log** (Mordor, EVTX-ATTACK-SAMPLES, Loghub) no pré-treino de modelos abertos: não achei estudo. [B-17] não descontamina, e [B-19] só mitiga pelo cutoff.

## Controvérsias e resultados conflitantes

- **O rank importa?** [B-10] diz que r não afeta o desempenho final quando o LoRA está em todas as camadas (LLaMA, Alpaca e similares). [B-13] mostra desempenho ordenado pelo rank e r=16 insuficiente em código. Uma conciliação possível: o efeito do rank cresce com a distância de domínio e com o volume de dados. O resultado da Run 4 deve ser lido como dependente da tarefa.
- **Mascarar ou não o prompt?** A prática padrão (PLW = 0) é contestada por [B-14], que melhora com loss total em instruções longas e poucos dados, e por [B-15], que acha o ótimo com PLW pequeno, mas não zero, em completions curtas. Os dois usam benchmarks gerais, e nenhum mede alucinação de entidades.
- **4-bit sai de graça?** [B-10] relata paridade NF4 contra 16-bit. [B-12] mostra que a inicialização do QLoRA carrega erro de quantização que o QPiSSA reduz, o que dá ganho mensurável em 70B. Logo, o custo da quantização depende da inicialização e do esquema.
- **LLM contra ML clássico em IDS:** vários preprints relatam LLMs melhores que baselines no mesmo dataset (ex.: arXiv 2507.02390, não incluído). [B-8] mostra empate no mesmo dataset e derrota com FPR 0.78 sob mudança de distribuição, mas vitória sob evasão adversarial. Não há vencedor universal.
- **Pré-treino de domínio:** [B-17] tem ganhos em CTIBench, zero em CyberMetric e leve perda em SecBench. O Primus (não incluído) relata +15.9% agregado. Os ganhos dependem do benchmark escolhido, e nenhum desses benchmarks mede triagem de log.
- **Fine-tuning e calibração:** em [B-21], o fine-tuning piora a calibração na maioria das entidades e melhora em uma (extração de CVE). [B-18] diz que o CoT destrói a utilidade das probabilidades do rótulo e que é preciso um calibrador treinado.
- **Escala contra treino direcionado:** [B-20] associa modelos maiores a escores melhores. [B-18] mostra um 30B ajustado superando modelos de fronteira. As tarefas diferem, então não há contradição direta, mas os dois resultados apontam para lados opostos.

## O que confirma ou desafia as decisões do projeto

**Confirmado pela literatura**
- **Medir a superioridade só no teste real e não aceitar o 0,954 do rival:** apoiado por [B-2] (lab-only evaluation, sampling bias), [B-6] (sintético difere do real), [B-5] (diversidade artificial, vazamento de rótulo) e [B-8] (paridade no mesmo dataset esconde FPR alta sob mudança). Inferência: com n = 55, um Macro-F1 perto de 0.95 tem intervalo de confiança da ordem de ±0.06, largo demais para afirmar superioridade.
- **Split por grupo de incidente ou cenário, com hold-out fora da seleção de hiperparâmetros:** apoiado por [B-2] (data snooping) e [B-7] (o agrupamento muda os resultados). Para quase-duplicatas entre splits, ver [B-5].
- **Teto para sintéticos:** apoiado por [B-6], [B-22] e [B-5]. O card do opensec-triage (TF-IDF+LR com 100% num split) é um caso típico de atalho no sentido de [B-2] e [B-5].
- **Run 2 (all-linear) como referência:** apoiado por [B-10] e [B-13]. A Run 1 deve render menos, como prevê a literatura.
- **FPR em `benign`/`expected_admin` como métrica central e curadoria manual com conferência de IoC:** apoiado por [B-1] (custo de erro), [B-8] (colapso de FPR) e [B-4] (rótulos errados em datasets públicos).
- **Base geral + LoRA da tarefa, em vez de um LLM de segurança pré-treinado:** coerente com [B-17] (ganhos irregulares) e [B-18] (treino direcionado vence escala).

**Desafiado ou incompleto (ações concretas)**
1. **`mask_prompt: true` em todas as rodadas:** o regime do projeto (entrada longa, saída curta, cerca de 1,1k exemplos) é aquele em que [B-14] e [B-15] acham ganho com loss no prompt. O controle pareado `mask_prompt: false` deveria ter prioridade. Se a stack permitir, incluir um PLW intermediário (ex.: 0.1) e medir também a alucinação de IoC.
2. **Seed única (42) em todas as rodadas:** fixar a seed garante reprodutibilidade, não conclusões robustas. As diferenças esperadas (Run 2 contra Run 3, r8 contra r64, DoRA/PiSSA contra LoRA) são pequenas segundo [B-10], [B-11] e [B-12]. Sem 3 ou mais seeds, ou bootstrap por grupo no teste de 166 exemplos, a matriz não separa efeito de ruído. Isso também se liga a *biased parameter selection* [B-2].
3. **Run 4 com LR fixo:** [B-13] mostra que o LR ótimo muda com o rank. Ajustar o LR por rank no valid, ou declarar o confundimento.
4. **Run 3 contra Run 2 como "efeito da quantização":** além do microbatch e do checkpointing (já reconhecidos), a paridade de [B-10] vale para NF4, não para o 4-bit do MLX. E o PiSSA interage com a quantização [B-12]. A rodada PiSSA precisa fixar a precisão e versionar o modelo residual.
5. **Viés temporal e espacial não tratados:** acrescentar um hold-out por fonte e, quando possível, por tempo [B-3], [B-8]. Reportar a precisão projetada para prevalências realistas de SOC, além da FPR [B-2] (base rate fallacy). A proporção 45/45/10 não é a do mundo real.
6. **Falta baseline simples no teste real:** TF-IDF+LR e regras por modalidade, além do zero-shot (Run 0), seguindo [B-2] (inappropriate baseline). Se um baseline linear chegar perto, o ganho do LoRA está superestimado.
7. **Falta métrica de calibração:** o campo "risco de falso positivo" do Guardião precisa de ECE/Brier ou curva risco-cobertura [B-21]. Testar também a ordem dos campos (veredito antes ou depois do rationale) [B-18].
8. **Esquecimento medido só de forma qualitativa:** [B-13] tem um protocolo quantitativo. Um conjunto pequeno de perguntas gerais de segurança com gabarito reforçaria o artigo, com cuidado com a contaminação [B-19].
9. **Contaminação do zero-shot (Run 0):** fontes públicas como Mordor, EVTX e Loghub podem estar no pré-treino do Gemma 4. Reservar um subconjunto do teste com material posterior ao cutoff, no desenho de [B-19].
10. **Atalhos via pseudonimização:** se IDs pseudonimizados ou nomes de host forem estáveis dentro de um cenário, o modelo pode aprender "host X → malicioso" no treino. O split por grupo evita o vazamento para o teste, mas não o aprendizado do atalho, e o efeito aparece como queda fora do grupo. Testar com um baseline que vê só os identificadores ([B-5], vazamento de rótulo; [B-2], spurious correlations).
11. **Proveniência dos sintéticos:** registrar o modelo gerador e evitar a mesma família na avaliação ou como juiz ([B-20], viés do gerador). Medir a distância de distribuição sintético-real antes da mistura [B-6].
