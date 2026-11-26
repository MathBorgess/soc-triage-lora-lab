# Tema C — Integração em operações de SOC, drift e injeção de prompt

Revisão feita em 2026-11-25. Fiz buscas na web nos modos standard e extended e abri cada URL citada nesta sessão. Venue e ano vêm da página aberta. Onde ACM DL (HTTP 403), IEEE Xplore (página vazia) ou atlas.mitre.org (sem conteúdo renderizado) não abriram, a entrada indica a fonte primária alternativa usada: cópia do autor, repositório institucional, campo *comments* do arXiv ou espelho MITRE.

Convenções:
- **Status** indica se o trabalho é peer-reviewed, preprint ou documento de organização.
- Os números vêm da página aberta e cada entrada diz onde eles aparecem.
- A seção "Relevância para o Guardião" traz **inferências** minhas e não afirmações das fontes.
- "Ver também" lista trabalhos relacionados agrupados na mesma entrada. Cada um tem link próprio aberto nesta sessão.

---

## 1. Operação de SOC e fadiga de alertas

### [C-1] Alahmadi, Axon & Martinovic (2022). 99% False Positives: A Qualitative Study of SOC Analysts' Perspectives on Security Alarms. USENIX Security 2022.
- Link: https://www.usenix.org/conference/usenixsecurity22/presentation/alahmadi · Status: peer-reviewed (31st USENIX Security Symposium, pp. 2783–2800) · Verificado: sim
- Contribuição:
  - Survey online com 20 praticantes de SOC seguido de estudo qualitativo com 21 praticantes. Os participantes confirmam que as ferramentas geram muitos FPs e exigem validação manual dos alarmes. O "99%" aparece só no título: o resumo não traz uma taxa de FP medida.
  - Segundo os participantes, a maioria dos FPs são *benign triggers*: alarmes tecnicamente verdadeiros disparados por atividade legítima da organização. Os autores pedem que fornecedores e pesquisadores separem esses tipos de FP ao avaliar ferramentas.
  - A validação tediosa leva a burnout e dessensibilização. Os autores propõem cinco propriedades de alarmes de qualidade: *Reliable, Explainable, Analytical, Contextual, Transferable*.
- Relevância para o Guardião (inferência):
  - A distinção entre FP e *benign trigger* corresponde quase exatamente à separação `benign` vs `expected_admin` do schema. Isso sustenta reportar o FPR **por classe**, além do agregado.
  - As cinco propriedades podem servir de checklist para o Relato. A Evidência literal cobre *Explainable/Analytical*. O campo de risco de FP e o Contexto cobrem *Contextual*.

### [C-2] Kokulu, Soneji, Bao, Shoshitaishvili, Zhao, Doupé & Ahn (2019). Matched and Mismatched SOCs: A Qualitative Study on Security Operations Center Issues. ACM CCS 2019.
- Link: https://adamdoupe.com/publications/matched-and-mismatched-socs-ccs2019.md (cópia do autor; https://dl.acm.org/doi/10.1145/3319535.3354239 retornou 403) · DOI 10.1145/3319535.3354239 (como listado na cópia) · Status: peer-reviewed · Verificado: sim (via cópia do autor)
- Contribuição:
  - 18 entrevistas semiestruturadas com analistas e gestores de 13 SOCs internos e 5 terceirizados, em seis setores. O problema mais citado é a baixa visibilidade de rede e endpoints: cerca de 71% dos analistas e 60% dos gestores, segundo o texto.
  - Gestores e analistas divergem principalmente sobre velocidade de resposta e automação, métricas de avaliação e funcionalidade das ferramentas. Gestores querem mais automação. Parte dos analistas desconfia dela por causa de FPs.
  - Sobre FP, o texto é internamente inconsistente. A Seção 4.1.5 diz que 15 participantes não consideram FP um problema maior, e a Introdução diz que nenhum considera. A Tabela 2 marca "High False Positives Rate" para 12,50% dos analistas e 20,00% dos gestores.
- Ver também: Vielberth, Böhm, Fichtinger & Pernul (2020). *Security Operations Center: A Systematic Study and Open Challenges*. IEEE Access 8:227756–227779, DOI 10.1109/ACCESS.2020.3045514. Link: https://epub.uni-regensburg.de/44375/ (repositório institucional com metadados do publisher; IEEE Xplore abriu vazio) · peer-reviewed · Verificado: sim. A revisão sistemática conclui que a pesquisa sobre SOC se concentra em pessoas e tecnologia e negligencia os processos, sobretudo os não técnicos, que conectam as duas coisas.
- Relevância para o Guardião (inferência):
  - A desconfiança dos analistas em automação por causa de FPs e o conflito gestor × analista sustentam que as Propostas de contenção só valham após aprovação humana. Vielberth reforça que o artigo deve descrever o **processo**: quem aprova, como as regras são versionadas e como as decisões ficam registradas. Descrever só o modelo não basta.
  - Como baixa visibilidade é o problema nº 1 e o Recorte cobre uma única modalidade, o Guardião não deve concluir `benign` pela falta de evidência fora da janela. Ver [C-8].

### [C-3] Sundaramurthy, Bardas, Case, Ou, Wesch, McHugh & Rajagopalan (2015). A Human Capital Model for Mitigating Security Analyst Burnout. SOUPS 2015.
- Link: https://www.usenix.org/conference/soups2015/proceedings/presentation/sundaramurthy · Status: peer-reviewed (SOUPS 2015, pp. 347–359) · Verificado: sim
- Contribuição:
  - Estudo antropológico de seis meses num SOC corporativo, analisado com Grounded Theory. O modelo trata o burnout como um problema de gestão de capital humano, produzido por ciclos viciosos entre fatores humanos, técnicos e gerenciais.
  - O modelo foi aplicado a notas de campo de um SOC universitário e explicou os sintomas observados lá. Os autores sugerem como converter os ciclos viciosos em ciclos virtuosos.
- Relevância para o Guardião (inferência):
  - Automação que tira do analista o aprendizado e o controle pode alimentar esses ciclos. A Evidência literal e a hipótese CWE do Relato podem servir de material de aprendizado. Esse efeito precisa ser medido no estudo e não pode ser presumido.

### [C-4] Oesch, Bridges, Smith, Beaver, Goodall, Huffer, Miles & Scofield (2020). An Assessment of the Usability of Machine Learning Based Tools for the Security Operations Center. IEEE CPSCom 2020.
- Link: https://arxiv.org/abs/2012.09013 e https://www.osti.gov/biblio/1766395 (OSTI informa CPSCom 2020, DOI 10.1109/iThings-GreenCom-CPSCom-SmartData-Cybermatics50389.2020.00111) · Status: peer-reviewed (conferência; a versão arXiv é preprint) · Verificado: sim
- Contribuição:
  - Primeira avaliação *in situ* de usabilidade de ferramentas de ML para SOC: seis analistas de SOC da Marinha dos EUA usaram duas ferramentas num cyber range nacional.
  - Os autores acharam problemas graves de usabilidade. Os analistas não tinham um modelo mental de como os *scores* eram gerados, o que levou a desconfiança ou mau uso. Formação e anos de experiência não se correlacionaram com o desempenho.
- Relevância para o Guardião (inferência):
  - O Relato deve mostrar *por que* chegou ao veredito, com Evidência e Contexto usados, em vez de um score opaco. Um campo de "confiança" sem semântica operacional repetiria o problema descrito.
  - Com n = 6, a evidência é fraca, e o artigo do projeto não deve generalizar a partir dela.

---

## 2. Humano no loop, explicabilidade e LLMs em fluxos reais de SOC

### [C-5] Warnecke, Arp, Wressnegger & Rieck (2020). Evaluating Explanation Methods for Deep Learning in Security. IEEE EuroS&P 2020.
- Link: https://arxiv.org/abs/1906.02108 (o campo *comments* informa IEEE EuroS&P 2020) · Status: peer-reviewed · Verificado: sim (venue via arXiv; IEEE Xplore não aberto)
- Contribuição:
  - Propõe critérios para avaliar métodos de explicação em segurança: gerais, como acurácia da explicação, e específicos de segurança, como completude, eficiência e robustez.
  - Aplica os critérios a seis métodos em detecção de malware e descoberta de vulnerabilidades. Os métodos diferem muito entre si, e os autores dão recomendações de escolha.
- Relevância para o Guardião (inferência):
  - O *rationale* de um LLM é uma auto-explicação gerada pelo próprio modelo, não uma atribuição sobre o modelo. Os critérios de completude e robustez sugerem dois testes: se a Evidência citada basta para o veredito e se ela muda sob injeção.
  - A checagem literal de Evidência e IoC no log é uma verificação barata e determinística de parte da "acurácia da explicação".

### [C-6] Singh, Tariq, Jalalvand, Baruwal Chhetri, Nepal, Paris & Lochner (2025). LLMs in the SOC: An Empirical Study of Human-AI Collaboration in Security Operations Centres. arXiv (under review).
- Link: https://arxiv.org/abs/2508.18947 · Status: preprint · Verificado: sim
- Contribuição:
  - Analisa 3.090 consultas de 45 analistas ao longo de 10 meses. Os analistas usam o LLM como apoio sob demanda para entender situações e montar contexto. Eles não o usam para decisões de alto risco e mantêm a autoridade decisória.
  - A maioria das consultas trata de telemetria de baixo nível, como comandos, ou de redação técnica, em trocas curtas de 1 a 3 turnos. Cerca de 93% das consultas se alinham a competências do NICE Framework (dados do resumo).
- Ver também: Thurner, Jost, Horstmann, Ising, Groeber, Naiakshina & Schinzel (2026). *From Chasing Ghosts to Missed Attacks: Perspectives and Perceptions of SOC Practitioners on LLM Integration, Risks, and Readiness*. https://arxiv.org/abs/2608.00672 · preprint · Verificado: sim.
  - 25 entrevistas identificaram 15 casos de uso em 6 categorias.
  - Os praticantes ainda consideram inviável a análise de incidentes, por falta de profundidade técnica, de consciência de contexto e de conhecimento da organização.
  - Eles atribuem os limites sobretudo à prontidão do SOC e a fatores humanos, como *over-reliance*.
- Ver também: Banstola, Al Faisal, Dao, Irving, Lende & Ou (2026). *It is Not Yet Another Tool: Creating and Deploying an Agentic AI Companion in a Security Operations Center*. https://arxiv.org/abs/2609.06250 · preprint · Verificado: sim.
  - Os autores fizeram trabalho de campo por mais de um ano dentro de um SOC.
  - Em mais de 90% dos casos, a saída do *companion* foi reaproveitada no relatório de fechamento do ticket.
  - A confiança cresceu à medida que os analistas moldaram o comportamento da ferramenta.
- Relevância para o Guardião (inferência):
  - Os três trabalhos convergem com o desenho "modelo só relata, humano decide". O risco de *over-reliance* apontado por Thurner justifica que o Relato declare o risco de FP e os limites da janela.
  - A taxa de "reaproveitamento no relatório" de Banstola mede adoção, não correção. O artigo deve separar adoção, acurácia e benefício observado.

### [C-7] Wu, Velazco, Zhao, Meléndez Luján, Movva, Roy, Nguyen, Rodriguez, Wu, Albada, Kiseleva & Mudgerikar (2026). ExCyTIn-Bench: Evaluating LLM agents on Cyber Threat Investigation. ICML 2026 (PMLR 306).
- Link: https://proceedings.mlr.press/v306/wu26bd.html · Status: peer-reviewed (PMLR 306:136937–136980) · Verificado: sim
- Contribuição:
  - Benchmark montado num tenant Azure controlado, com ambiente SQL de 57 tabelas de log do Microsoft Sentinel e serviços relacionados. Tem 7.542 perguntas geradas a partir de grafos de investigação: o nó inicial é o contexto e o nó final é a resposta.
  - O melhor modelo atinge *reward* 0,606 no conjunto de teste (número do resumo). A investigação multi-hop continua difícil.
- Ver também: Deason et al. (2025). *CyberSOCEval: Benchmarking LLMs Capabilities for Malware Analysis and Threat Intelligence Reasoning* (parte do CyberSecEval 4). https://arxiv.org/abs/2509.20166 · preprint · Verificado: sim.
  - Modelos maiores e mais novos tendem a ir melhor.
  - *Test-time scaling* ajuda menos aqui do que em código e matemática.
  - Os benchmarks estão longe da saturação.
- Relevância para o Guardião (inferência):
  - Os dois benchmarks reforçam o escopo estreito do Guardião: triar um Recorte, e não conduzir uma investigação aberta.
  - Ancorar o *ground truth* em nós explícitos é análogo à checagem literal de IoC. A mesma ideia serve para gerar rótulos e casos da suíte a partir de grafos de cenário.

### [C-8] Tsegai, Kantchelian, Yao & Gao (2026). From Investigation Failures to Reliable SOC Agents: Understanding and Improving LLM-Based Alert Triage. arXiv.
- Link: https://arxiv.org/abs/2610.10608 · Status: preprint · Verificado: sim
- Contribuição:
  - ALERT-BENCH reproduz telemetria empresarial num SIEM ao vivo, com 1.247 alertas de um cenário multi-estágio. Os autores testaram cinco estratégias de agente: *single-pass tool use*, *iterative retrieval*, investigações amostradas, *self-review* e verificação explícita. Todas perderam pelo menos 40,4% dos alertas de ataque.
  - Alertas de ataque eram descartados com mais frequência quando as buscas não retornavam registros. O *self-review* no mesmo contexto teve correção líquida negativa. Os descartes não receberam investigação mais forte do que os escalonamentos.
  - O sistema proposto, AIDA, funciona assim:
    - Exige uma decisão proposta explícita antes do desafio.
    - Pede evidência mais forte para descartar.
    - Mantém um *Investigation Ledger* append-only.
    - Roda o desafio num contexto separado, com um juiz separado.
  - Resultados do AIDA: F1 de 0,958, contra 0,371–0,744 das outras estratégias. A FNR cai de 40,4% para 3,1%, e 18,4% dos alertas vão para analistas.
- Relevância para o Guardião (inferência):
  - O trabalho apoia diretamente a assimetria do projeto: rebaixar deve exigir mais evidência do que manter. Também apoia o registro append-only, já que o Runtime produz um ledger auditável. Ausência de registro no Recorte não é evidência de benignidade.
  - Como o *self-review* no mesmo contexto piora o resultado, a verificação deve ser determinística (feita pelo Runtime) ou rodar num contexto isolado, e não ser uma segunda passada do mesmo prompt.

---

## 3. Concept drift, rejeição e implantação

### [C-9] Pendlebury, Pierazzi, Jordaney, Kinder & Cavallaro (2019). TESSERACT: Eliminating Experimental Bias in Malware Classification across Space and Time. USENIX Security 2019.
- Link: https://www.usenix.org/conference/usenixsecurity19/presentation/pendlebury · Status: peer-reviewed (pp. 729–746) · Verificado: sim
- Contribuição:
  - Mostra que dois vieses inflam resultados publicados, com F1 de até 0,99 em malware Android. O viés espacial vem de proporções de classes que não representam a implantação real. O viés temporal vem de splits que treinam com conhecimento do futuro.
  - Propõe restrições de espaço e tempo para os experimentos e uma métrica de robustez esperada ao longo do tempo, com algoritmo de *tuning*. Avalia mitigações como *active learning* em três classificadores e 129 mil apps de mais de três anos.
- Relevância para o Guardião (inferência):
  - O split por grupo de cenário evita vazamento entre grupos, mas não elimina o viés temporal. Convém um hold-out temporal, com coletas e cenários mais recentes só no teste.
  - A proporção 45/45/10 é adequada ao treino. O FPR operacional deve ser estimado também com a proporção de classes esperada na operação.

### [C-10] Jordaney et al. (2017). Transcend: Detecting Concept Drift in Malware Classification Models. USENIX Security 2017 — e Barbero, Pendlebury, Pierazzi & Cavallaro (2022). Transcending Transcend: Revisiting Malware Classification in the Presence of Concept Drift. IEEE S&P 2022.
- Links: https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/jordaney (pp. 625–642) e https://arxiv.org/abs/2010.03856 (o campo *comments* informa aceite no IEEE S&P 2022 e aponta uma errata da versão publicada) · Status: peer-reviewed (ambos) · Verificado: sim (S&P via arXiv; IEEE Xplore não aberto)
- Contribuição:
  - Transcend usa *conformal evaluation* para comparar estatisticamente as amostras novas com as de treino. Assim detecta o envelhecimento do modelo antes que a acurácia caia de forma visível, em malware Android e Windows.
  - TRANSCENDENT formaliza a teoria e adiciona dois avaliadores conformes mais baratos. Na classificação com rejeição, os prováveis erros vão para análise de especialistas. A avaliação usa um dataset de 5 anos sem as fontes de viés experimental.
- Relevância para o Guardião (inferência):
  - Os dois trabalhos fundamentam a abstenção. Em vez de forçar um veredito, o Runtime pode rejeitar e encaminhar ao humano quando um score calibrado *fora* do LLM indicar não-conformidade.
  - Aplicar *conformal* a saídas JSON geradas por um LLM não é trivial. Isso aparece como lacuna.

### [C-11] Yang, Guo, Hao, Ciptadi, Ahmadzadeh, Xing & Wang (2021). CADE: Detecting and Explaining Concept Drift Samples for Security Applications. USENIX Security 2021.
- Link: https://www.usenix.org/conference/usenixsecurity21/presentation/yang · Status: peer-reviewed (pp. 2327–2344) · Verificado: sim
- Contribuição:
  - Detecta amostras individuais que se afastam das classes conhecidas, sem esperar muitos rótulos novos. Para isso, projeta os dados num espaço de baixa dimensão e aprende uma distância com *contrastive learning*.
  - Explica o drift por distância, em vez de explicar a fronteira de decisão. Foi avaliado em malware Android, em detecção de intrusão em rede e na base de malware de uma empresa.
- Relevância para o Guardião (inferência):
  - O Projetor determinístico pode sinalizar drift de formato ou modalidade *antes* de chamar o modelo: campos novos, parser falhando, distribuição de tokens fora do padrão. Recortes fora da distribuição iriam para revisão humana.

### [C-12] Arp, Quiring, Pendlebury, Warnecke, Pierazzi, Wressnegger, Cavallaro & Rieck (2022). Dos and Don'ts of Machine Learning in Computer Security. USENIX Security 2022.
- Link: https://www.usenix.org/conference/usenixsecurity22/presentation/arp (PDF dos autores consultado: https://mlsec.tu-berlin.de/docs/2022-sec.pdf) · Status: peer-reviewed (pp. 3971–3988; Distinguished Paper) · Verificado: sim
- Contribuição:
  - Dez armadilhas (Fig. 1 do PDF):
    - Coleta e rotulagem: *sampling bias*, *label inaccuracy*.
    - Projeto e aprendizado: *data snooping* (inclui *temporal snooping*), *spurious correlations*, *biased parameters*.
    - Avaliação: *inappropriate baselines*, *inappropriate measures*, *base rate fallacy*.
    - Implantação: *lab-only evaluation*, *inappropriate threat model*.
  - As armadilhas são frequentes em 30 artigos de conferências de ponta da última década. Os autores medem o impacto em quatro domínios e propõem recomendações.
- Relevância para o Guardião (inferência):
  - Serve de checklist para o artigo. *Base rate fallacy*: FPR medido num teste balanceado engana. *Lab-only*: logs sintéticos ou curados. *Inappropriate threat model*: a suíte adversarial precisa declarar as capacidades do atacante.
  - *Spurious correlations*: IDs pseudonimizados ou artefatos do dataset de origem podem virar atalhos para o rótulo. Uma ablação por fonte e por modalidade ajuda a detectar isso.

---

## 4. Injeção de prompt e segurança de sistemas com LLM

### [C-13] Greshake, Abdelnabi, Mishra, Endres, Holz & Fritz (2023). Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. ACM AISec 2023.
- Link: https://arxiv.org/abs/2302.12173 e https://cispa.de/en/research/publications/77133-not-what-you-ve-signed-up-for-compromising-real-world-llm-integrated-applications-with-indirect-prompt-injection (a página do CISPA informa AISec 2023) · Status: peer-reviewed (workshop) · Verificado: sim (venue via CISPA; ACM DL não aberto)
- Contribuição:
  - Define *indirect prompt injection*: o atacante planta instruções em dados que o LLM vai recuperar, sem precisar de acesso à interface. Propõe uma taxonomia de impactos que inclui roubo de dados, *worming* e contaminação de ecossistemas de informação.
  - Demonstra os ataques contra o Bing Chat (GPT-4) e engines de *code completion*. Argumenta que processar prompts recuperados equivale, na prática, a executar código arbitrário.
- Relevância para o Guardião (inferência):
  - O Registro (o log) é exatamente esse canal indireto: user-agent, URL, linha de comando e username são controláveis pelo atacante. Isso fundamenta a premissa de que todo Registro é hostil.

### [C-14] Liu, Jia, Geng, Jia & Gong (2024). Formalizing and Benchmarking Prompt Injection Attacks and Defenses. USENIX Security 2024.
- Link: https://www.usenix.org/conference/usenixsecurity24/presentation/liu-yupei · Status: peer-reviewed (pp. 1831–1847) · Verificado: sim
- Contribuição:
  - Framework formal no qual os ataques existentes são casos especiais. A partir dele, os autores derivam um ataque que combina os existentes.
  - Avaliação sistemática de 5 ataques e 10 defesas (de prevenção e de detecção) em 10 LLMs e 7 tarefas. A plataforma de benchmark é pública.
- Relevância para o Guardião (inferência):
  - Fornece uma taxonomia e um gerador de ataques de referência para as mutações de treino e para a suíte adversarial. Para não medir memorização, as famílias e os templates usados no treino devem ser diferentes dos usados na suíte.

### [C-15] Zverev, Abdelnabi, Tabesh, Fritz & Lampert (2025). Can LLMs Separate Instructions From Data? And What Do We Even Mean By That? ICLR 2025.
- Link: https://arxiv.org/abs/2403.06833 (o campo *comments* informa conference paper no ICLR 2025) · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Define formalmente a separação entre instrução e dados, com uma variante empírica calculável a partir das saídas. Publica o dataset SEP.
  - Todos os modelos avaliados falham em atingir alta separação. *Prompt engineering* e fine-tuning não melhoram a separação de forma substancial ou reduzem a utilidade (afirmações do resumo).
- Relevância para o Guardião (inferência):
  - É a evidência mais direta contra confiar que o modelo respeite Contexto vs Registro só porque foi treinado para isso. A separação precisa ser imposta também fora do modelo, no Projetor e no Runtime.

### [C-16] Chen, Piet, Sitawarin & Wagner (2025). StruQ: Defending Against Prompt Injection with Structured Queries. USENIX Security 2025 — e Chen, Zharmagambetov, Mahloujifar, Chaudhuri, Wagner & Guo (2025). SecAlign: Defending Against Prompt Injection with Preference Optimization. ACM CCS 2025.
- Links: https://www.usenix.org/conference/usenixsecurity25/presentation/chen-sizhe (pp. 2383–2400) e https://arxiv.org/abs/2410.05451 (o campo *comments* informa ACM CCS 2025, DOI relacionado 10.1145/3719027.3744836). Detalhes do StruQ conferidos em https://arxiv.org/html/2402.06363v2 · Status: peer-reviewed (ambos) · Verificado: sim
- Contribuição:
  - **StruQ** separa prompt e dados em dois canais.
    - Um front-end seguro usa tokens especiais reservados como delimitadores. Ele filtra dos dados, de forma repetida, as strings delimitadoras até que não reste nenhuma.
    - O modelo é fine-tuned para ignorar instruções na porção de dados.
    - Na Tabela 2 da versão arXiv v2, os ataques manuais caem para 0–2%. TAP ainda atinge 9–36% e GCG atinge 56–58% (Llama/Mistral).
    - Os próprios autores dizem que o StruQ não é uma defesa completa no pior caso.
  - **SecAlign** aplica *preference optimization* com pares de saída segura e saída insegura sobre entradas injetadas. Segundo o resumo, reduz a taxa de sucesso de várias injeções para menos de 10%, inclusive contra ataques mais sofisticados que os do treino, mantendo a utilidade.
- Relevância para o Guardião (inferência):
  - Os dois trabalhos dão uma receita concreta para o Recorte: delimitadores reservados para Contexto e Registro, e o Projetor removendo ou escapando esses delimitadores do Registro de forma determinística. As mutações de treino com injeções do projeto são uma variante de StruQ/SecAlign.
  - Os números acima vêm de avaliações não adaptativas, e [C-17] mostra que eles não se sustentam contra um atacante adaptativo.

### [C-17] Nasr, Carlini, Sitawarin, Schulhoff, Hayes, Ilie, Pluto, Song, Chaudhari, Shumailov, Thakurta, Xiao, Terzis & Tramèr (2026). The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections. USENIX Security 2026.
- Link: https://www.usenix.org/conference/usenixsecurity26/presentation/nasr · Status: peer-reviewed (pp. 1467–1486) · Verificado: sim
- Contribuição:
  - Defende que defesas sejam avaliadas contra atacantes adaptativos, que ajustam a estratégia à defesa específica. Usa gradiente, RL, *random search* e exploração guiada por humanos.
  - Contorna 12 defesas recentes. Sob ataque adaptativo, a maioria passa a ter taxa de sucesso de ataque acima de 90%, embora tenha reportado originalmente taxas próximas de zero (resumo).
- Ver também: Pandya, Labunets, Gao & Fernandes (2025). *May I have your Attention? Breaking Fine-Tuning based Prompt Injection Defenses using Architecture-Aware Attacks*. https://arxiv.org/abs/2507.07417 · preprint · Verificado: sim. Um ataque *white-box* baseado em atenção contra SecAlign, SecAlign++ e StruQ atinge até 85–95% de sucesso em prompts não vistos, com aumento modesto do orçamento de tokens do atacante.
- Relevância para o Guardião (inferência):
  - Um gate de "zero rebaixamentos" sobre uma suíte **estática** é o tipo de avaliação que esse trabalho critica. Como os pesos do Gemma são abertos, o cenário *white-box* é realista: o atacante pode otimizar contra o modelo base. A transferência desse ataque para o adaptador LoRA é uma hipótese a testar.
  - A suíte estática deve funcionar como teste de regressão. A alegação de robustez exige rodadas adaptativas (otimização contra o adaptador e *red team* humano), e a segurança operacional não pode depender só do modelo.

### [C-18] Karanjai, Lu, Hegadehalli Madhavarao, Xu & Shi (2026). Context Contamination in LLM Analysis of Network Security Logs: Poison with Passive Prompt Injection and Mitigation Evaluation. USENIX Security 2026.
- Link: https://www.usenix.org/conference/usenixsecurity26/presentation/karanjai · Status: peer-reviewed (pp. 1507–1526) · Verificado: sim
- Contribuição:
  - Define *passive prompt injection*: payloads gravados em campos de log persistem no armazenamento e só são executados quando o analista consulta o LLM. O benchmark LogInject-1.0 tem 12.847 entradas, das quais 2.569 são adversariais.
  - Testa três LLMs de produção e quatro objetivos: ocultar atividade, gerar FPs, exfiltrar informação e sequestrar a saída. A taxa de sucesso chega a 88,2%, com média de 83,4%. A técnica *Context Stitching* fragmenta o payload em várias entradas para escapar de filtros *stateless* e atinge 76,4%.
  - A defesa em camadas (filtragem de entrada, *prompt hardening* e validação de saída) reduz os ataques em 90,4%, mas deixa 8,4% de vulnerabilidade residual. Os autores descrevem o cenário como um problema de *confused deputy* e recomendam defesa em profundidade e supervisão humana.
- Ver também: Landauer, Skopik, Wurzenberger, Górski & Krzysztoń (2026). *Just Testing, Move Along: Evasion of LLM-based System Log Interpretation by Prompt Injection*. https://arxiv.org/abs/2607.24174 · preprint · Verificado: sim.
  - Os exemplos adversariais são construídos a partir de logs de ataques reais.
  - As injeções fazem traços maliciosos com IoCs claros serem classificados como benignos.
  - As explicações geradas pelos LLMs frequentemente revelam a manipulação e poderiam servir de sinal de detecção.
  - O resumo não traz números.
- Ver também: Pandey & Bhujang (2026). *Poisoning the Watchtower: Prompt Injection Attacks Against LLM-Augmented Security Operations Through Adversarial Log Content*. https://arxiv.org/abs/2605.24421 · preprint · Verificado: sim. Números do resumo:
  - Taxonomia em quatro classes: S1 override direto, S2 persona hijack, S3 manipulação de contexto, S4 ofuscação.
  - Teste com gpt-4o-mini em 48 combinações de estratégia, defesa e tarefa.
  - O override direto (S1) teve 0% de supressão.
  - Persona hijack suprimiu 68% dos logs maliciosos sob classificador ingênuo.
  - Sumarização é a tarefa de maior risco: 96% de sucesso sem defesa e 38% com saída restrita.
  - A média de sucesso caiu de 26,6% para 11,8% com a defesa mais forte.
  - Um "analista mock" determinístico previu mal o comportamento real do modelo.
- Relevância para o Guardião (inferência):
  - É a literatura mais próxima do Guardião. O objetivo "ocultar atividade" corresponde ao rebaixamento de veredito. O objetivo "gerar FP" mostra que o atacante também pode **inflar** alertas para causar fadiga, então a suíte deve medir as duas direções.
  - *Context Stitching* ataca exatamente a janela multi-linha do Recorte. A saída restrita (JSON) reduz o risco mas não o elimina, e o campo livre de *rationale* é o mais exposto. Simular o atacante com um mock determinístico não substitui testar o modelo real.

### [C-19] OWASP GenAI Security Project (2025). OWASP Top 10 for LLM and Gen AI Applications 2025 — e MITRE ATLAS AML.T0051; MITRE ATT&CK T1698 e T1685.007.
- Links: https://genai.owasp.org/llm-top-10/ · https://d3fend.mitre.org/offensive-technique/attack/AML.T0051/ (espelho MITRE D3FEND da técnica ATLAS; atlas.mitre.org não renderizou conteúdo) · https://attack.mitre.org/techniques/T1698/ · https://attack.mitre.org/techniques/T1685/007/ · Status: documento de organização (não acadêmico) · Verificado: sim
- Contribuição:
  - O OWASP 2025 lista 10 riscos, entre eles LLM01 *Prompt Injection*, LLM05 *Improper Output Handling* e LLM06 *Excessive Agency*. O MITRE ATLAS AML.T0051 (*LLM Prompt Injection*) tem as sub-técnicas *Direct* (.000), *Indirect* (.001) e *Triggered* (.002).
  - O ATT&CK incluiu em setembro de 2026 a T1698 *Indirect Prompt Injection* (tática Execution) e a T1685.007 *Impair Autonomous Defenses* (tática Defense Impairment). A T1685.007 descreve adversários que usam injeção indireta para fazer ferramentas defensivas com IA ignorar dados, deixar de alertar ou abortar a análise.
  - As mitigações da T1685.007 incluem auditar o status, a origem e o motivo de término da análise (M1047). Também incluem impedir que o conteúdo do artefato controle o fluxo de trabalho (M1038). A detecção DET0943 correlaciona o conteúdo ingerido com supressão de detecção ou mudança de decisão de segurança.
- Relevância para o Guardião (inferência):
  - A T1685.007 descreve exatamente a ameaça ao Guardião e dá ao artigo um vocabulário padrão para o *threat model*. A DET0943 sugere registrar no ledger cada mudança de veredito que ocorra junto com conteúdo de aparência instrucional no Registro.
  - LLM05 e LLM06 apoiam o desenho: a saída do modelo é tratada como não confiável (validação de schema e regras versionadas) e o modelo não tem agência.

---

## 5. Arquiteturas que separam decisão probabilística de ação determinística; integração em SIEM/SOAR

### [C-20] Debenedetti, Shumailov, Fan, Hayes, Carlini, Fabian, Kern, Shi, Terzis & Tramèr (2025). Defeating Prompt Injections by Design (CaMeL). arXiv.
- Link: https://arxiv.org/abs/2503.18813 · Status: preprint · Verificado: sim
- Contribuição:
  - CaMeL envolve o LLM numa camada de sistema que extrai o fluxo de controle e o fluxo de dados da consulta confiável. Dados não confiáveis recuperados pelo LLM não conseguem alterar o fluxo do programa. *Capabilities* impedem exfiltração e aplicam políticas a cada chamada de ferramenta.
  - No AgentDojo, CaMeL resolve 77% das tarefas com segurança demonstrável (*provable*), contra 84% de um sistema sem defesa.
- Relevância para o Guardião (inferência):
  - É o modelo de referência para "segurança que não depende da robustez do modelo". Com proveniência por campo (Contexto vs Registro) no estilo das *capabilities*, o Runtime pode decidir de forma determinística se um rebaixamento é admissível.
  - A perda de 84% para 77% antecipa o trade-off do projeto: restringir rebaixamentos tende a aumentar o FPR operacional, e isso deve ser medido.

### [C-21] Beurer-Kellner, Buesser, Creţu, Debenedetti, Dobos, Fabian, Fischer, Froelicher, Grosse, Naeff, Ozoani, Paverd, Tramèr & Volhejn (2025). Design Patterns for Securing LLM Agents against Prompt Injections. arXiv.
- Link: https://arxiv.org/abs/2506.08837 (detalhes conferidos em https://arxiv.org/html/2506.08837v3) · Status: preprint · Verificado: sim
- Contribuição:
  - Seis padrões: Action-Selector, Plan-Then-Execute, LLM Map-Reduce, Dual LLM, Code-Then-Execute e Context-Minimization. O princípio comum: depois que o agente ingere entrada não confiável, ele deve ser restringido de forma que essa entrada não consiga disparar ações com consequências.
  - Dez estudos de caso, nenhum de segurança ou análise de logs. Vários restringem a saída a formatos fixos: booleano, categoria ou objeto estruturado obtido por *constrained decoding*.
- Ver também: Boboila, Cadet, Koh, Balasubramanian, Van Bruggen, Chin & Oprea (2026). *BlueSTAR: Tiered Agentic Architecture for Autonomous Cyber Defense*. https://arxiv.org/abs/2609.11852 · preprint · Verificado: sim.
  - A arquitetura converte telemetria de alto volume em IoCs compactos.
  - Mantém resposta determinística rápida para ameaças conhecidas e usa raciocínio de LLM para casos que exigem contexto.
  - Foi avaliada em dois cyber ranges IT/OT com sete cadeias de ataque.
  - O resumo não menciona aprovação humana nem traz números de resultado.
- Relevância para o Guardião (inferência):
  - O Guardião se aproxima de LLM Map-Reduce e Dual LLM. Um modelo "quarentenado", sem ferramentas, processa um único Recorte e devolve JSON restrito. Um componente privilegiado e determinístico, o Runtime, decide o que fazer. Isso apoia diretamente o desenho.
  - A proteção vem de limitar o que a saída pode causar, não de tornar o modelo imune. O veredito continua manipulável, e o dano da injeção fica restrito a rebaixar ou inflar alertas. É isso que a suíte adversarial deve medir.

### [C-22] Zhao, Zhang, Tian, Xie, Liu & Wang (2025). Information-Dense Reasoning for Efficient and Auditable Security Alert Triage (AIDR). arXiv.
- Link: https://arxiv.org/abs/2512.08169 · Status: preprint · Verificado: sim
- Contribuição:
  - Framework híbrido cloud-edge. Cada alerta é destilado em 3 a 5 bullets de alta informação, o que reduz os tokens em 68%. *Experts* de domínio treinados com LoRA rodam on-premises e geram JSON pronto para SOAR. Um LLM na nuvem faz o roteamento entre eles.
  - Os autores relatam redução de 40,6% na latência em relação a Chain-of-Thought e maior acurácia (sem números de acurácia no resumo). Também defendem auditabilidade e residência de dados.
- Relevância para o Guardião (inferência):
  - É o precedente mais próximo do projeto: LoRA local, JSON estrito e integração com SOAR. Também apoia raciocínio curto (`enable_thinking=false`) por custo e latência. O trabalho não trata injeção, e o roteador na nuvem seria uma superfície de ataque adicional.
  - Nenhuma fonte encontrada mede latência ou memória para modelos de cerca de 4B em Apple Silicon. O projeto pode contribuir com tokens/s e pico de RAM por Recorte.

---

## Lacunas observadas

1. **Injeção em logs contra modelos pequenos, locais e fine-tuned.** Os estudos de injeção em logs usam modelos de produção ou de nuvem: Karanjai testa três LLMs de produção, Pandey usa gpt-4o-mini e Landauer usa "LLMs de estado da arte". Não encontrei avaliação de um modelo de cerca de 4B com LoRA e saída JSON estrita.
2. **Canais de dados com autoridade assimétrica.** StruQ e SecAlign separam *instrução* de *dados*. Não encontrei trabalho que avalie **dois canais de dados** (Contexto confiável e Registro não confiável) com a regra "só um deles pode rebaixar". O desenho do Guardião é novo nesse ponto, o que é uma oportunidade de contribuição, mas sem evidência prévia a favor ou contra.
3. **Drift e abstenção para LLM generativo.** TESSERACT, Transcend e CADE tratam classificadores sobre *features*. Não achei método conformal ou de rejeição calibrada para saída estruturada de LLM em triagem de logs, nem uma avaliação temporal no estilo TESSERACT para esse caso.
4. **FPR operacional com taxas-base realistas.** O ALERT-BENCH foca em FNs. Os estudos de SOC sobre FP são qualitativos ([C-1], [C-2]). Faltam medidas de FPR de triagem com LLM sob a proporção de classes da operação.
5. **Fatores humanos do Relato.** Nenhum estudo testa se campos como "risco de FP" ou "hipótese CWE" melhoram a decisão do analista ou induzem *automation bias*. A amostra do único estudo *in situ* de ML em SOC é pequena (n = 6, [C-4]).
6. **Edge e local.** Não há medições de latência, custo ou memória em Apple Silicon. O AIDR ([C-22]) é o único que quantifica latência com LoRA on-prem, e em outro hardware.
7. **Ataque em duas direções.** A maioria dos trabalhos mede supressão de alertas. Só Karanjai inclui geração de FP como objetivo. Inflar alertas para causar fadiga é pouco estudado.
8. **Limites desta revisão.** ACM DL e IEEE Xplore não abriram. Os venues de Kokulu, Vielberth, Warnecke, Transcendent, SecAlign e Zverev vieram de cópia do autor, repositório institucional ou *comments* do arXiv. Não verifiquei se o template do Gemma 4 tem papel de sistema ou tokens reservados utilizáveis como delimitadores, o que é relevante para aplicar StruQ ao Recorte. Não pesquisei o Shirudo.

## Controvérsias e resultados conflitantes

- **FP é o problema central do SOC?** Alahmadi ([C-1]) relata FPs dominantes, sobretudo *benign triggers*. Kokulu ([C-2]) relata que 15 de 18 participantes não veem FP como problema maior, mas o próprio texto é inconsistente (a Introdução diz "nenhum") e cinco participantes se preocupam com o volume de alertas não filtrados. Parte da diferença é de definição: Alahmadi separa FP técnico de *benign trigger*.
- **Defesas por fine-tuning.** StruQ e SecAlign ([C-16]) relatam taxas de sucesso de ataque baixas contra ataques manuais e conhecidos. Pandya relata 85–95% em *white-box* e Nasr relata mais de 90% com ataques adaptativos ([C-17]). Zverev ([C-15]) diz que fine-tuning não melhora a separação de forma substancial. O resultado depende do modelo de ameaça (*white-box* ou *black-box*, estático ou adaptativo), e os trabalhos que propõem defesas tendem a usar o modelo de ameaça mais fraco.
- **Eficácia de injeções simples.** Pandey encontra 0% de supressão com override direto no gpt-4o-mini, enquanto Karanjai relata até 88,2% de sucesso em três LLMs de produção ([C-18]). A diferença depende do modelo, da tarefa (sumarização é mais vulnerável que classificação) e do objetivo do ataque.
- **Autoverificação pelo LLM.** O ALERT-BENCH ([C-8]) mostra correção líquida negativa no *self-review* feito no mesmo contexto. Landauer ([C-18]) sugere que as explicações do LLM revelam a manipulação. Os dois resultados são compatíveis se a checagem ocorrer em contexto separado ou por um detector externo, mas não há consenso.
- **Utilidade real de LLMs no SOC.** Banstola relata mais de 90% de reaproveitamento da saída, enquanto Thurner relata que a análise de incidentes ainda é inviável ([C-6]). O ExCyTIn tem *reward* máximo de 0,606 ([C-7]), e no ALERT-BENCH todas as estratégias perdem pelo menos 40,4% dos ataques ([C-8]). A divergência acompanha a diferença entre tarefas de baixo nível (redação, explicação de comandos) e investigação.
- **Segurança vs utilidade.** CaMeL cai de 84% para 77% de tarefas resolvidas ([C-20]), e Zverev aponta perda de utilidade com fine-tuning. Restringir o modelo tem custo, e no Guardião esse custo provavelmente aparece como FPR maior. Isso é inferência.

## O que confirma ou desafia as decisões do projeto

**Confirma (com ressalvas):**
- **Modelo que só relata e Runtime determinístico com aprovação humana.** Apoiado pelo princípio dos Design Patterns ([C-21]) e pelo CaMeL ([C-20]). Também é coerente com a mitigação M1038 da T1685.007 ([C-19]), com a recomendação de supervisão humana de Karanjai ([C-18]), com a preferência dos analistas por manter a decisão ([C-6]) e com a desconfiança da automação causada por FPs ([C-2]).
- **Projetor determinístico e saída JSON restrita.** O desenho é análogo a LLM Map-Reduce e Dual LLM ([C-21]). AIDR e BlueSTAR também destilam a telemetria antes do LLM ([C-22], [C-21]). Pandey mostra que saída restrita reduz o sucesso dos ataques sem zerá-lo ([C-18]).
- **Checagem literal de IoC e Evidência.** Alinhada às propriedades *Explainable/Analytical* de Alahmadi ([C-1]) e ao *ground truth* ancorado do ExCyTIn ([C-7]).
- **FPR medido em `benign`/`expected_admin`.** Fundamentado pela distinção de *benign triggers* ([C-1]). A literatura sugere reportar as duas classes separadamente.
- **Rebaixar exige mais evidência.** O AIDA ([C-8]) obtém o maior ganho justamente ao exigir evidência mais forte para descartar alertas.

**Desafia:**
- **A separação Contexto/Registro basta como defesa? Não, segundo a literatura.**
  - Nenhum modelo avaliado separa bem instrução de dados ([C-15]).
  - Nenhuma das defesas testadas resolve o problema ([C-14]).
  - Mesmo com tokens reservados e filtragem de delimitadores, GCG ainda atinge 56–58% contra StruQ ([C-16]).
  - Ataques adaptativos e *white-box* passam de 85–90% ([C-17]).
  - Defesa em camadas deixa 8,4% residual ([C-18]).

  A separação é uma mitigação necessária, mas não é garantia. Recomendações (inferência):
  - (a) Impor a regra "só o Contexto rebaixa" **no Runtime**, e não apenas no treino. O rebaixamento só é aceito se o Relato citar Evidência cujo trecho está literalmente no Contexto, verificado por busca literal como já se faz com os IoCs. Caso contrário, o Runtime mantém o veredito mais severo ou encaminha ao humano (*fail-closed*).
  - (b) Usar delimitadores reservados e fazer o Projetor escapar ou remover esses delimitadores do Registro de forma determinística, como no StruQ.
  - (c) Tratar o *rationale* como não confiável e nunca usá-lo como gatilho de regra.
- **Fine-tuning contra injeção funciona? Parcialmente.** Reduz a taxa de sucesso contra ataques conhecidos e estáticos e generaliza um pouco ([C-16]). Não resiste a ataques adaptativos, sobretudo *white-box* ([C-17]), e os pesos do Gemma são públicos. As mutações de treino são *hardening* útil, mas não sustentam o argumento de segurança do artigo, que precisa vir do Runtime.
- **O gate "zero alertas rebaixados por injeção" pode dar falsa confiança ([C-17]).** Sugestões (inferência):
  - Manter os geradores e templates da suíte disjuntos dos usados nas mutações de treino.
  - Incluir ataques adaptativos: otimização contra o próprio adaptador, *Context Stitching* entre linhas do Recorte, *persona hijack* e tags de fechamento forjadas ([C-18]).
  - Reportar a taxa de sucesso de ataque com intervalo de confiança. Zero sucessos em *n* casos só limita a taxa a cerca de 3/*n* com 95% de confiança (regra de três).
  - Medir também injeções que **inflam** alertas.
- **Split por grupo não basta contra drift.** É preciso tratar o *temporal snooping* com hold-out temporal ([C-9], [C-12]), além de considerar abstenção calibrada fora do LLM ([C-10]) e checagem de drift de formato no Projetor ([C-11]).
- **Taxa-base.** O FPR medido num teste com cerca de 45% de benignos não representa a operação ([C-12], *base rate fallacy*). Convém reportar também precisão e alertas por dia sob taxas-base realistas.
- **Ausência de evidência.** O Recorte cobre uma modalidade, e baixa visibilidade é a queixa nº 1 dos SOCs ([C-2]). No ALERT-BENCH, buscas sem resultado levaram ao descarte de ataques ([C-8]). Por isso o Guardião não deve rebaixar por falta de evidência e precisa de um modo explícito de "evidência insuficiente".
