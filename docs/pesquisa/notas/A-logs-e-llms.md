# Tema A — Detecção de anomalias em logs e LLMs para análise de logs

Revisão feita em 2026-11-25. Todas as URLs abaixo foram abertas nesta sessão. Venue e ano saem da página aberta: página do artigo, arXiv com `comments`/`journal-ref`, programa oficial da conferência ou primeira página do PDF. Os números vêm do resumo, salvo quando a seção ou tabela é indicada. As seções "Relevância para o Guardião" são inferências minhas, não afirmações das fontes.

Legenda de status: **peer-reviewed** quando a página indica publicação em anais ou periódico; **preprint** quando não há venue confirmada.

---

## 1. Detecção de anomalias em logs com deep learning: clássicos e críticas de avaliação

### [A-1] Du, M.; Li, F.; Zheng, G.; Srikumar, V. (2017). DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning. ACM CCS '17.
- Link: https://users.cs.utah.edu/~lifeifei/papers/deeplog.pdf · Status: peer-reviewed · Verificado: sim. A página do ACM DL retornou 403. Venue (CCS'17, Dallas) e DOI 10.1145/3133956.3134015 foram lidos na primeira página do PDF dos autores.
- Contribuição:
  - Trata a sequência de chaves de log (templates) como uma linguagem. Uma LSTM é treinada só com execuções normais, e um desvio das próximas chaves previstas é marcado como anomalia.
  - Propõe atualização incremental online e construção de workflows a partir do log para diagnóstico e causa raiz. A avaliação inclui estudos de caso com logs de segurança.
- Relevância para o Guardião (inferência):
  - DeepLog representa o paradigma "aprender o normal e detectar desvio". O Guardião é triagem supervisionada de janelas curadas, com veredito e evidência. O artigo deve declarar essa diferença para não ser comparado a benchmarks de detecção não supervisionada.
  - A dependência de parser e template é justamente o que o Recorte (projeção determinística e curada) substitui. Isso merece aparecer como decisão de desenho.

### [A-2] Zhang, X.; Lin, Q.; et al. (2019). Robust Log-based Anomaly Detection on Unstable Log Data (LogRobust). ESEC/FSE '19.
- Link: https://www.microsoft.com/en-us/research/publication/robust-log-based-anomaly-detection-on-unstable-log-data/ · Status: peer-reviewed · Verificado: sim. A página da Microsoft Research trunca a lista de autores, e o ACM DL retornou 403.
- Contribuição:
  - Mostra que logs reais são instáveis, por evolução dos logging statements e por ruído de processamento. Isso quebra a hipótese de um conjunto fixo e conhecido de eventos.
  - LogRobust representa eventos como vetores semânticos e usa uma Bi-LSTM com atenção. Foi avaliado em Hadoop e num serviço online da Microsoft. O resumo não traz números.
- Relevância para o Guardião (inferência):
  - Apoia ler o texto do log (pseudonimizado) em vez de IDs de template. A pseudonimização e as mudanças de formato entre versões de uma fonte são, porém, formas de instabilidade. Uma suíte barata de robustez seria perturbar o formato do Recorte (campos reordenados, timestamps em outro formato) e checar se o veredito se mantém.

### [A-3] Le, V.-H.; Zhang, H. (2022). Log-based Anomaly Detection with Deep Learning: How Far Are We? ICSE 2022.
- Link: https://arxiv.org/abs/2202.04301 (texto completo lido em https://ar5iv.labs.arxiv.org/html/2202.04301) · Status: peer-reviewed (aceito no ICSE 2022, segundo os comments do arXiv) · Verificado: sim
- Contribuição:
  - Avalia cinco modelos (DeepLog, LogAnomaly, PLELog, LogRobust, CNN) em HDFS, BGL, Spirit e Thunderbird. Varia a seleção do treino, o agrupamento em janelas, a distribuição de classes, o ruído e a detecção precoce, e conclui que todos esses fatores mudam significativamente os resultados.
  - Split aleatório contra cronológico (Seção 4.1, Tabela 2, janelas fixas de 1 h e split 80:20): no BGL, o F1 do DeepLog cai de 0,927 para 0,426 e o do LogAnomaly de 0,931 para 0,483. Os autores atribuem a inflação ao vazamento de eventos futuros para o treino. Os modelos supervisionados caem menos (LogRobust: 0,981 para 0,967).
  - O agrupamento importa (Seção 4.2, Tabelas 3–4). No BGL com janelas fixas de 20, 100 e 200 linhas, o F1 do DeepLog fica entre 0,227 e 0,322, e janelas de sessão (block_id no HDFS, node_id no BGL) dão resultados melhores. Com 1% de rótulos trocados no HDFS, o F1 do LogRobust cai 37,2% (Seção 4.4.1). Os autores pedem que Specificity seja relatada, porque Precision, Recall e F1 enganam sob desbalanceamento (Seção 4.3).
- Relevância para o Guardião (inferência):
  - Confirma o split por grupo de incidente ou cenário. Sugere também uma análise temporal secundária, com treino anterior e teste posterior dentro de cada fonte.
  - A política de corte do Recorte (tamanho da janela e posição da âncora) é uma variável experimental, não um detalhe de implementação. Ela deve ser registrada e, se possível, ablada. A sensibilidade a 1% de ruído de rótulo justifica a curadoria manual e uma auditoria de rótulos.

### [A-4] Landauer, M.; Onder, S.; Skopik, F.; Wurzenberger, M. (2023). Deep Learning for Anomaly Detection in Log Data: A Survey. Machine Learning with Applications, v. 12.
- Link: https://arxiv.org/abs/2207.03820 (texto lido em https://arxiv.org/html/2207.03820) · Status: peer-reviewed (journal-ref no arXiv) · Verificado: sim
- Contribuição:
  - Revisão sistemática de 62 artigos (Seção III-A2) sobre arquiteturas, pré-processamento, técnicas de detecção e avaliação. Não faz comparação quantitativa.
  - Constata que a grande maioria das avaliações usa apenas quatro datasets (IV-E1). Também nota que muitos métodos ditos não supervisionados operam na prática de forma semi-supervisionada (IV-B3) e que os rótulos do HDFS são por sessão, não por evento (IV-E2).
  - Lista 10 desafios abertos (II-B), entre eles instabilidade, desbalanceamento, disponibilidade de rótulos, logs intercalados, qualidade dos dados e explicabilidade.
- Relevância para o Guardião (inferência):
  - O campo não tem datasets de segurança multi-fonte rotulados por janela. O conjunto curado do projeto (5 modalidades, rótulo por Recorte, split por incidente) pode ser uma contribuição, ao menos como protocolo e esquema publicáveis.
  - A explicabilidade aparece como desafio aberto. Um Relato com Evidência literal verificável dá uma resposta mensurável a ele.

### [A-5] Landauer, M.; Skopik, F.; Wurzenberger, M. (2024). A Critical Review of Common Log Data Sets Used for Evaluation of Sequence-based Anomaly Detection Techniques. Proceedings of the ACM on Software Engineering (FSE 2024).
- Link: https://arxiv.org/abs/2309.02854 (texto lido em https://arxiv.org/html/2309.02854) · Status: peer-reviewed (DOI 10.1145/3660768, segundo a página do arXiv) · Verificado: sim
- Contribuição:
  - Analisa HDFS, BGL, Thunderbird, OpenStack, Hadoop e ADFA e conclui que a maioria das anomalias não se manifesta como ordem sequencial. No OpenStack, 98,5% das sequências se sobrepõem entre normais e anômalas. No Hadoop, 83,2% das sequências normais têm uma contraparte anômala idêntica (Tabela I).
  - Detectores triviais atingem F1 alto (Tabela II): no BGL, só "tipo de evento nunca visto" dá F1 médio de 98,8%. No HDFS, combinações de evento novo, comprimento e vetor de contagem chegam a 96,4–98,8%.
  - Recomenda (Seção V) entender como as anomalias se manifestam antes de usar um dataset, usar baselines simples, repetir execuções e relatar variância, relatar TNR/FPR junto do F1 e publicar splits e parâmetros.
- Relevância para o Guardião (inferência):
  - É o análogo direto do risco de "rótulo derivado do formato". Se certos tokens (EventID do Sysmon, assinatura do Suricata, regra do WAF) determinam o veredito, um baseline trivial pode igualar o LoRA. Reportar esse baseline, junto da separabilidade por TF-IDF já observada no opensec-triage, serve como diagnóstico de atalho.
  - Apoia relatar FPR em benign/expected_admin junto do Macro-F1 e relatar variância. Com a seed 42 fixa, a variância pode vir de bootstrap do teste ou de seeds extras numa análise secundária.

### [A-6] Landauer, M.; Skopik, F.; Frank, M.; Hotwagner, W.; Wurzenberger, M.; Rauber, A. (2022). Maintainable Log Datasets for Evaluation of Intrusion Detection Systems. IEEE Transactions on Dependable and Secure Computing.
- Link: https://arxiv.org/abs/2203.08580 · Status: peer-reviewed (journal-ref IEEE TDSC 2022, DOI 10.1109/TDSC.2022.3201582) · Verificado: sim. Volume e número (20(4), 2023) apareceram só em resultado de busca e não foram verificados.
- Contribuição:
  - Testbed de pequena empresa com usuários simulados por máquinas de estado e um ataque multi-etapa. A geração e a rotulagem são automáticas, por model-driven engineering, e permitem repetir o ataque com parâmetros variados.
  - Publica 8 datasets com 20 tipos de arquivos de log, dos quais 8 rotulados para 10 passos de ataque (AIT-LDS v2), com código aberto.
- Relevância para o Guardião (inferência):
  - Os datasets repetem o mesmo cenário com parâmetros diferentes. O grupo do split deve, então, ser a simulação ou o cenário, para que execuções replicadas do mesmo ataque não cruzem os splits. Isso também permite testar generalização: treino em N−1 simulações e teste na restante.
  - Os eventos benignos são simulados. Na política de mistura, AIT-LDS conta como dado semi-sintético, e não como "real" no mesmo sentido de logs de produção.

### [A-7] Zhu, J.; He, S.; He, P.; Liu, J.; Lyu, M. R. (2023). Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics. ISSRE 2023.
- Link: https://arxiv.org/abs/2008.06448 · Status: peer-reviewed (aceito no ISSRE 2023, segundo os comments do arXiv) · Verificado: sim
- Contribuição:
  - Reúne 19 datasets reais de sistemas distribuídos, supercomputadores, sistemas operacionais, mobile, aplicações servidoras e software standalone, com estatísticas, cenários de uso e benchmarks. O resumo relata cerca de 90 mil downloads.
  - É a base de fato da área (HDFS, BGL, Thunderbird), justamente a concentração que [A-4] e [A-5] criticam.
- Relevância para o Guardião (inferência):
  - Loghub é fonte candidata no projeto, mas seus logs são de confiabilidade e operação, não de intrusão. Rótulos de anomalia não equivalem a veredito de segurança. A fonte é mais útil para exemplos benign/expected_admin e para ruído do que para malicious, salvo rotulagem própria.
  - Por estar público desde 2020, há risco de os pesos base (Gemma) terem visto esses logs no pré-treino. Isso afeta a interpretação do Run 0 em exemplos derivados de Loghub.

### [A-8] Yu, B.; Yao, J.; Fu, Q.; Zhong, Z.; Xie, H.; Wu, Y.; Ma, Y.; He, P. (2024). Deep Learning or Classical Machine Learning? An Empirical Study on Log-Based Anomaly Detection. ICSE 2024.
- Link: https://conf.researchr.org/details/icse-2024/icse-2024-research-track/21/Deep-Learning-or-Classical-Machine-Learning-An-Empirical-Study-on-Log-Based-Anomaly- · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Em cinco datasets públicos, algoritmos simples (KNN, SLFN) superam métodos de deep learning (CNN, NeuralLog) em tempo e acurácia. No Thunderbird, o KNN treina 1.000 vezes mais rápido que o NeuralLog e tem F1 0,0625 maior (resumo).
  - Atribui o resultado a três causas: pré-processamento redundante, simplicidade dos datasets e natureza binária da tarefa. Propõe o LightAD, com tuning automático, para comparações justas.
- Relevância para o Guardião (inferência):
  - Reforça incluir baselines leves (TF-IDF com modelo linear, regras) ao lado dos Runs 0–4. Se o baseline leve empatar no veredito, o valor do LoRA tem de ser mostrado no que o baseline não faz: normalização em JSON, IoCs, Evidência e rationale.
  - A tarefa do projeto (4 classes, severidade e MITRE) é menos "binária" que o benchmark padrão. Esse argumento só se sustenta com o baseline medido.

### [A-9] Arp, D.; Quiring, E.; Pendlebury, F.; Warnecke, A.; Pierazzi, F.; Wressnegger, C.; Cavallaro, L.; Rieck, K. (2022). Dos and Don'ts of Machine Learning in Computer Security. 31st USENIX Security Symposium.
- Link: https://www.usenix.org/conference/usenixsecurity22/presentation/arp (PDF lido em https://www.usenix.org/system/files/sec22-arp.pdf) · Status: peer-reviewed (Distinguished Paper Award, segundo a página) · Verificado: sim
- Contribuição:
  - Define dez armadilhas (Fig. 1): viés de amostragem, rótulos imprecisos, data snooping, correlações espúrias, parâmetros enviesados, baselines inadequados, medidas inadequadas, falácia da taxa-base, avaliação só em laboratório e modelo de ameaça inadequado.
  - Na análise de 30 artigos de conferências de topo, cada artigo sofre de pelo menos três armadilhas (Introdução). O impacto é demonstrado em quatro domínios, incluindo detecção de intrusão.
  - Ao descrever o viés de amostragem (P1), cita dados sintéticos e a combinação de fontes diferentes como origens de viés.
- Relevância para o Guardião (inferência):
  - A mistura sintética 1:1 e a combinação de 5 modalidades caem em P1 e P4. Convém reportar resultados com e sem sintéticos, por fonte, e um teste de "quão bem a fonte prevê o rótulo".
  - Falácia da taxa-base (P8): o FPR medido num teste aproximadamente balanceado (45/45/10) não se traduz para a carga real de um SOC. O artigo deve converter o FPR em alertas falsos por dia sob uma prevalência declarada.

---

## 2. LLMs para logs: parsing, detecção, interpretabilidade e surveys

### [A-10] Ma, Z.; Chen, A. R.; Kim, D. J.; Chen, T.-H.; Wang, S. (2024). LLMParser: An Exploratory Study on Using Large Language Models for Log Parsing. ICSE 2024.
- Link: https://arxiv.org/abs/2404.18001 · venue: https://conf.researchr.org/details/icse-2024/icse-2024-research-track/150/LLMParser-An-Exploratory-Study-on-Using-Large-Language-Models-for-Log-Parsing · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Parser generativo com few-shot tuning, ou seja, fine-tuning em poucos logs amostrados por clustering. Usa Flan-T5-small/base, LLaMA-7B e ChatGLM-6B e relata 96% de acurácia média de parsing em 16 sistemas (resumo).
  - Modelos menores podem ser mais eficazes: Flan-T5-base iguala LLaMA-7B com inferência mais curta. Um pré-treino adicional no LLaMA reduziu a group accuracy em quase 55% (resumo).
- Relevância para o Guardião (inferência):
  - É evidência de que fine-tuning com poucos exemplos em modelo pequeno basta para saída estruturada de logs. Isso apoia a meta de 3B local e o piloto com cerca de 1.100 exemplos.
  - O efeito negativo do pré-treino adicional pede cautela com etapas extras de adaptação, como pré-treino contínuo em logs sintéticos antes do LoRA.

### [A-11] Jiang, Z.; Liu, J.; Chen, Z.; Li, Y.; Huang, J.; Huo, Y.; He, P.; Gu, J.; Lyu, M. R. (2024). LILAC: Log Parsing using LLMs with Adaptive Parsing Cache. FSE 2024.
- Link: https://arxiv.org/abs/2310.01796 · Status: peer-reviewed (aceito no FSE 2024, segundo os comments do arXiv) · Verificado: sim
- Contribuição:
  - Parsing por in-context learning, com amostragem hierárquica de demonstrações e um cache adaptativo de templates. O cache evita consultas repetidas e corrige templates inconsistentes gerados pelo LLM.
  - Relata ganho de 69,5% no F1 médio de template accuracy sobre o estado da arte, em datasets de larga escala, e redução das consultas ao LLM em ordens de grandeza (resumo).
- Relevância para o Guardião (inferência):
  - O padrão é próximo do Guardião: um componente determinístico em volta do LLM, para consistência e custo. O runtime poderia deduplicar Recortes equivalentes e reaproveitar Relatos auditados.
  - A motivação, que é a inconsistência das respostas do LLM, justifica medir estabilidade: o mesmo Recorte com perturbações irrelevantes deve gerar o mesmo veredito.

### [A-12] Liu, Y.; Tao, S.; Meng, W.; Wang, J.; Ma, W.; Zhao, Y.; Chen, Y.; Yang, H.; Jiang, Y.; Chen, X. (2024). Interpretable Online Log Analysis Using Large Language Models with Prompt Strategies (LogPrompt). ICPC 2024.
- Link: https://arxiv.org/abs/2308.07610 · Status: peer-reviewed (aceito no ICPC 2024, segundo os comments do arXiv) · Verificado: sim
- Contribuição:
  - Relata que métodos existentes podem cair até 62,5% em logs não vistos de novos domínios. Estratégias de prompt (self-prompt, CoT, in-context) melhoram o LLM em até 380,7% sobre prompts simples. Sem treino in-domain, o método supera abordagens treinadas em milhares de logs em até 55,9%, em 9 datasets e 2 tarefas (resumo).
  - Na avaliação humana de interpretabilidade, seis praticantes com mais de 10 anos de experiência deram nota média 4,42/5 às explicações (resumo).
- Relevância para o Guardião (inferência):
  - O ganho de prompting é grande. Antes de atribuir ganhos ao LoRA, o Run 0 (Macro-F1 0,33) precisa de uma variante few-shot ou com prompt melhorado como baseline mais forte.
  - A explicação avaliada por nota humana é subjetiva. A Evidência literal checável é uma métrica mais auditável, e o contraste entre as duas é material para o artigo.

### [A-13] Guan, W.; Cao, J.; Qian, S.; Gao, J.; Ouyang, C. (2024). LogLLM: Log-based Anomaly Detection Using Large Language Models. arXiv.
- Link: https://arxiv.org/abs/2411.08561 · Status: preprint (sem journal-ref na página; última revisão listada em 2026) · Verificado: sim
- Contribuição:
  - Combina um encoder, que gera vetores semânticos por mensagem, e um decoder, que modela a sequência e emite a decisão. Usa um projetor aprendível, treino em três estágios e pré-processamento por regex no lugar de parser.
  - Relata melhoria média de 6,6% no F1 sobre a melhor abordagem existente em quatro datasets públicos (resumo; a página não nomeia os datasets).
- Relevância para o Guardião (inferência):
  - Representa a linha "LLM como classificador de sequência": decide, mas não normaliza nem explica. O Guardião se diferencia ao exigir saída generativa estruturada e verificável.
  - Se os quatro datasets forem os do Loghub, valem para ele as críticas de [A-5].

### [A-14] Ma, Z.; Yang, J.; Chen, T.-H. (2026). LLM4Log: A Systematic Review of Large Language Model-based Log Analysis. arXiv.
- Link: https://arxiv.org/abs/2604.16359 · Status: preprint · Verificado: sim
- Contribuição:
  - Revisão sistemática de 145 artigos, com coleta até novembro de 2025, sobre sete tarefas de log. Propõe uma taxonomia por tarefa e padrões de projeto: prompting/ICL, grounding por recuperação, fine-tuning, agentes com ferramentas e verificação.
  - Aponta como desafios a robustez a drift e a eventos de cauda longa com poucos rótulos, a fidelidade das saídas para operadores (alucinação), custo e latência, privacidade e a necessidade de comportamento verificável no deploy.
- Relevância para o Guardião (inferência):
  - "Verificação" como padrão de projeto e "comportamento verificável" como lacuna enquadram bem a checagem literal de IoC e Evidência e o runtime determinístico.
  - O foco é confiabilidade de software, não segurança, o que ajuda a delimitar a lacuna de SOC na seção de trabalhos relacionados.

---

## 3. LLMs para triagem de alertas e eventos de segurança e geração estruturada

### [A-15] Karlsen, E.; Luo, X.; Zincir-Heywood, N.; Heywood, M. (2023). Benchmarking Large Language Models for Log Analysis, Security, and Interpretation. arXiv.
- Link: https://arxiv.org/abs/2311.14519 · Status: preprint · Verificado: sim para o preprint. A versão no Journal of Network and Systems Management (2024, DOI 10.1007/s10922-024-09831-x) aparece só em resultados de busca, e a página da Springer exigiu login: NÃO VERIFICADO.
- Contribuição:
  - Fine-tuning de 60 modelos de cinco arquiteturas (BERT, RoBERTa, DistilRoBERTa, GPT-2, GPT-Neo) como classificadores de sequência, em seis datasets de logs de aplicações web e de sistema, com o pipeline LLM4Sec.
  - O melhor modelo (DistilRoBERTa) atinge F1 médio de 0,998 nos seis datasets (resumo). Os autores concluem que o fine-tuning é importante para a adaptação de domínio.
- Relevância para o Guardião (inferência):
  - Modelos pequenos ajustados chegam a números quase perfeitos em datasets públicos. À luz de [A-5] e [A-9], isso indica mais a facilidade do benchmark do que a capacidade do modelo. O projeto deve evitar comparar números absolutos entre datasets.
  - Um encoder pequeno como classificador puro é um baseline natural para o veredito.

### [A-16] Henshaw, C.; Karmakar, G. (2026). From Noise to Signal: Improving Security Log Anomaly Detection Using LLMs with Endpoint-Specific Logs. arXiv.
- Link: https://arxiv.org/abs/2608.19938 · Status: preprint (os comments dizem que ainda não foi submetido e que os autores planejam um periódico) · Verificado: sim
- Contribuição:
  - Classificação de autenticação anômala, incluindo casos limítrofes, por LLMs instruídos (Llama 3.1 8B Instruct, Qwen 2.5 7B Instruct, GPT-OSS 20B). Usa dados de testbed específicos do endpoint e compara com Wazuh e OpenSearch AD sob uma escala de severidade comum.
  - Llama 3.1 8B obteve 89,3% de acurácia, 91,8% de F1, 11,8% de FNR e detectou 80% dos casos limítrofes; o Wazuh ficou em 52,0% de acurácia. O Qwen teve 100% de validade de resposta estruturada e a menor latência, e o GPT-OSS foi forte quando produziu resposta válida (resumo). O resumo não relata FPR.
- Relevância para o Guardião (inferência):
  - Confirma que a validade da saída estruturada varia por modelo e precisa entrar nas métricas de triagem. O projeto já exige registrar como respostas inválidas entram nessas métricas.
  - A classe limítrofe é análoga a suspicious/expected_admin. Sem FPR, o estudo não responde ao critério central do projeto, e essa é uma lacuna a ocupar.

### [A-17] Zhao, G.; Zhang, Y.; Tian, C.; Xie, D.; Liu, H.; Wang, B. (2025). Information-Dense Reasoning for Efficient and Auditable Security Alert Triage. arXiv.
- Link: https://arxiv.org/abs/2512.08169 · Status: preprint · Verificado: sim
- Contribuição:
  - AIDR é um framework cloud-edge: um LLM na nuvem roteia alertas para especialistas on-premises treinados com LoRA, que emitem JSON pronto para SOAR.
  - Comprime o raciocínio em 3–5 bullets de alta informação, com 68% menos tokens e 40,6% menos latência que CoT, e relata acurácia maior. O resumo não dá números de acurácia, FPR, tamanho de modelo nem datasets.
- Relevância para o Guardião (inferência):
  - É o desenho mais próximo do projeto (LoRA, JSON para automação e auditabilidade). O Guardião pode se distinguir por métricas de grounding literal e por separar relato de ação, já que o AIDR produz saída para SOAR.
  - Sugere ablar rationale curto contra longo no contrato.

### [A-18] Tsegai, S. A.; Kantchelian, A.; Yao, D.; Gao, P. (2026). From Investigation Failures to Reliable SOC Agents: Understanding and Improving LLM-Based Alert Triage. arXiv.
- Link: https://arxiv.org/abs/2610.10608 · Status: preprint · Verificado: sim
- Contribuição:
  - ALERT-BENCH é um benchmark interativo que reexecuta telemetria corporativa num SIEM real, com 1.247 alertas de um cenário de ataque multi-etapa. Compara cinco estratégias de agente: tool use em passe único, recuperação iterativa, amostragem, auto-revisão e verificação explícita.
  - Todas as estratégias perderam pelo menos 40,4% dos alertas de ataque. Buscas vazias levaram ao descarte de alertas de ataque, e a auto-revisão no mesmo contexto teve correção líquida negativa. O AIDA, multi-agente com ledger append-only e juiz separado, atinge F1 0,958 contra 0,371–0,744 dos baselines, com FNR de 3,1% e 18,4% dos alertas escalados (resumo).
- Relevância para o Guardião (inferência):
  - O modo de falha "ausência de evidência, logo benigno" afeta o Recorte diretamente: se a projeção omitir contexto, o modelo pode concluir benign. É preciso testar os Recortes truncados (os ~10% que exigem `null`) e medir se o veredito é rebaixado por falta de dados.
  - O ledger append-only e o juiz separado ecoam o runtime auditável do Guardião. Os resultados vêm de um único cenário, então a generalização é limitada.

### [A-19] Tam, Z. R.; Wu, C.-K.; Tsai, Y.-L.; Lin, C.-Y.; Lee, H.-y.; Chen, Y.-N. (2024). Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models. EMNLP 2024 (Industry Track).
- Link: https://aclanthology.org/2024.emnlp-industry.91 (texto lido em https://arxiv.org/html/2408.02442v3) · Status: peer-reviewed (pp. 1218–1236, DOI 10.18653/v1/2024.emnlp-industry.91) · Verificado: sim
- Contribuição:
  - Compara decodificação restrita (JSON mode), instruções de formato (FRI) e NL-to-Format em vários modelos, entre eles LLaMA-3-8B-Instruct e Gemma-2-9B-Instruct. As restrições de formato degradam tarefas de raciocínio, mais quanto mais estritas.
  - Em classificação o efeito se inverte: o JSON mode foi competitivo e às vezes melhor (DDXPlus com Gemini 1.5 Flash: 41,6 em texto contra 60,3 em JSON, Tabela 10). No JSON mode, o GPT-3.5 pôs a chave da resposta antes da chave de raciocínio em 100% dos casos de Last Letter, respondendo sem raciocinar. Os erros de parsing não explicam a maior parte das diferenças.
- Relevância para o Guardião (inferência):
  - A ordem dos campos no alvo de treino importa. Se Evidência e rationale vierem antes do veredito no JSON, o veredito é condicionado à evidência gerada. Essa ordem é uma ablação barata.
  - JSON estrito tende a não custar acurácia no veredito (classificação), mas pode custar na rationale e na Hipótese de CWE (raciocínio). As métricas devem ser separadas por campo.

### [A-20] Landauer, M.; Skopik, F.; Wurzenberger, M.; Górski, F.; Krzysztoń, M. (2026). Just Testing, Move Along: Evasion of LLM-based System Log Interpretation by Prompt Injection. arXiv.
- Link: https://arxiv.org/abs/2607.24174 (texto lido em https://arxiv.org/html/2607.24174v1) · Status: preprint · Verificado: sim
- Contribuição:
  - Framework que gera injeções em logs de ataques reais (CAM-LDS e AIT-LDSv2, com 15 casos de ataque e 2 amostras benignas) em três etapas: geração genérica com enquadramento benigno, variação e otimização com contexto do ataque.
  - As injeções foram postas no User-Agent (web) e como parâmetro extra de linha de comando (audit) e fizeram traços maliciosos serem classificados como normais. Na etapa otimizada, o sucesso foi de 66,7% no GPT-5.2, 73,3% no Devstral-2 e 86,7% no Llama-3.3 e no Qwen. Todo caso teve ao menos uma combinação com pontuação máxima de "normal" (seção de resultados).
  - Quando o veredito muda, as explicações dos modelos costumam mencionar as notas injetadas, o que é um possível sinal de detecção, avaliado com um segundo LLM.
- Relevância para o Guardião (inferência):
  - Valida a suíte adversarial planejada. Sugere injetar em campos controláveis pelo atacante em cada modalidade (User-Agent e URI em apache/waf, CommandLine em sysmon, usuário em linux_auth) e medir veredito rebaixado, IoC omitido e Evidência que cita a injeção.
  - A checagem literal pode virar defesa: se o Relato usa como evidência de benignidade um trecho de texto livre controlado pelo atacante, o runtime marca para revisão. Os modelos testados são grandes e sem ajuste. Ainda não se sabe se LoRA num modelo pequeno aumenta ou reduz a suscetibilidade.

---

### Outras fontes abertas nesta sessão, fora das entradas
- LogAnomaly (Meng et al., IJCAI 2019, pp. 4739–4745): https://www.ijcai.org/proceedings/2019/658. Template2vec e detecção conjunta de anomalias sequenciais e quantitativas em HDFS e BGL. Peer-reviewed, verificado.
- LogBERT (Guo, Yuan, Wu, 2021): https://arxiv.org/abs/2103.04475. Preprint sem journal-ref. A versão IJCNN 2021 não foi verificada, porque a página do IEEE veio vazia.
- He et al., A Survey on Automated Log Analysis for Reliability Engineering: https://arxiv.org/abs/2009.07237. Os comments dizem "accepted by ACM Computing Survey". Volume e DOI não foram verificados.
- Chen et al., Experience Report: Deep Learning-based System Log Analysis for Anomaly Detection: https://arxiv.org/abs/2107.05908. Preprint com seis métodos, dois datasets e cerca de 16 milhões de mensagens.
- CORTEX (Wei et al., 2025): https://arxiv.org/abs/2510.00311. Preprint de triagem multi-agente que relata menos falsos positivos que baselines de agente único; a página não traz números.
- Poisoning the Watchtower (Pandey, Bhujang, 2026): https://arxiv.org/abs/2605.24421. Preprint discutido em Controvérsias.
- Habibzadeh et al., LLMs for SOCs: A Comprehensive Survey: https://arxiv.org/abs/2509.10858. O journal-ref indica J. Electrical and Computer Engineering 2026. A cobertura é superficial: não trata fine-tuning nem alucinação no resumo.
- Sementes não abertas nesta sessão (NÃO VERIFICADO): DivLog, RAGLog, LogGPT e Loghub-2.0 (este só por resultado de busca; ISSTA 2024, arXiv 2308.10828).

---

## Lacunas observadas

1. **Triagem de segurança multi-fonte rotulada por janela.** A literatura de anomalia em logs gira em torno de confiabilidade (HDFS, BGL, Thunderbird): [A-4] relata que a grande maioria das avaliações usa quatro datasets, e [A-5] mostra que eles são triviais. Não há benchmark público com Sysmon, auth, web, IDS e WAF, veredito em 4 classes que inclua `expected_admin`, e split por incidente. O protocolo e o esquema do projeto são uma contribuição possível, mesmo que os logs não possam ser publicados.
2. **Grounding literal como métrica.** Nenhuma entrada mede alucinação de IoC ou de evidência por busca literal no log de entrada. [A-14] aponta fidelidade e verificação como desafios abertos, e [A-12] avalia explicação por nota humana. Taxa de IoC alucinado e taxa de Evidência literal são métricas novas e auditáveis.
3. **FPR em benignos administrativos.** [A-16] não relata FPR no resumo, [A-18] foca FNR e [A-15] relata F1. Medir FPR em `benign`/`expected_admin`, convertido para alertas por dia sob uma prevalência declarada (armadilha P8 de [A-9]), quase não aparece.
4. **Quantização, alvos e rank do LoRA em tarefa de segurança.** Nenhuma entrada isola o efeito de QLoRA 4-bit contra LoRA BF16, de alvos atenção contra all-linear ou do rank sobre validade de JSON, alucinação de IoC e FPR. A matriz de ablação do projeto preenche isso.
5. **Injeção em modelos pequenos ajustados.** [A-20] e o Watchtower testam modelos grandes, por API ou zero-shot. Ainda não se sabe se o fine-tuning com JSON estrito e evidência literal torna um modelo de 3–4B mais ou menos robusto.
6. **Efeito de sintéticos separáveis.** [A-9] alerta para viés de dados sintéticos e de fontes combinadas, mas nenhuma entrada mede o efeito de misturar sintéticos separáveis por TF-IDF na triagem de logs. Ablações 0:1 contra 1:1, avaliadas só no teste real, seriam inéditas.
7. **Contaminação de pré-treino.** Não encontrei estudo que quantifique memorização de Loghub ou AIT-LDS por LLMs. Isso afeta baselines zero-shot com dados públicos.
8. **Separação entre relato e ação.** Os sistemas de SOC revisados agem ou alimentam SOAR ([A-17]), ou decidem e escalam via agentes ([A-18], CORTEX). Uma arquitetura em que o modelo só relata e um runtime determinístico propõe contenção com aprovação humana não aparece avaliada, nem em governança nem em auditabilidade.

## Controvérsias e resultados conflitantes

- **Deep learning contra métodos simples.** O resumo de [A-4] diz que DL tem mostrado desempenho melhor que ML convencional. [A-8] mostra KNN e SLFN superando DL em tempo e acurácia, e [A-5] mostra que detectores triviais chegam a F1 acima de 96% em HDFS e BGL. [A-3] explica parte do conflito: o ranking muda com o split (aleatório contra cronológico) e com a janela.
- **Números quase perfeitos contra quedas sob avaliação realista.** [A-15] relata F1 médio de 0,998, e vários modelos passam de 0,9 no HDFS ([A-3]). No BGL, porém, o split cronológico derruba o DeepLog de 0,927 para 0,426 ([A-3], Tabela 2). Números absolutos entre estudos não são comparáveis.
- **Prompting contra fine-tuning.** [A-12] relata que prompting sem treino in-domain supera métodos treinados em até 55,9%. [A-15] e [A-10] concluem que o fine-tuning é essencial e que modelos menores ajustados podem igualar maiores. As tarefas e bases diferem, e nenhuma compara as duas abordagens sob um mesmo split por incidente.
- **Formato estruturado: custo ou ganho.** [A-19] mostra que formatos estritos degradam raciocínio mas podem ajudar classificação. [A-16] mostra que a validade estrutural varia de 100% (Qwen) até respostas inválidas frequentes (GPT-OSS). O efeito depende do campo e do modelo.
- **Raciocínio adicional ajuda ou atrapalha.** [A-12] relata ganho com CoT. [A-17] afirma acurácia maior que CoT com raciocínio comprimido. [A-18] encontra correção líquida negativa na auto-revisão no mesmo contexto. Não há consenso sobre quanto raciocínio a triagem precisa.
- **Que injeção funciona.** O Watchtower (https://arxiv.org/abs/2605.24421, gpt-4o-mini) relata 0% de supressão por override direto na classificação, persona hijack como o ataque mais forte e sumarização como a tarefa mais vulnerável. Saída restrita reduziu a manipulação de contexto de 96% para 38%, e o sucesso médio caiu de 26,6% para 11,8% sob a defesa mais forte (resumo). [A-20] relata 53–87% de sucesso com enquadramentos benignos do tipo "apenas teste". Os resultados divergem em modelos, tarefas e métricas, então a suíte do projeto deve cobrir várias famílias de ataque.
- **"Não supervisionado".** [A-4] nota que muitos métodos ditos não supervisionados são semi-supervisionados, porque treinam só com dados normais. Isso confunde comparações de custo de rótulo.

## O que confirma ou desafia as decisões do projeto

**Confirma:**
- **Split por grupo de incidente ou cenário.** Apoiado pelo vazamento em split aleatório ([A-3]), pelo data snooping ([A-9], P3) e pela recomendação de publicar splits ([A-5]). Em AIT-LDS, o grupo deve ser a simulação ([A-6]).
- **JSON estrito validado, com inválidas contabilizadas.** A validade varia por modelo ([A-16]) e erros de parsing existem mesmo em modelos fortes ([A-19]).
- **Checagem literal de IoC e Evidência e runtime determinístico.** Alinha-se a verificação como padrão e lacuna ([A-14]), ao cache determinístico para consistência ([A-11]) e ao ledger auditável ([A-18]).
- **FPR em benign/expected_admin junto do Macro-F1.** [A-5] pede TNR/FPR, e [A-3] pede Specificity porque o F1 engana sob desbalanceamento.
- **Suíte adversarial em campos literais.** [A-20] e o Watchtower mostram que é um vetor real e que a mitigação é parcial.
- **Modelo pequeno com fine-tuning.** [A-10] (modelos menores ajustados são competitivos) e [A-15] (fine-tuning é essencial para adaptação de domínio) apoiam a meta.

**Desafia ou pede ajuste:**
- **Mistura sintética 1:1 separável por TF-IDF.** Cai em viés de amostragem e correlação espúria ([A-9], P1/P4). Sugestão: ablações 0:1 e 1:1, teste apenas com dados reais, e um classificador "fonte sintética ou real" como diagnóstico de vazamento de estilo.
- **Baselines fracos.** Um Run 0 zero-shot não basta. Faltam um baseline leve (TF-IDF ou regras, [A-8], [A-5]), um baseline few-shot ou com prompt melhorado ([A-12]) e um encoder pequeno classificador ([A-15]). Sem eles, ganhos do LoRA no veredito podem ser atalho.
- **Rótulo derivado do formato.** Se EventID, assinatura ou regra determinam o veredito, o modelo aprende o atalho ([A-5]). Convém medir o desempenho do baseline que só vê esses campos.
- **Desenho do Recorte como variável.** O agrupamento altera o F1 de forma drástica ([A-3]), e a ausência de evidência induz descarte de ataques ([A-18]). Tamanho e política da janela devem ser registrados, e os Recortes truncados avaliados à parte.
- **Variância e tamanho do teste.** [A-5] pede repetições e variância. Com 166 exemplos de teste e 4 classes, os intervalos de confiança do Macro-F1 e do FPR serão largos (inferência). Uma saída compatível com a seed 42 fixa é bootstrap no teste; seeds extras numa análise secundária são decisão do responsável pelo estudo.
- **Taxa-base.** A distribuição-alvo 45/45/10 não reflete a prevalência real de um SOC ([A-9], P8). O artigo deve projetar o FPR para volumes realistas.
- **Ordem dos campos no JSON.** Gerar o veredito antes da Evidência e da rationale pode reduzir o raciocínio condicionado ([A-19]). Vale testar o contrato v2 com a Evidência antes do veredito.
- **Contaminação e dados públicos.** Exemplos derivados de Loghub e AIT-LDS podem estar no pré-treino ([A-7], inferência). Convém reportar o Run 0 separadamente para fontes públicas e privadas.
