# Tema G — Medir carga cognitiva, supervisão humana, auditabilidade e governança local

> **Escopo.** Revisão focada em *como medir* as três contribuições do artigo do Guardião: menos carga na triagem do SOC, auditabilidade com supervisão humana e governança dos dados por processamento local.
> **Método.** Busca web e leitura das páginas primárias em 2026-11-25. "Verificado" significa que a URL indicada foi aberta nesta sessão e que o conteúdo resumido veio dela. Quando só os metadados abriram, a ficha diz isso. Números e venues não confirmados estão marcados como **NÃO VERIFICADO**.
> **Registro de execução.** Host: Claude Code (subagente), modelo Opus 5.5. Nenhum repositório foi alterado. Os PDFs foram lidos apenas como texto (pdftotext) na área temporária.
> **Convenção.** "Como usar no Guardião" é **inferência** desta revisão, não afirmação das fontes.

---

## 1. Carga cognitiva e carga de trabalho em SOC

### [G-1] Hart, S. G.; Staveland, L. E. (1988). Development of NASA-TLX (Task Load Index): Results of empirical and theoretical research. In: Hancock, P. A.; Meshkati, N. (eds.), *Human Mental Workload* (Advances in Psychology, v. 52), North-Holland, p. 139–183.
— https://bibbase.org/network/publication/hart-staveland-developmentofthenasatlxtaskloadindexresultsofempiricalandtheoreticalresearch-1988 · Capítulo de livro com editores (instrumento de referência) · **Verificado parcialmente:** registro bibliográfico e resumo abertos. O PDF da NASA (humansystems.arc.nasa.gov) recusou conexão. O PDF do NTRS é uma digitalização sem camada de texto.
- O programa de pesquisa coletou avaliações subjetivas de 10 fatores de carga em 16 experimentos. Os experimentos iam de tarefas cognitivas simples a simulação de aeronave.
- Os autores propõem uma escala multidimensional que combina **seis fatores** em uma estimativa de carga sensível e confiável. Os nomes das subescalas (demanda mental, física e temporal; desempenho; esforço; frustração) e a variante sem pesos, o *Raw TLX*, aparecem só em fontes secundárias desta sessão. Ainda falta conferir esses nomes no texto original.
- A carga varia com a dificuldade da tarefa, as fontes de carga e a forma como cada pessoa entende "carga". Por isso a comparação deve ser **intra-sujeito**.

**Como usar no Guardião (inferência)**
- Em um estudo com analistas, aplique o TLX (ou o RTLX) depois de cada bloco de triagem, nas condições "com Relato" e "sem Relato" (log bruto). Reporte a diferença pareada por participante, não médias absolutas.
- Não use o TLX como proxy computacional. Ele exige respondentes humanos.

### [G-2] Dykstra, J.; Paul, C. L. (2018). Cyber Operations Stress Survey (COSS): Studying fatigue, frustration, and cognitive workload in cybersecurity operations. 11th USENIX Workshop on Cyber Security Experimentation and Test (CSET '18).
— https://usenix.org/conference/cset18/presentation/dykstra · Peer-reviewed (workshop) · **Verificado** (página do artigo na USENIX)
- O COSS é um questionário de baixo custo para medir fadiga, frustração e carga cognitiva em operações cibernéticas em tempo real.
- Combina medidas pré e pós-operação com fatores validados do NASA-TLX e fatores de contexto.
- Os autores relatam desenvolvimento, validação e uso em quatro estudos na NSA. A página não detalha o método de validação.

**Como usar no Guardião (inferência)**
- Use o COSS como instrumento curto para um estudo de campo em turno real de SOC: aplique antes e depois do turno, com e sem Relatos do Guardião. É mais leve que o TLX ponderado.
- Métrica: variação (pós − pré) de fadiga, frustração e carga, comparada entre as condições.

### [G-3] Alahmadi, B. A.; Axon, L.; Martinovic, I. (2022). 99% False Positives: A Qualitative Study of SOC Analysts' Perspectives on Security Alarms. 31st USENIX Security Symposium, p. 2783–2800.
— https://usenix.org/conference/usenixsecurity22/presentation/alahmadi · Peer-reviewed · **Verificado**
- Combina um levantamento com 20 profissionais de SOC e um estudo qualitativo com 21. Os participantes confirmam altas taxas de falso positivo e a necessidade de validar alarmes manualmente.
- A maioria dos FPs vem de *gatilhos benignos*: alarmes tecnicamente corretos sobre comportamento legítimo do ambiente. Isso equivale aos vereditos `benign` e `expected_admin` do Guardião.
- Os autores propõem cinco propriedades para alarmes de qualidade: confiável, explicável, analítico, contextual e transferível. A validação manual leva a "alarm burnout and eventually desensitization".

**Como usar no Guardião (inferência)**
- Proxy de carga: conte os **FPs que chegam ao humano por 1.000 janelas**. São os alertas `malicious` ou `suspicious` em janelas rotuladas `benign` ou `expected_admin`. Compare com uma linha de base de regras (por exemplo, Sigma ou alerta nativo do Suricata).
- Use as cinco propriedades como rubrica de avaliação do Relato, pontuada por especialistas ou por checagem automática dos campos.

### [G-4] Oesch, S.; Bridges, R.; Smith, J.; Beaver, J.; Goodall, J.; Huffer, K.; Miles, C.; Scofield, D. (2020). An Assessment of the Usability of Machine Learning Based Tools for the Security Operations Center. IEEE CPSCom 2020 (Rhodes, Grécia).
— https://arxiv.org/abs/2012.09013 (preprint) · venue confirmado em https://www.osti.gov/biblio/1766395 · Peer-reviewed (anais IEEE) · **Verificado**
- Primeira avaliação *in situ* de usabilidade de ferramentas de ML para SOC: seis analistas de SOC da Marinha dos EUA usaram duas ferramentas no *national cyber range*.
- Os autores encontraram violações de heurísticas de usabilidade. Os analistas não tinham um modelo mental de como as pontuações eram geradas, o que levou a "mistrust and/or misuse of the tools themselves".
- Escolaridade e anos de experiência não se correlacionaram com o desempenho nas ferramentas.

**Como usar no Guardião (inferência)**
- Meça se o analista consegue explicar por que o Relato concluiu X. Métrica: **taxa de reconstrução correta do raciocínio**, ou seja, a proporção de analistas que apontam a Evidência decisiva.
- Com N pequeno (6 a 12 analistas, como em Oesch), apresente os resultados como evidência de usabilidade, não como estimativa de efeito.

### [G-5] Banstola, K.; Al Faisal, F.; Ou, X. (2026). Experiences of Using Agentic AI to Fill Tooling Gaps in a Security Operations Center. Workshop on SOC Operations and Construction (WOSOC 2026, NDSS), DOI 10.14722/wosoc.2026.23016.
— https://www.ndss-symposium.org/wp-content/uploads/wosoc26-02.pdf · Peer-reviewed (workshop) · **Verificado** (texto do PDF)
- Os pesquisadores trabalharam como analistas de nível de entrada em um SOC universitário. Construíram um agente ReAct que integra SIEM, OSINT e ferramentas internas. O agente roda **on-premises** (gpt-oss) porque os dados não podem sair da rede da organização.
- Em 8 tickets reais, cada um triado com e sem o agente em ordem alternada, a triagem assistida levou cerca de 40% menos tempo em média. Em um ticket ela foi mais lenta.
- Os próprios autores avisam que os construtores do sistema fizeram a avaliação. Eles tratam os números como evidência qualitativa de viabilidade. O artigo também relata um caso em que o agente se apoiou demais em reputação de IP, e o analista corrigiu.

**Como usar no Guardião (inferência)**
- É o precedente mais próximo da arquitetura local, e também mostra o desenho a evitar: os autores avaliaram o próprio sistema. Métrica: **tempo por alerta pareado** (com e sem Relato), em ordem contrabalançada e com avaliadores que não construíram o Guardião.
- Reporte separadamente os tickets em que o Relato *aumentou* o tempo.

### [G-6] Bono, J. (2025). Randomized Controlled Trials for Phishing Triage Agent. arXiv:2511.13860 (Microsoft Corporation).
— https://arxiv.org/html/2511.13860v1 · Preprint (do fornecedor) · **Verificado**
- ECR com 167 analistas externos, em três braços: Controle (52), *Aware*, que vê veredito, justificativa e calibração do agente (56), e *Blind*, que recebe só a fila ordenada (59). Cada fila tinha 25 e-mails, incluindo **um falso negativo e um falso positivo sintéticos plantados**.
- No *ground truth* do corpus, o grupo *Aware* teve até 6,5 vezes mais verdadeiros positivos por minuto de analista, e o F1 passou de 0,53 para 0,93. O ganho diminui em cenários contrafactuais, com acurácia do agente de 80% ou taxa de maliciosos de 20% a 30%. A maior parte do ganho veio do protocolo de "resolver benignos", não das explicações.
- **Viés de automação na direção benigna:** 46% do grupo *Aware* não detectou o falso negativo plantado, contra 17% do Controle (p = 0,001). Para o falso positivo plantado não houve diferença significativa (54% contra 48%). Um ECR anterior do mesmo grupo, com administradores de TI, relata acurácia 34,53% maior e tempo 29,79% menor (Bono & Xu, https://arxiv.org/abs/2411.01067, preprint).

**Como usar no Guardião (inferência)**
- Este é o desenho a replicar: **erros plantados nos dois sentidos**. Métricas: taxa de detecção de FN plantado (Relato `benign` em janela maliciosa) e de FP plantado, em cada condição.
- Para carga, use **verdadeiros positivos por analista-minuto** e reporte sensibilidade à taxa-base e à acurácia do modelo. Atenção: o risco maior para o Guardião é o veredito `benign` errado, não o alarme falso.

### [G-7] Rastogi, N.; Pant, S.; Dhanuka, D.; Saxena, A.; Mairal, P. (2025). Too Much to Trust? Measuring the Security and Cognitive Impacts of Explainability in AI-Driven SOCs. ACM CCS 2025 (segundo a página do arXiv).
— https://arxiv.org/abs/2503.02065 · Peer-reviewed segundo o arXiv (registro nos anais **NÃO VERIFICADO**) · **Verificado** (resumo no arXiv)
- Estudo de métodos mistos durante três meses: levantamento com 248 profissionais de SOC e 24 entrevistas.
- Os analistas aceitaram saídas de XAI *mesmo com acurácia preditiva menor* quando as explicações pareciam relevantes e apoiadas em evidência.
- Os analistas preferem explicações contextuais e adequadas ao papel em vez de painéis de resultado.

**Como usar no Guardião (inferência)**
- A "Evidência literal" pode *aumentar* a confiança indevida. Meça a **confiança condicionada ao acerto**: a confiança declarada pelo analista quando o Relato está certo e quando está errado. A diferença entre os dois casos é a métrica de calibração da confiança.
- No piloto, combine com G-6: Relatos errados *com* Evidência plausível são o teste mais duro.

## 2. Supervisão humana e viés de automação

### [G-8] Parasuraman, R.; Manzey, D. H. (2010). Complacency and Bias in Human Use of Automation: An Attentional Integration. *Human Factors*, 52(3), 381–410. DOI 10.1177/0018720810376055.
— https://api.semanticscholar.org/graph/v1/paper/DOI:10.1177/0018720810376055?fields=title,venue,year,authors,abstract,journal,externalIds · Peer-reviewed (periódico) · **Verificado parcialmente:** metadados abertos. PubMed, SAGE e dblp bloquearam o acesso automatizado. O resumo abaixo vem de trechos do PubMed exibidos pela busca e está **NÃO VERIFICADO na página**.
- É uma revisão integradora: complacência e viés de automação seriam manifestações sobrepostas de um fenômeno atencional.
- O viés de automação produz **erros de omissão** (não agir sem o alerta do sistema) e **erros de comissão** (seguir uma recomendação errada). Esses erros ocorrem em novatos e especialistas e persistem apesar de treino ou instruções.

**Como usar no Guardião (inferência)**
- Separe as métricas por tipo de erro. **Comissão**: o analista aceita um Relato `malicious` errado. **Omissão**: o analista não investiga uma janela que o Guardião classificou como `benign` e que era maliciosa.
- Avalie esses erros *sob carga*, com filas maiores, porque a teoria prevê mais complacência quando a atenção está dividida.

### [G-9] Goddard, K.; Roudsari, A.; Wyatt, J. C. (2012). Automation bias: a systematic review of frequency, effect mediators, and mitigators. *JAMIA*, 19(1), 121–127. DOI 10.1136/amiajnl-2011-000089.
— https://pmc.ncbi.nlm.nih.gov/articles/PMC3240751 · Peer-reviewed (revisão sistemática) · **Verificado**
- Revisão de 74 estudos (de 13.821 recuperados). A medida mais clara de viés é a **consulta negativa**: o usuário tinha uma decisão correta antes do conselho e a troca por uma incorreta depois. Em estudos de saúde, a frequência varia de cerca de 6% a 11%.
- Na metanálise, quando o conselho do sistema estava errado, os usuários tiveram 26% mais chance de decidir errado que os controles (RR 1,26; IC95% 1,11–1,44).
- Mediadores: confiança, experiência, carga de trabalho, complexidade e pressão de tempo. Mitigadores: responsabilização, confiança atualizada caso a caso, menor destaque visual do conselho e informação em vez de ordem.

**Como usar no Guardião (inferência)**
- Use um protocolo em duas etapas: o analista decide com o log, depois vê o Relato e pode revisar. Métricas: **taxa de consultas negativas** e **taxa de consultas positivas** (decisão errada corrigida).
- O campo "risco de falso positivo" corresponde ao mitigador "confiança caso a caso". Meça a **calibração** desse campo com Brier ou ECE contra o rótulo, sem humanos.

### [G-10] Buçinca, Z.; Malaya, M. B.; Gajos, K. Z. (2021). To Trust or to Think: Cognitive Forcing Functions Can Reduce Overreliance on AI in AI-assisted Decision-making. *Proc. ACM Hum.-Comput. Interact.* (CSCW1), DOI 10.1145/3449287.
— https://arxiv.org/abs/2102.09692 · Peer-reviewed (DOI ACM informado na página do arXiv. O número do artigo, 188, só apareceu na busca: **NÃO VERIFICADO**) · **Verificado** (resumo no arXiv)
- Experimento com 199 participantes. Três intervenções de "forçamento cognitivo" foram comparadas com duas abordagens simples de XAI e com uma linha de base sem IA.
- O forçamento cognitivo reduziu a dependência excessiva em relação à XAI simples, mas não a eliminou. Os participantes deram as piores notas subjetivas aos desenhos que mais reduziram a dependência.
- Quem tem alta "necessidade de cognição" se beneficiou mais.

**Como usar no Guardião (inferência)**
- Teste uma variante da interface do SOC que exige a decisão do analista *antes* de mostrar o veredito do Guardião. Métrica: **concordância com o Relato quando o Relato está errado**, comparada entre as variantes.
- Reporte também a preferência subjetiva, porque os resultados podem divergir.

### [G-11] Vasconcelos, H.; Jörke, M.; Grunde-McLaughlin, M.; Gerstenberg, T.; Bernstein, M.; Krishna, R. (2023). Explanations Can Reduce Overreliance on AI Systems During Decision-Making. CSCW 2023.
— https://arxiv.org/abs/2212.06823 · Peer-reviewed (CSCW, segundo o arXiv) · **Verificado**
- Define dependência excessiva como concordar com a IA quando ela erra. Propõe um modelo de **custo e benefício**: as pessoas decidem estrategicamente se vão verificar a explicação.
- Cinco estudos com 731 participantes. A dificuldade da tarefa, a dificuldade da explicação e a recompensa alteraram a dependência excessiva.
- Os resultados nulos de explicações em trabalhos anteriores podem vir de explicações que não *barateiam a verificação*.

**Como usar no Guardião (inferência)**
- Esta fonte fundamenta a **verificabilidade** como proxy computacional: Evidência literal checável contra o log diminui o custo de verificar. Métricas sem humanos: **% de itens de Evidência com casamento literal** e **nº de itens a conferir por Relato**.
- Com humanos, meça o **tempo para verificar** um Relato, ou seja, o tempo até o analista confirmar ou refutar a Evidência.

### [G-12] União Europeia (2024). Regulamento (UE) 2024/1689 (AI Act), arts. 12, 14, 19 e 26.
— https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng · Norma (citada só como referência, sem análise de aplicabilidade) · **Verificado** (texto no EUR-Lex)
- **Art. 14(4):** quem supervisiona deve poder entender capacidades e limites, detectar anomalias, interpretar a saída, decidir não usar ou reverter, e interromper o sistema. A alínea (b) pede consciência do viés de automação, a "possible tendency of automatically relying or over-relying on the output".
- **Art. 12:** sistemas de alto risco devem permitir registro automático de eventos durante todo o ciclo de vida, com rastreabilidade adequada à finalidade.
- **Arts. 19(1) e 26(6):** os logs devem ser guardados por pelo menos seis meses, salvo outra lei, especialmente a de proteção de dados.

**Como usar no Guardião (inferência)**
- Transforme cada alínea do art. 14(4) em um item verificável. Exemplos: (d) **% de Relatos que o analista consegue rejeitar ou reverter na interface**; (e) o Guardião nunca age. Este último é verificável por inspeção do código e pela ausência de ferramentas de escrita.
- Use o art. 12 como lista mínima de campos do Diário. Não afirme que o Guardião é "conforme" ao AI Act. A classificação de risco não foi analisada aqui.

## 3. Auditabilidade mensurável

### [G-13] Raji, I. D.; Smart, A.; White, R. N.; Mitchell, M.; Gebru, T.; Hutchinson, B.; Smith-Loud, J.; Theron, D.; Barnes, P. (2020). Closing the AI Accountability Gap: Defining an End-to-End Framework for Internal Algorithmic Auditing. ACM FAT* 2020. DOI 10.1145/3351095.3372873.
— https://arxiv.org/abs/2001.00973 · Peer-reviewed · **Verificado** (resumo no arXiv)
- Propõe o SMACTR, um arcabouço de auditoria interna que acompanha todo o ciclo de desenvolvimento.
- Cada etapa produz documentos que juntos formam o relatório de auditoria. Os modelos de documento são públicos.
- A auditoria compara as decisões de desenvolvimento com os princípios declarados da organização. Os nomes das etapas não foram conferidos na página aberta.

**Como usar no Guardião (inferência)**
- Use como âncora conceitual: auditabilidade é a **existência e completude de artefatos por etapa**, como dados, adaptador assinado, avaliação e Diário. Métrica: checklist de artefatos presentes e versionados por release do adaptador (% completo).

### [G-14] Atıl, B.; Aykent, S.; Chittams, A.; et al. (2025). Non-Determinism of "Deterministic" LLM System Settings in Hosted Environments. Eval4NLP 2025 (ACL), p. 135–148.
— https://aclanthology.org/2025.eval4nlp-1.12 · Peer-reviewed (workshop) · **Verificado**
- Cinco LLMs hospedados, configurados para serem determinísticos, rodaram 10 vezes em 8 tarefas. A acurácia variou até 15% entre execuções, e nenhum modelo foi consistentemente idêntico.
- O artigo propõe as métricas **TARr@N** (concordância total da saída bruta em N execuções) e **TARa@N** (concordância da resposta extraída).
- Fontes complementares, também abertas. Yuan et al. (2025), https://arxiv.org/abs/2506.09501 (preprint): sob decodificação gulosa em bf16, o tamanho do lote, o número e o tipo de GPU mudam as respostas, com até 9% de variação de acurácia. A correção proposta é computar em FP32. He (2025), https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/ (blog, sem revisão por pares): atribui o não determinismo à falta de *batch invariance*. Com kernels invariantes ao lote, 1.000 amostras a T=0 ficaram idênticas.

**Como usar no Guardião (inferência)**
- **Reprodutibilidade de decisão a partir do Diário**: re-execute cada linha (entrada, adaptador e respostas de ferramentas pelos hashes) N vezes e reporte TARr@N do Relato inteiro e TARa@N do veredito e da severidade.
- Repita a medição trocando threads, build do llama.cpp e CPU. Nenhuma fonte desta sessão mede determinismo em llama.cpp na CPU, então o artigo precisa medir isso, não presumir.

### [G-15] Crosby, S. A.; Wallach, D. S. (2009). Efficient Data Structures for Tamper-Evident Logging. 18th USENIX Security Symposium.
— https://www.usenix.org/conference/usenixsecurity09/technical-sessions/presentation/efficient-data-structures-tamper-evident (página) e https://www.usenix.org/legacy/event/sec09/tech/full_papers/crosby.pdf (texto) · Peer-reviewed · **Verificado**
- Modelo de *logger* não confiável, mantido honesto por auditores que exigem provas de que eventos continuam presentes e de que a visão atual é consistente com a passada.
- A *history tree* gera essas provas com tamanho logarítmico. Em um log de 80 milhões de eventos, uma cadeia de hash exigiria cerca de 800 MB para provar a presença de um evento, contra uma prova de cerca de 3 KB.
- O protótipo processa 1.750 eventos/s em um núcleo, e 10.500 eventos/s com as assinaturas delegadas. O esquema também permite apagar eventos antigos de forma acordada e provável.

**Como usar no Guardião (inferência)**
- Métrica de integridade: **taxa de detecção de adulteração**. Injete alterações, remoções e reordenações em cópias do Diário; o verificador deve detectar 100%. Reporte também o **custo por linha** (µs, bytes) e o **tamanho da prova** de inclusão.
- Se o Diário for uma cadeia de hash linear, declare a limitação da auditoria em tempo linear. Uma árvore de Merkle é a alternativa mensurável.

### [G-16] Chan, A.; Ezell, C.; Kaufmann, M.; et al. (2024). Visibility into AI Agents. ACM FAccT 2024.
— https://arxiv.org/abs/2401.13138 · Peer-reviewed (FAccT, segundo o arXiv. As páginas 958–973 vieram só da busca: **NÃO VERIFICADO**) · **Verificado** (resumo)
- Avalia três medidas de visibilidade para agentes de IA: identificadores de agente, monitoramento em tempo real e **registro de atividades**.
- Para cada medida, discute implementações que vão de menos a mais intrusivas e informativas, e as implicações para privacidade e concentração de poder.

**Como usar no Guardião (inferência)**
- Use como justificativa para registrar **cada chamada de Ferramenta** (nome, argumentos e hash da resposta). Métrica: **cobertura da trilha** = chamadas de ferramenta registradas ÷ chamadas executadas, medida por instrumentação independente (por exemplo, strace ou contador no runtime).
- O tensionamento com privacidade apontado pelos autores vale para o próprio Diário, que contém trechos de log. A governança do Diário entra na dimensão 4.

## 4. Governança de dados em arquitetura local

### [G-17] Menges, F.; Latzo, T.; Vielberth, M.; et al. (2021). Towards GDPR-compliant data processing in modern SIEM systems. *Computers & Security*, 103, 102165. DOI 10.1016/j.cose.2020.102165.
— https://cris.fau.de/publications/249330950 · Peer-reviewed · **Verificado** (resumo no repositório institucional)
- Afirma que SIEMs existentes frequentemente processam dados pessoais sem aplicar princípios de proteção de dados.
- Deriva requisitos do GDPR para SIEM e propõe uma arquitetura conforme.
- Examina o efeito da **pseudonimização sobre a detectabilidade** de incidentes. Os números não estão no resumo e não foram conferidos.

**Como usar no Guardião (inferência)**
- Use o mesmo par de métricas: **exposição** (dados pessoais que saem da origem) contra **detectabilidade** (Macro-F1 e recall do Guardião local, comparados com um classificador central que vê o log bruto).
- Métrica de exposição: **identificadores pessoais por Relato enviado** (IPs, usuários, hostnames, e-mails, por regex ou NER) contra identificadores na janela bruta. Isso também mede quanto a "Evidência literal" vaza.

### [G-18] Agrawal, S.; Sarkar, S.; Aouedi, O.; et al. (2021). Federated Learning for Intrusion Detection System: Concepts, Challenges and Future Directions. arXiv:2106.09527.
— https://arxiv.org/abs/2106.09527 · Preprint (a página diz "Submitted to JNCA". A versão publicada não foi conferida: **NÃO VERIFICADO**) · **Verificado** (resumo)
- IDS de ML e DL centralizados exigem guardar e transmitir dados a um servidor central, o que compromete a privacidade.
- O aprendizado federado treina localmente e envia só parâmetros, então os dados brutos ficam no dispositivo.
- O artigo revisa tipos de IDS, abordagens de ML e aplicações de FL em detecção de anomalias.

**Como usar no Guardião (inferência)**
- Posicione o Guardião como **inferência na borda** sem treino federado: os dados brutos ficam, só o Relato sai. Métrica: **fator de redução de egress** = bytes da janela bruta ÷ bytes do Relato, por fonte de log.
- Se houver treino contínuo, o FL é a comparação natural. Fora isso, não afirme proteção equivalente sem medir.

### [G-19] Brasil (2018). Lei nº 13.709/2018 (LGPD), art. 6º, III e X; art. 7º, IX; art. 46 — e União Europeia (2016). Regulamento (UE) 2016/679 (GDPR), art. 5(1)(c) e 5(2); considerando 49.
— https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm e https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng · Norma · **Verificado**
- **LGPD art. 6º, III (necessidade):** "limitação do tratamento ao mínimo necessário para a realização de suas finalidades", com dados pertinentes, proporcionais e não excessivos. O inciso X exige demonstrar medidas eficazes. O art. 46 exige medidas de segurança desde a concepção.
- **GDPR art. 5(1)(c):** dados adequados, pertinentes e limitados ao necessário. O art. 5(2) pede que o controlador *demonstre* conformidade.
- **GDPR considerando 49:** tratar dados pessoais na medida estritamente necessária e proporcional à segurança de redes e informação é interesse legítimo. O art. 7º, IX da LGPD prevê o legítimo interesse como base legal.

**Como usar no Guardião (inferência)**
- Transforme a "necessidade" em uma **matriz campo × finalidade**: cada campo do Relato que sai da máquina precisa de uma finalidade de triagem declarada. Métrica: % de campos enviados com finalidade documentada, mais a contagem de campos sem justificativa.
- Como evidência de "demonstrar" (LGPD art. 6º, X; GDPR art. 5(2)), o Diário com hashes serve, mas ele também guarda dados. Declare a retenção e quem acessa. Isto não é aconselhamento jurídico.

## 5. Estudos com participantes humanos no Brasil

### [G-20] Conselho Nacional de Saúde: Resolução CNS nº 466/2012, Resolução CNS nº 510/2016 e Ofício Circular nº 17/2022/CONEP/SECNS/MS.
— 466/2012: https://bvsms.saude.gov.br/bvs/saudelegis/cns/2013/res0466_12_12_2012.html · 510/2016: https://bvsms.saude.gov.br/bvs/saudelegis/cns/2016/res0510_07_04_2016.html · Ofício 17/2022: cópia assinada no SEI hospedada em https://www.gov.br/hubrasil/pt-br/hospitais-universitarios/regiao-nordeste/hulw-ufpb/ensino-e-pesquisa/residencias/oficiocircular17_2022.pdf (código verificador SEI 0027884544) · Norma · **Verificado**. Os links antigos de conselho.saude.gov.br redirecionam para a página inicial do CNS, então foram usadas a BVS-MS e a cópia em gov.br.
- **Res. 466/2012:** o item II.14 define pesquisa com seres humanos como aquela em que o ser humano participa direta ou indiretamente, *incluindo o uso de seus dados*. O item VII.1 diz que "Pesquisas envolvendo seres humanos devem ser submetidas à apreciação do Sistema CEP/CONEP". O item XIII.3 remete as Ciências Humanas e Sociais, *e outras pesquisas que usam metodologias dessas áreas*, a uma resolução complementar.
- **Res. 510/2016:** o art. 1º cobre pesquisas com dados obtidos diretamente dos participantes ou com informações identificáveis. O parágrafo único lista o que **não** é registrado nem avaliado pelo sistema CEP/CONEP: (I) pesquisa de opinião pública com participantes não identificados; (II) informações de acesso público; (III) domínio público; (IV) censitária; (V) bancos de dados agregados sem identificação individual; (VI) revisão de literatura; (VII) aprofundamento teórico de situações que surgem espontaneamente na prática profissional, sem identificar o sujeito; (VIII) atividade só de ensino. O art. 2º, XIV define a pesquisa de opinião pública como consulta pontual sem possibilidade de identificar o participante. O registro do consentimento pode ser não escrito, mas a dispensa desse registro precisa ser aprovada pelo sistema (art. 16).
- **Ofício 17/2022:** a dispensa vale *só* para protocolos cujos procedimentos se enquadram **na totalidade** nos incisos. A pesquisa de opinião deve ter como único propósito descrever a valoração que o participante dá ao objeto, sem identificação desde a coleta. O inciso VII não pode criar nenhuma ação diferente da prática cotidiana. A instituição pode exigir análise ética mesmo quando o protocolo está dispensado.

**Como usar no Guardião (descrição do texto, não aconselhamento jurídico)**
- Um experimento com analistas que fazem triagem, respondem ao NASA-TLX, têm tempo medido e recebem erros plantados envolve dados obtidos diretamente dos participantes. Pelo texto, isso não se reduz a uma "pesquisa de opinião" nem a uma situação espontânea da prática, então se enquadra no caso geral do item VII.1 da 466. Um questionário anônimo e pontual de opinião com profissionais pode se encaixar no inciso I, mas só se *todo* o protocolo couber nele. Quem decide o enquadramento na prática é o CEP da instituição.
- A Res. CNS 674/2022 (art. 26) e o Ofício Circular 12/2023, que retomam essas dispensas, foram citados por fontes secundárias e estão **NÃO VERIFICADOS** aqui.

---

## Métricas propostas

| Dimensão | Métrica | Como calcular no Guardião | Precisa de humanos? | Fonte |
| --- | --- | --- | --- | --- |
| Carga (proxy) | FPs que chegam ao SOC por 1.000 janelas | Relatos `malicious`/`suspicious` em janelas rotuladas `benign`/`expected_admin`, comparados com uma linha de base de regras sem Guardião | Não | G-3, G-6 |
| Carga (proxy) | Taxa de escalonamento | Janelas que geram Relato enviado ÷ janelas processadas, por fonte (sysmon, auth, apache, suricata, WAF) | Não | G-3 |
| Carga (proxy) | Material a ler | Tokens ou bytes do Relato ÷ tokens ou bytes da janela bruta. Reporte também as linhas de Evidência por Relato | Não | G-5, G-11 |
| Carga (proxy) | Verificabilidade | % de itens de Evidência com casamento literal (sem distinção de maiúsculas) no log hasheado. Reporte também os itens a conferir por Relato | Não | G-11, G-3 |
| Carga (humana) | NASA-TLX/RTLX ou COSS | Bloco com Relato contra bloco com log bruto, intra-sujeito e contrabalançado. Reporte a diferença pareada | Sim | G-1, G-2 |
| Carga (humana) | Tempo por alerta e TP por analista-minuto | Cronometragem por ticket nas duas condições, com sensibilidade à taxa-base | Sim | G-5, G-6 |
| Supervisão | Detecção de erros plantados | % de FN plantados (Relato `benign` em ataque) e de FP plantados que o analista corrige, separados por direção | Sim | G-6, G-8 |
| Supervisão | Consultas negativas e positivas | Decisão antes do Relato, depois decisão revista. Conte trocas de certo para errado e de errado para certo | Sim | G-9 |
| Supervisão | Dependência excessiva | P(concorda \| Relato errado) contra P(concorda \| Relato certo), por variante de interface | Sim | G-10, G-11 |
| Supervisão (proxy) | Calibração do "risco de FP" | Brier ou ECE do campo de risco contra o rótulo, no conjunto de teste | Não | G-9 |
| Supervisão (proxy) | Itens do art. 14(4) atendidos | Checklist: rejeitar ou reverter na interface, sem ação autônoma, apenas ferramentas de leitura | Não (inspeção) | G-12 |
| Auditabilidade | Reprodutibilidade a partir do Diário | Re-executar N vezes cada linha do Diário (hashes de entrada, adaptador e ferramentas) e reportar TARr@N e TARa@N. Repetir com outros threads, build e CPU | Não | G-14 |
| Auditabilidade | Completude da trilha | % de linhas com todos os campos obrigatórios. Reporte também chamadas de ferramenta registradas ÷ executadas, por instrumentação independente | Não | G-12, G-16 |
| Auditabilidade | Integridade do Diário | Taxa de detecção de adulterações injetadas (meta: 100%), custo por linha e tamanho da prova | Não | G-15 |
| Auditabilidade | Artefatos por release | % do checklist de artefatos presentes e assinados (dados, adaptador, avaliação, Diário) | Não | G-13 |
| Governança | Redução de egress | Bytes ou eventos da janela bruta ÷ bytes ou eventos do Relato enviado, por fonte | Não | G-18, G-19 |
| Governança | Exposição de dados pessoais | Identificadores pessoais por Relato enviado contra identificadores na janela bruta (regex ou NER) | Não | G-17, G-19 |
| Governança | Custo em detecção | Δ Macro-F1, recall e FPR entre o Guardião local e um classificador central com log bruto | Não | G-17 |
| Governança | Necessidade por campo | % de campos enviados com finalidade documentada (matriz campo × finalidade) | Não (revisão documental) | G-19 |

## Lacunas observadas

- Não foi encontrado nesta sessão nenhum estudo revisado por pares que aplique o **NASA-TLX à triagem de SOC assistida por LLM com profissionais**. Os estudos com LLM em SOC medem tempo e acurácia (G-5, G-6) ou uso (Singh et al., 2025, https://arxiv.org/abs/2508.18947, preprint: 3.090 consultas de 45 analistas em 10 meses, sem métricas de carga).
- Os ECRs com maior N (G-6 e Bono & Xu) são do próprio fornecedor e não revisados por pares. O estudo local (G-5) foi avaliado pelos construtores. Falta uma replicação independente.
- O **viés de automação com erros plantados** em analistas profissionais aparece em um único estudo (G-6). A base teórica e quantitativa vem da saúde e da aviação (G-8, G-9).
- **Determinismo em llama.cpp na CPU** não tem medição publicada entre as fontes abertas. As evidências cobrem GPU e serviços hospedados (G-14).
- Não foi encontrado um **estudo acadêmico que compare** o envio de log bruto a um SIEM central com o processamento na borda, medindo volume e exposição de dados pessoais. Só apareceram documentos de fornecedores (Splunk, Google SecOps), não incluídos como fichas.
- Fichas com conteúdo parcialmente verificado: G-1 (texto integral não aberto) e G-8 (resumo não aberto). Res. CNS 674/2022 está **NÃO VERIFICADA**.
- O wiki do projeto (mathai-wiki) não foi consultado nesta tarefa. Decisões anteriores sobre métricas podem existir lá.

## Riscos de validade

- **Validade de construto:** os proxies computacionais (FPs encaminhados, tamanho do material, verificabilidade) medem *carga de trabalho* e *volume*, não *carga cognitiva*. Afirmar "redução de carga cognitiva" exige medida humana (TLX, COSS ou equivalente). Sem ela, a afirmação defensável é "redução da carga de triagem encaminhada ao SOC".
- **Lei de Goodhart:** um Relato menor reduz o "material a ler", mas pode omitir contexto e *aumentar* o custo de verificação (G-11). Reporte tamanho e verificabilidade juntos.
- **Dependência da taxa-base:** os ganhos variam com a taxa de maliciosos e com a acurácia do modelo (G-6). O dataset curado (cerca de 45% maliciosos) não reflete a taxa operacional de um SOC.
- **Direção do erro:** o viés de automação foi maior para vereditos *benignos* errados (G-6). Uma FPR baixa pode esconder omissões perigosas. Reporte os FN aceitos pelo humano.
- **Avaliador construtor e amostra:** o efeito é inflado quando quem construiu o sistema avalia (G-5) ou quando os participantes são estudantes. Amostras pequenas de SOC brasileiros limitam a generalização.
- **Reprodutibilidade local:** igualdade bit a bit em uma máquina não garante igualdade em outra CPU, build ou número de threads (G-14). Declare a configuração.
- **Integridade não é veracidade:** um Diário à prova de adulteração prova *o que foi registrado*, não que as respostas das Ferramentas eram verdadeiras. Se o host monitorado estiver comprometido, as entradas podem estar forjadas na origem (inferência).
- **Evidência literal e minimização:** citar trechos do log no Relato aumenta a verificabilidade, mas exporta dados pessoais. O ganho de governança precisa ser medido (G-17), não presumido.
- **Ética e consentimento:** um estudo com analistas reais em turno tem riscos de identificação e de avaliação de desempenho profissional, e passa pelo CEP (G-20).
