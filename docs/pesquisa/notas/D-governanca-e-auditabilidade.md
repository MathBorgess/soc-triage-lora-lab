# Tema D — Governança, proveniência e auditabilidade de dados e modelos

> Revisão feita em 2026-11-25 por Claude Opus 5.5 (`claude-opus-5-5`) no Claude Code. As fontes foram abertas nesta sessão por WebFetch, por PDF extraído localmente ou pelo painel de navegador (EUR-Lex, ISO, Câmara).
> "Verificado: sim" quer dizer que a página primária ou um registro bibliográfico confiável (OpenAlex) foi aberto e que venue, ano e status vieram dele. Quando a página da editora bloqueou o acesso (ACM DL e Nature retornaram 403 ou pediram login), isso está anotado.
> As seções "Relevância para o Guardião" são **inferências** sobre o projeto, não afirmações das fontes. Nada aqui é aconselhamento jurídico.

---

## 1. Documentação de dados e modelos

### [D-1] Gebru, Morgenstern, Vecchione, Wortman Vaughan, Wallach, Daumé III, Crawford (2021). Datasheets for Datasets. Communications of the ACM 64(12):86–92. DOI 10.1145/3458723.
- Link: https://arxiv.org/abs/1803.09010 (o comentário do arXiv diz "Published in CACM, December 2021") · metadados do periódico: https://api.openalex.org/works/doi:10.1145/3458723 · Status: peer-reviewed · Verificado: sim (a página da ACM retornou 403; volume, número e páginas vêm do OpenAlex)
- Trabalho complementar verificado: Bender & Friedman (2018). *Data Statements for Natural Language Processing*. TACL 6:587–604. DOI 10.1162/tacl_a_00041. https://aclanthology.org/Q18-1041/ (peer-reviewed). Propõe "data statements" como prática profissional em PLN para explicitar a população e a variedade linguística dos dados.
- Contribuição:
  - Propõe que todo dataset traga uma "datasheet", por analogia às folhas de dados de componentes eletrônicos. Ela documenta motivação, composição, processo de coleta e usos recomendados.
  - O objetivo declarado é melhorar a comunicação entre quem cria e quem consome datasets, e assim reforçar a transparência e a accountability.
- Relevância para o Guardião (inferência):
  - As perguntas da datasheet sobre composição e coleta são o lugar natural para registrar licença, revisão e hash de origem de cada fonte, além da regra de pseudonimização (C1…) e da divisão por grupo de incidente.
  - Uma datasheet por versão (ex.: v12) dá ao artigo um artefato citável e auditável, separado do código.

### [D-2] Mitchell, Wu, Zaldivar, Barnes, Vasserman, Hutchinson, Spitzer, Raji, Gebru (2019). Model Cards for Model Reporting. FAT* '19 (ACM). DOI 10.1145/3287560.3287596.
- Link: https://arxiv.org/abs/1810.03993 · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Propõe "model cards": documentos curtos que acompanham um modelo treinado. Eles trazem avaliação desagregada por grupos, contexto de uso pretendido e procedimento de avaliação.
  - Os autores dizem que o formato serve para documentar qualquer modelo treinado, embora os exemplos sejam de visão computacional e PLN.
- Relevância para o Guardião (inferência):
  - Cada adaptador liberado pode ter um model card que registre o uso pretendido ("apenas relata; contenção exige humano"), as métricas oficiais (Pydantic Pass Rate, IoC Hallucination, Macro-F1, FPR) e os limites. O card seria um anexo da Liberação vinculado aos mesmos hashes.
  - A avaliação desagregada sugere relatar FPR por fonte de log e por família de exemplos, além do valor agregado.

### [D-3] Pushkarna, Zaldivar, Kjartansson (2022). Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI. ACM FAccT 2022. DOI 10.1145/3531146.3533231.
- Link: https://arxiv.org/abs/2204.01075 · venue e DOI: https://api.openalex.org/works/doi:10.1145/3531146.3533231 · Status: peer-reviewed · Verificado: sim (a página da ACM retornou 403)
- Contribuição:
  - Define Data Cards como "structured summaries of essential facts" sobre datasets ao longo do ciclo de vida: origem, coleta, anotação, uso pretendido e avaliação.
  - Traz frameworks de design centrado em pessoas, dois estudos de caso e lições de mais de 20 Data Cards em produção no Google.
- Relevância para o Guardião (inferência):
  - O foco em "como foi anotado" encaixa na diferença entre aprovação linha a linha e aprovação por família. O Data Card deveria dizer, para cada subconjunto, qual regime de aprovação foi aplicado e com qual amostra.

### [D-4] Akhtar, Benjelloun, Conforti, Foschini et al. (2024). Croissant: A Metadata Format for ML-Ready Datasets. NeurIPS 2024 Datasets & Benchmarks Track (versão curta no DEEM/SIGMOD 2024, DOI 10.1145/3650203.3663326). Inclui a especificação Croissant RAI 1.0 (MLCommons, 2024).
- Link: https://arxiv.org/abs/2403.19546 · RAI: https://docs.mlcommons.org/croissant/docs/croissant-rai-spec.html · Status: peer-reviewed (artigo); documento técnico (especificação RAI 1.0, publicada em 2024-03-06) · Verificado: sim
- Contribuição:
  - Croissant é um vocabulário de metadados, legível por máquina, que repositórios e frameworks de ML usam para descrever datasets. Hoje já cobre centenas de milhares de datasets.
  - A extensão RAI acrescenta propriedades como `rai:dataCollection`, `rai:dataAnnotationProtocol`, `rai:personalSensitiveInformation`, `rai:dataReleaseMaintenancePlan` e `rai:machineAnnotationTools`. No caso de uso "regulatory compliance", pede o método de geração de dados sintéticos.
  - Na versão 1.0, o caso de uso "Traceability" ainda não tem propriedades definidas, e a página não menciona W3C PROV.
- Relevância para o Guardião (inferência):
  - Publicar o dataset curado com Croissant + RAI tornaria a governança legível por máquina. `machineAnnotationTools` e o campo de dados sintéticos são justamente o que falta no card do opensec-triage.
  - A lacuna de rastreabilidade do RAI 1.0 é um espaço onde o projeto pode contribuir: ligar hash de origem → exemplo → versão.

## 2. Auditoria, accountability, reprodutibilidade e proveniência

### [D-5] Raji, Smart, White, Mitchell, Gebru, Hutchinson, Smith-Loud, Theron, Barnes (2020). Closing the AI Accountability Gap: Defining an End-to-End Framework for Internal Algorithmic Auditing. FAT* 2020, pp. 33–44. DOI 10.1145/3351095.3372873.
- Link: https://arxiv.org/abs/2001.00973 · metadados: https://api.openalex.org/works/doi:10.1145/3351095.3372873 · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Propõe o SMACTR, um framework de auditoria **interna** que acompanha todo o ciclo de desenvolvimento. Cada etapa gera documentos, e o conjunto deles forma o relatório de auditoria.
  - O objetivo é detectar danos antes da implantação e rastrear problemas até a origem, comparando decisões com princípios declarados.
- Relevância para o Guardião (inferência):
  - A Liberação (aprovação escrita + hashes) funciona como um "gate" de auditoria interna. O SMACTR sugere que cada etapa anterior (curadoria, inspeção de tokens, treino, avaliação) também produza um artefato assinável.
  - Quando o mesmo responsável cura, aprova e libera, a separação de funções é fraca. O artigo deve declarar essa limitação.

### [D-6] Pineau, Vincent-Lamarre, Sinha, Larivière, Beygelzimer, d'Alché-Buc, Fox, Larochelle (2021). Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program). JMLR 22(164):1–20.
- Link: https://www.jmlr.org/papers/v22/20-303.html · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Relata o programa de reprodutibilidade do NeurIPS 2019, com três partes: política de submissão de código, desafio comunitário de reprodução e um checklist de reprodutibilidade no envio de artigos.
  - Define reprodutibilidade como obter resultados semelhantes com o mesmo código e os mesmos dados, e aponta seu papel na redução de erros não intencionais.
- Relevância para o Guardião (inferência):
  - Diretórios por execução com configuração efetiva, revisões de pesos, tokenizer e dados, versões da stack e `seed: 42` já cobrem boa parte do checklist. Falta verificar se os dados e os adaptadores podem ser redistribuídos para reprodução externa, o que depende das licenças (ver D-8).

### [D-7] W3C — Moreau & Missier (eds.) (2013). PROV-DM: The PROV Data Model. W3C Recommendation, 30 abr. 2013.
- Link: https://www.w3.org/TR/prov-dm/ · Status: norma técnica (W3C Recommendation) · Verificado: sim
- Contribuição:
  - Define o modelo de proveniência com Entity, Activity e Agent e as relações `wasGeneratedBy`, `used`, `wasDerivedFrom` e `wasAttributedTo`.
  - Os *bundles* permitem expressar a proveniência da própria proveniência: quem afirmou o quê e quando.
- Relevância para o Guardião (inferência):
  - A cadeia "log bruto (hash) → exemplo pseudonimizado → dataset v12 → execução → adaptador → Liberação" mapeia diretamente para PROV. As aprovações do responsável viram `wasAttributedTo` sobre Entities identificadas por hash, o que permite consultas de auditoria do tipo "quais adaptadores derivam deste exemplo?".

## 3. Proveniência e licenças de datasets de fine-tuning; dados sintéticos

### [D-8] Longpre, Mahari, Chen, Obeng-Marnu et al. (2024). A large-scale audit of dataset licensing and attribution in AI. Nature Machine Intelligence 6:975–987. DOI 10.1038/s42256-024-00878-8. (Preprint: "The Data Provenance Initiative", arXiv 2310.16787, 2023.)
- Link: https://arxiv.org/abs/2310.16787 · seções lidas em https://arxiv.org/html/2310.16787v3 · metadados do periódico: https://api.openalex.org/works/doi:10.1038/s42256-024-00878-8 · Status: peer-reviewed · Verificado: sim (a página da Nature redirecionou para login; volume e páginas vêm do OpenAlex; os números abaixo são do preprint)
- Contribuição:
  - Audita mais de 1.800 datasets de texto usados em fine-tuning. Nos agregadores, a omissão de licença passa de 70% e o erro de categorização passa de 50%. A licença do autor costuma ser mais restritiva que a declarada no agregador.
  - Mostra que datasets sintéticos se concentram em licenças não comerciais. Trata os termos de uso de provedores de modelos (ex.: OpenAI) como uma restrição de uso, embora registre que isso é disputado para terceiros. Estima que ~12% dos datasets auditados usaram anotações da OpenAI.
  - Lança o Data Provenance Explorer (dataprovenance.org).
- Relevância para o Guardião (inferência):
  - Confirma a prática de registrar licença e revisão **na origem**, sem confiar no rótulo do agregador (Hugging Face).
  - No opensec-triage (CC BY 4.0, gerador não declarado), a licença do dataset não resolve possíveis restrições dos termos de uso do modelo gerador. Esse risco fica sem resolução enquanto o gerador não for conhecido.

### [D-9] Shumailov, Shumaylov, Zhao, Papernot, Anderson, Gal (2024). AI models collapse when trained on recursively generated data. Nature 631:755–759. DOI 10.1038/s41586-024-07566-y.
- Link: https://arxiv.org/abs/2305.17493 · metadados: https://api.openalex.org/works/doi:10.1038/s41586-024-07566-y · Status: peer-reviewed · Verificado: sim (a página da Nature redirecionou para login)
- Contribuição:
  - Descreve o "model collapse": treinar recursivamente com dados gerados por modelos faz desaparecer as caudas (eventos raros) da distribuição original. O efeito aparece em VAEs, GMMs e LLMs.
  - Conclui que dados de interação humana autêntica ganham valor à medida que o conteúdo gerado se espalha.
- Relevância para o Guardião (inferência):
  - Em triagem de SOC, os eventos raros são exatamente os ataques incomuns. Uma fração alta de sintéticos de origem desconhecida pode reduzir a cobertura de cauda. O artigo estuda recursão sem filtro; a extrapolação para uma mistura pequena com dados reais **não** é estabelecida por ele.
  - Justifica relatar a proporção sintético/real por versão do dataset e avaliar separadamente no hold-out real (ver também NIST MS-2.11-005 em D-20).

### [D-10] Arp, Quiring, Pendlebury, Warnecke, Pierazzi, Wressnegger, Cavallaro, Rieck (2022). Dos and Don'ts of Machine Learning in Computer Security. USENIX Security 2022, pp. 3971–3988 (Distinguished Paper).
- Link: https://www.usenix.org/conference/usenixsecurity22/presentation/arp (PDF lido: https://www.usenix.org/system/files/sec22-arp.pdf) · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Identifica dez armadilhas de ML em segurança. Duas ficam na coleta e rotulagem (P1 viés de amostragem, P2 rótulos imprecisos); as outras são P3 *data snooping*, P4 correlações espúrias, P5 parâmetros enviesados, P6 baselines e P7 métricas inadequadas, P8 falácia da taxa-base, P9 avaliação só em laboratório e P10 modelo de ameaça inadequado.
  - Na amostra de 30 artigos de conferências de topo, todos tinham pelo menos três armadilhas. O texto cita dados sintéticos e a combinação de fontes heterogêneas como causas de viés (P1).
- Relevância para o Guardião (inferência):
  - A divisão por grupo de incidente responde a P3, e o uso de FPR no conjunto benigno responde a P8. As aprovações por família com sintéticos tocam P1 e P2 e devem ser declaradas como ameaças à validade.

## 4. Cadeia de suprimento de modelos e ataques

### [D-11] Torres-Arias, Afzali, Kuppusamy, Curtmola, Cappos (2019). in-toto: Providing farm-to-table guarantees for bits and bytes. USENIX Security 2019, pp. 1393–1410. + SLSA v1.2 (OpenSSF/Linux Foundation).
- Link: https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias · SLSA: https://slsa.dev/spec/v1.2/ e https://slsa.dev/spec/v1.2/provenance · Status: peer-reviewed (in-toto); documento técnico (SLSA 1.2, status "Approved") · Verificado: sim
- Contribuição:
  - O in-toto protege criptograficamente toda a cadeia de produção de software. Cada etapa (fonte, build, teste, empacotamento) gera metadados assinados, e o usuário final verifica a cadeia inteira. A avaliação cobre 30 comprometimentos reais.
  - O SLSA 1.2 organiza níveis em trilhas (Build e Source) e recomenda formatos de atestação. A proveniência de build usa o predicado in-toto `https://slsa.dev/provenance/v1`.
- Relevância para o Guardião (inferência):
  - Um *layout* in-toto poderia exigir, para liberar um adaptador, atestações de cada passo: curadoria aprovada, `02_inspect_tokens` com zero truncamentos, treino e avaliação. Cada passo ficaria ligado ao seu "funcionário" (quem executou ou aprovou), e a Liberação passaria a ser verificável por terceiros.

### [D-12] Newman, Meyers, Torres-Arias (2022). Sigstore: Software Signing for Everybody. ACM CCS 2022, pp. 2353–2367. DOI 10.1145/3548606.3560596. + OpenSSF Model Signing (OMS) e biblioteca `model_signing` v1.0 (2025).
- Link: https://par.nsf.gov/biblio/10470793 · OMS: https://github.com/ossf/model-signing-spec · versões: https://pypi.org/project/model-signing/ · Status: peer-reviewed (Sigstore); documento técnico (OMS) · Verificado: sim (a página da ACM retornou 403; o registro NSF-PAR mostra DOI, páginas e local em Los Angeles)
- Contribuição:
  - O Sigstore torna a assinatura de software viável em larga escala. Usa identidade OIDC, chaves efêmeras e logs de transparência para assinaturas e identidades.
  - A especificação OMS assina um modelo como unidade. O manifesto lista o hash (SHA-256 por padrão) de cada arquivo (pesos, configs, tokenizer, eventualmente datasets) dentro de uma declaração in-toto em envelope DSSE, empacotada como *bundle* Sigstore. Também aceita chaves próprias e PKI.
  - A biblioteca `model_signing` teve a v1.0.0 lançada em 2025-04-04; a versão mais recente é a 1.1.1, de 2025-10-10.
- Relevância para o Guardião (inferência):
  - A Liberação "aprovação escrita vinculada a hashes" pode virar uma assinatura OMS do diretório do adaptador, com anotações que apontem para o hash do dataset e da configuração. Com isso, a carga do adaptador pode recusar artefatos não liberados. Chaves locais evitam dependência de serviço externo.

### [D-13] CycloneDX ML-BOM e SPDX 3.0.1 (perfis AI e Dataset). Especificações de lista de materiais para IA.
- Link: https://cyclonedx.org/capabilities/mlbom/ · https://spdx.github.io/spdx-spec/v3.0.1/model/AI/AI/ · Status: documento técnico (especificações) · Verificado: sim (a página do CycloneDX lista "ECMA-424" entre as especificações, mas não explica a relação; não verificado)
- Contribuição:
  - O CycloneDX ML-BOM descreve modelos, datasets e configurações, incluindo proveniência de datasets e riscos de integridade de dados.
  - O SPDX 3.0.1 define `AIPackage`, com propriedades como `informationAboutTraining`, `modelDataPreprocessing`, `safetyRiskAssessment` e `useSensitivePersonalInformation`, e exige licença declarada e licença concluída. O perfil Dataset inclui `anonymizationMethodUsed`, `hasSensitivePersonalInformation`, `confidentialityLevel` e `dataCollectionProcess`.
- Relevância para o Guardião (inferência):
  - A separação SPDX entre licença *declarada* e licença *concluída* corresponde ao achado de D-8 e à prática de registrar a licença verificada na origem.
  - `anonymizationMethodUsed` é o campo onde caberia a regra de pseudonimização (C1…).

### [D-14] Carlini, Jagielski, Choquette-Choo, Paleka, Pearce, Anderson, Terzis, Thomas, Tramèr (2024). Poisoning Web-Scale Training Datasets is Practical. IEEE S&P 2024, pp. 407–425. DOI 10.1109/SP54263.2024.00179. + Wan, Wallace, Shen, Klein (2023). Poisoning Language Models During Instruction Tuning. ICML 2023, PMLR 202:35413–35425.
- Link: https://arxiv.org/abs/2302.10149 · venue: https://www.research-collection.ethz.ch/items/5e3ee588-49e1-452c-8a66-2319bdf36689 · Wan: https://proceedings.mlr.press/v202/wan23b.html · Status: peer-reviewed (ambos) · Verificado: sim
- Contribuição:
  - Carlini et al. apresentam dois ataques. O *split-view poisoning* explora o fato de o conteúdo de uma URL mudar entre a anotação e o download. O *frontrunning* explora snapshots periódicos. Os autores estimam envenenar 0,01% do LAION-400M por US$ 60 e propõem defesas de baixo custo, entre elas a verificação por hash.
  - Wan et al. mostram que cerca de 100 exemplos envenenados num dataset de instruction tuning bastam para associar um gatilho a um comportamento indesejado em centenas de tarefas. Modelos maiores foram mais vulneráveis, e a filtragem só protege moderadamente.
- Relevância para o Guardião (inferência):
  - Fixar revisão e hash de cada fonte neutraliza o *split-view*: o projeto já faz isso.
  - A aprovação por família com amostragem pode deixar passar envenenamento de baixa taxa. O dado relevante é a ordem de grandeza (~100 exemplos) frente a uma meta de 2.000–3.000 exemplos. Isso pesa contra aprovar sintéticos de gerador desconhecido só por regra mais amostra.

### [D-15] Dong, Xue, Chen, Holland, Meng, Li, Liu, Zhu (2025). The Philosopher's Stone: Trojaning Plugins of Large Language Models. NDSS 2025.
- Link: https://www.ndss-symposium.org/ndss-paper/the-philosophers-stone-trojaning-plugins-of-large-language-models/ · Status: peer-reviewed · Verificado: sim (a página não mostra DOI; o ano vem do nome do arquivo do artigo, "2025-s164")
- Contribuição:
  - Mostra que adaptadores de baixo posto (LoRA) podem ser trojanizados. POLISHED usa um LLM superior para "polir" dados envenenados, e FUSION transforma um adaptador benigno em malicioso por *over-poisoning*. O adaptador infectado mantém ou melhora a utilidade aparente.
  - Nenhuma das três defesas avaliadas protegeu por completo.
- Relevância para o Guardião (inferência):
  - Um adaptador é uma unidade da cadeia de suprimento e precisa ser verificado na carga, não só no treino. A Liberação vinculada a hash protege contra substituição, mas não contra um adaptador treinado com dados envenenados. Por isso a governança dos dados (D-14) e a da liberação se complementam.
  - Relevante também para comparar com o modelo rival derivado: só use adaptadores e pesos de terceiros com hash e origem registrados.

## 5. Privacidade de logs e memorização

### [D-16] Carlini, Tramèr, Wallace, Jagielski, Herbert-Voss, Lee, Roberts, Brown, Song, Erlingsson, Oprea, Raffel (2021). Extracting Training Data from Large Language Models. USENIX Security 2021, pp. 2633–2650.
- Link: https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting · Status: peer-reviewed · Verificado: sim
- Contribuição:
  - Demonstra a extração de centenas de sequências literais de treino do GPT-2, incluindo PII (nomes, telefones, e-mails), código e UUIDs de 128 bits, mesmo quando a sequência aparecia em um único documento.
  - Modelos maiores memorizaram mais.
- Relevância para o Guardião (inferência):
  - IoCs, hostnames, usuários e GUIDs de logs reais são justamente o tipo de cadeia de alta entropia que pode ser memorizada. A pseudonimização *antes* do treino reduz o dano, e um teste de extração ou de *canaries* no adaptador liberado mediria o resíduo.
  - A métrica de "IoC Hallucination" verifica o oposto (IoC inventado). Seria útil um teste espelho de "IoC memorizado de outro exemplo".

### [D-17] Coull, Wright, Monrose, Collins, Reiter (2007). Playing Devil's Advocate: Inferring Sensitive Information from Anonymized Network Traces. NDSS 2007.
- Link: https://www.ndss-symposium.org/?p=2598 (PDF lido: https://www.ndss-symposium.org/wp-content/uploads/2017/09/Playing-Devils-Advocate-Inferring-Sensitive-Information-from-Anonymized-Network-Traces-Scott-E.-Coull.pdf) · Status: peer-reviewed · Verificado: sim
- Trabalhos relacionados verificados: Slagell, Lakkaraju, Luo (2006), *FLAIM: A Multi-level Anonymization Framework for Computer and Network Logs*, USENIX LISA '06 (peer-reviewed), https://www.usenix.org/conference/lisa-06/flaim-multi-level-anonymization-framework-computer-and-network-logs. Bargale et al. (2025), anonimização de logs com hash salgado por octeto e ruído temporal, arXiv 2507.21904 (preprint), https://arxiv.org/abs/2507.21904. Kapelinski, Lautert, Machado, Kreutz, Ferrão (2026), *AnonShield*, pseudonimização on-premise para dados de CSIRT, arXiv 2606.15650 (preprint submetido ao SBRC 2026), https://arxiv.org/abs/2606.15650.
- Contribuição:
  - Mostra que traces de rede anonimizados (com IPs ofuscados) permitem inferir a topologia e desanonimizar servidores usando só os próprios dados e informação pública. Os vazamentos vêm de padrões que são justamente o que torna os dados úteis.
  - O FLAIM propõe anonimização multinível de logs, com troca explícita entre perda de informação e privacidade. Os preprints de 2025–2026 mostram que o tema continua ativo e que o hash sem sal é considerado fraco.
- Relevância para o Guardião (inferência):
  - A pseudonimização consistente (cliente = C1; mesmo IP → mesmo token) preserva correlações úteis para triagem, mas, pelo argumento de Coull et al., também preserva padrões reidentificáveis. Os recortes publicados devem ser tratados como pseudonimizados, não como anônimos (ver D-18).

### [D-18] Brasil (2018). Lei nº 13.709/2018 — Lei Geral de Proteção de Dados Pessoais (LGPD). + ANPD (2023). Estudo técnico sobre anonimização de dados na LGPD: uma visão de processo baseado em risco e técnicas computacionais, v1.0, nov. 2023. + ANPD (2023). Guia orientativo: Tratamento de dados pessoais para fins acadêmicos e para a realização de estudos e pesquisas, v1.0, jun. 2023.
- Link: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm · estudo técnico: https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos/estudo_tecnico_sobre_anonimizacao_de_dados_na_lgpd_uma_visao_de_processo_baseado_em_risco_e_tecnicas_computacionais.pdf/@@display-file/file · guia acadêmico: https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/web-guia-anpd-tratamento-de-dados-para-fins-academicos.pdf/@@display-file/file · consulta do guia de anonimização: https://www.gov.br/anpd/pt-br/assuntos/noticias/anpd-abre-consulta-a-sociedade-sobre-o-guia-de-anonimizacao-e-pseudonimizacao · Status: norma/lei (LGPD); documentos técnicos e orientativos (ANPD) · Verificado: sim
- Contribuição:
  - A LGPD define dado pessoal como informação sobre pessoa natural "identificada ou identificável" (art. 5º, I). Dado anonimizado não é dado pessoal, salvo se o processo puder ser revertido por meios razoáveis, que consideram custo, tempo e tecnologia disponível (art. 12 e § 1º). O art. 13, § 4º define pseudonimização como perda da associação a um indivíduo, salvo por informação adicional mantida separadamente pelo controlador em ambiente controlado e seguro. O art. 7º, IV admite estudos por órgão de pesquisa, com anonimização garantida sempre que possível. O art. 37 exige registro das operações de tratamento e o art. 46 exige medidas de segurança.
  - O estudo técnico da ANPD (v1.0, nov. 2023) trata a anonimização como **processo contínuo baseado em risco**, com documentação da trilha de estados do dataset (seção 2.2) e gestão do risco de reidentificação. Diz que as técnicas estão sempre sujeitas a ataques bem-sucedidos.
  - Status do guia: a ANPD pôs em consulta uma minuta de Guia de Anonimização e Pseudonimização (30/01 a 28/02/2024). Em 2026-11-25, a página de materiais e publicações da ANPD não listava versão final desse guia. O guia de fins acadêmicos (v1.0, jun. 2023) está publicado e trata da hipótese de "órgão de pesquisa".
- Relevância para o Guardião (inferência):
  - A LGPD não menciona IPs nem nomes de usuário. Pelo critério "identificável" e pelos meios razoáveis do art. 12, IPs e usernames em logs tendem a ser dados pessoais quando há meio razoável de vínculo. A tabela de correspondência C1↔cliente real é a "informação adicional" do art. 13, § 4º e deve ficar separada e fora do Git.
  - A trilha documental que a ANPD recomenda (seção 2.2) coincide com o registro de versões e hashes do projeto. Falta registrar a avaliação de risco de reidentificação de cada recorte publicado.

## 6. Marcos normativos

### [D-19] União Europeia (2024). Regulamento (UE) 2024/1689 — AI Act. JO L, 12.7.2024. + Regulamento (UE) 2026/1744 ("Digital Omnibus on AI"), de 8 jul. 2026.
- Link: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689 · omnibus: https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng · Status: norma/lei · Verificado: sim (texto lido no navegador; o WebFetch recebeu página vazia)
- Contribuição:
  - **Art. 10 (dados e governança de dados), para sistemas de alto risco:** as práticas de governança devem cobrir escolhas de design, processos de coleta e **origem** dos dados, operações de preparação (anotação, rotulagem, limpeza, atualização, enriquecimento, agregação), pressupostos, exame e mitigação de vieses e identificação de lacunas (n.º 2). Os dados devem ser relevantes, suficientemente representativos e, "na medida do possível", livres de erros e completos (n.º 3).
  - **Art. 12:** o sistema de alto risco deve permitir tecnicamente o registro **automático de eventos (logs) durante toda a vida útil**, para rastreabilidade, monitoramento pós-comercialização e monitoramento da operação. **Art. 19:** os logs sob controle do provedor devem ser guardados por no mínimo seis meses. **Art. 13:** as instruções de uso devem incluir informação sobre os dados de treino, validação e teste (n.º 3, b, vi) e sobre os mecanismos de coleta de logs (n.º 3, f). **Art. 14:** a supervisão humana deve permitir entender limitações, estar atento ao **viés de automação**, desconsiderar ou reverter a saída e interromper o sistema (n.º 4, a–e). **Art. 15(5):** exige, quando apropriado, medidas contra *data poisoning* e *model poisoning* de componentes pré-treinados.
  - **Datas:** pelo Omnibus (art. 113 alterado), as seções 1–3 do Capítulo III valem a partir de **2 dez. 2027** para os sistemas do Anexo III e de **2 ago. 2028** para os do Anexo I. O antigo art. 10(5), sobre dados sensíveis para correção de viés, passou para o novo art. 4a. A lista de alterações do Omnibus não inclui os arts. 12, 13 e 14.
- Relevância para o Guardião (inferência):
  - O texto não diz se um assistente de triagem de SOC é de "alto risco". O Anexo III, ponto 2, menciona componentes de segurança na gestão de infraestrutura digital crítica, e a classificação dependeria do uso concreto. Para o artigo, o AI Act serve como **referência de boas práticas**, não como obrigação demonstrada.
  - O Art. 12 trata de logs **de operação** (inferência em uso), não de registros de treino. A Liberação por hashes cobre a proveniência de treino, mas não substitui um log por inferência (hash da entrada, hash do adaptador, saída, decisão humana).

### [D-20] NIST (2023). Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1, 26 jan. 2023. DOI 10.6028/NIST.AI.100-1. + NIST (2024). AI RMF: Generative AI Profile, NIST AI 600-1, 26 jul. 2024. DOI 10.6028/NIST.AI.600-1.
- Link: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10 · https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence (PDFs lidos em nvlpubs.nist.gov) · Status: documento técnico (voluntário) · Verificado: sim
- Contribuição:
  - O AI RMF organiza o núcleo em quatro funções (GOVERN, MAP, MEASURE, MANAGE) e sete características de confiabilidade, entre elas "Accountable and Transparent", "Secure and Resilient" e "Privacy-Enhanced". Afirma que manter a proveniência dos dados de treino ajuda a transparência e a accountability. Pede processos documentados de supervisão humana (MAP 3.5) e mapeamento de riscos de componentes de terceiros, incluindo dados (MAP 4.1).
  - O perfil 600-1 lista 12 riscos de IA generativa, entre eles Data Privacy, Information Security, Harmful Bias/Homogenization e "Value Chain and Component Integration" (integração não rastreável de componentes de terceiros). Ações sugeridas: inventário com proveniência dos dados (fonte, assinaturas, versionamento) (GV-1.6-003); verificar a proveniência dos dados de treino e TEVV (MS-2.5-005); deduplicar sintéticos (MS-2.10-003); medir a proporção sintético/não sintético por risco de colapso (MS-2.11-005); reavaliar o risco após fine-tuning e testar *data poisoning* na cadeia de valor (MG-3.1-001 a 003).
- Relevância para o Guardião (inferência):
  - A combinação de hashes de origem, revisões, diretórios por execução e Liberação atende de forma direta a GV-1.6-003 e MS-2.5-005. A aprovação por família de sintéticos sem gerador conhecido é o ponto em que MS-2.5-005 e MS-2.11-005 ficam só parcialmente atendidos.

### [D-21] ISO/IEC (2023). ISO/IEC 42001:2023 — Information technology — Artificial intelligence — Management system. Ed. 1, dez. 2023, ISO/IEC JTC 1/SC 42.
- Link: https://www.iso.org/standard/42001 · Status: norma (publicada, estágio 60.60, 51 p.) · Verificado: sim, só a página de catálogo. O conteúdo normativo (cláusulas e Anexo A) está **NÃO VERIFICADO**: a prévia no OBP exige aceitar termos de uso, e não foram aceitos.
- Contribuição:
  - Especifica requisitos para estabelecer, implementar, manter e melhorar continuamente um Sistema de Gestão de IA (AIMS) em organizações que desenvolvem, fornecem ou usam IA. A página de catálogo cita rastreabilidade, transparência e confiabilidade entre os benefícios.
  - Pode ser certificada e é comercializada em pacote com a ISO/IEC 27001 e a ISO/IEC 42005:2025 (avaliação de impacto).
- Relevância para o Guardião (inferência):
  - Para um laboratório individual, um AIMS certificável é desproporcional. A lógica de ciclo de melhoria contínua com evidências documentadas é, ainda assim, compatível com o fluxo de versões e Liberações. Qualquer afirmação sobre controles específicos do Anexo A exige ler a norma.

### [D-22] Brasil — Senado Federal / Câmara dos Deputados. PL 2338/2023 (dispõe sobre o desenvolvimento, o fomento e o uso ético e responsável da inteligência artificial).
- Link: https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao=2487262 · Senado: https://www25.senado.leg.br/web/atividade/materias/-/materia/157233 · Status: projeto de lei (não é lei) · Verificado: sim (status); o conteúdo do texto **não foi analisado** nesta revisão
- Contribuição:
  - Senado: tramitação encerrada com aprovação pelo Plenário (documentos de plenário de 10/12/2024) e remetida à Câmara em 17/03/2025 (Ofício SF nº 235).
  - Câmara, situação exibida em 2026-11-25: **"Aguardando Parecer do(a) Relator(a) na Comissão Especial sobre Inteligência Artificial (PL 2338/23)"**, em regime de prioridade (art. 151, II, RICD), sujeita à apreciação do Plenário. As últimas ações (nov. 2026) são apensações de outros PLs.
- Relevância para o Guardião (inferência):
  - Não há marco legal de IA em vigor no Brasil. Para o eixo de governança do artigo, a LGPD (D-18) é o instrumento brasileiro aplicável hoje. O PL deve ser citado só com o status exato acima e a data da consulta.

---

## Lacunas observadas

- **Governança de datasets de logs de segurança para treinar LLMs.** Nesta busca delimitada, não encontrei trabalho revisado por pares que aplique datasheets ou data cards, proveniência (PROV/in-toto) ou assinatura de modelos especificamente a **datasets de logs de SOC usados em fine-tuning de LLMs**. O que existe se divide em três grupos:
  - Qualidade e manutenção de datasets de intrusão para avaliar IDS. Metadados conferidos no OpenAlex, sem leitura do texto completo: Landauer et al., *Maintainable Log Datasets for Evaluation of Intrusion Detection Systems*, IEEE TDSC 20(4), DOI 10.1109/tdsc.2022.3201582 (origem do AIT-LDS); Kenyon, Deka, Elizondo, *Are public intrusion datasets fit for purpose*, Computers & Security 99 (2020), DOI 10.1016/j.cose.2020.102022; Engelen, Rimmer, Joosen, *Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study*, IEEE SPW 2021, DOI 10.1109/spw53761.2021.00009. Fonte: https://api.openalex.org/works?search=Are%20public%20intrusion%20datasets%20fit%20for%20purpose e https://api.openalex.org/works?search=Troubleshooting%20an%20intrusion%20detection%20dataset%20CICIDS2017.
  - Armadilhas metodológicas (D-10).
  - Trabalhos recentes de LLM para SOC que usam "auditável" no sentido de **explicação do raciocínio**, não de proveniência de dados. Exemplo próximo do projeto: AIDR, especialistas LoRA que emitem JSON pronto para SOAR (Zhao et al., arXiv 2512.08169, preprint, https://arxiv.org/abs/2512.08169). O survey de Ndichu et al. (arXiv 2605.08316, submetido à ACM CSUR, https://arxiv.org/abs/2605.08316) aponta lacunas em validação operacional e prática de avaliação; proveniência e licenças não aparecem no resumo.
- **Aprovação por família vs. por linha.** Não encontrei literatura que quantifique o risco de aprovar subconjuntos de dados de treino por regra e amostra, nem que relacione o tamanho da amostra ao limite de detecção de exemplos envenenados (cf. ~100 exemplos em D-14). Esta é uma inferência a partir de uma busca não exaustiva.
- **Dados sintéticos de gerador desconhecido.** D-4 (Croissant RAI) e D-20 (NIST) pedem o método de geração. D-8 mostra que termos de uso do gerador podem restringir o uso. Não há prática estabelecida para *aceitar* datasets sintéticos cujo card omite o gerador.
- **Liberação humana como atestação.** As especificações D-11 e D-12 assinam artefatos e passos de build, mas não definem um predicado padrão para "aprovação humana de liberação de modelo, vinculada aos hashes de dados e configuração".
- **O que o projeto poderia contribuir** (proposta, não resultado):
  1. Um perfil de datasheet ou Croissant-RAI para datasets de logs de segurança, com campos para hash e revisão por fonte, regra de pseudonimização, verificação literal de IoCs, regime de aprovação (linha ou família, com tamanho de amostra) e divisão por grupo de incidente.
  2. Uma cadeia de proveniência verificável (PROV + in-toto/OMS) do log bruto até a Liberação.
  3. Medidas empíricas: (a) taxa de erro detectada em auditoria linha a linha de uma amostra das famílias aprovadas por regra; (b) testes de memorização ou *canaries* de identificadores pseudonimizados no adaptador; (c) efeito da fração sintética no FPR e no Macro-F1 do hold-out real.
  4. A perspectiva da LGPD e da ANPD, rara na literatura internacional de ML para segurança.

## Controvérsias

- **Anonimização vs. utilidade em logs.** Esquemas que preservam estrutura (prefixo de IP, hash por octeto, pseudônimos consistentes) mantêm correlações úteis para triagem. Coull et al. (D-17) mostram que essas mesmas regularidades permitem desanonimizar. A ANPD (D-18) trata a anonimização como processo de risco contínuo, não como estado definitivo. Não há consenso sobre o nível "suficiente" para publicar recortes.
- **Documentação autodeclarada vs. verificação.** Datasheets, model cards e data cards (D-1 a D-3) são preenchidos por quem produz o artefato. Raji et al. (D-5) propõem auditoria interna estruturada, mas a independência do auditor continua em aberto. No projeto, curador e liberador coincidem.
- **Alcance do model collapse.** D-9 estuda treino recursivo com dados gerados. Não verifiquei nesta sessão trabalhos que contestem ou delimitem o efeito quando os sintéticos são misturados com dados reais. Por isso, usar D-9 para condenar uma pequena fração sintética seria extrapolação.
- **Licença de dados gerados por modelo.** D-8 registra que é disputado se os termos de uso do provedor alcançam terceiros que não geraram os dados. Uma licença CC BY 4.0 no dataset não resolve a questão.
- **Escala e vulnerabilidade.** D-14 (Wan) e D-16 encontram mais vulnerabilidade ou memorização em modelos maiores. O plano de escalar para 7B–8B pode aumentar esses riscos. Isso é uma inferência, não um resultado medido no projeto.
- **Aplicabilidade e calendário do AI Act.** A classificação de um assistente de triagem como alto risco não decorre diretamente do texto, e as datas mudaram com o Regulamento 2026/1744. Citações de prazos precisam indicar a versão consolidada.

## O que confirma ou desafia as práticas do projeto

**Confirma**
- *Hashes de origem, revisões e licenças registradas na fonte.* Estão alinhados com AI Act Art. 10(2)(b)–(c) (origem e operações de preparação), NIST GV-1.6-003 e MS-2.5-005, PROV (D-7) e a defesa contra *split-view poisoning* (D-14). D-8 mostra que confiar no agregador seria insuficiente.
- *Diretórios por execução com configuração efetiva, revisões e versões da stack.* Atendem ao núcleo do checklist de reprodutibilidade (D-6) e à trilha documental recomendada pela ANPD (D-18, seção 2.2).
- *Divisão por grupo de incidente e hold-out isolado.* Respondem ao *data snooping* (D-10, P3).
- *Pseudonimização (C1…).* Está coerente com LGPD art. 7º, IV (anonimização "sempre que possível" em pesquisa), com a definição do art. 13, § 4º e com o risco de memorização (D-16).
- *"O modelo só relata; contenção exige aprovação humana".* Corresponde a AI Act Art. 14(4)(d)–(e) (desconsiderar ou reverter a saída, interromper) e a NIST MAP 3.5.

**Desafia ou fica aquém**
- *AI Act Art. 12 e Art. 19.* A Liberação documenta o **treino**. O Art. 12 pede registro automático de eventos durante toda a **operação**, e o Art. 19 fixa guarda mínima de seis meses (se o sistema for de alto risco). Para se aproximar disso, cada inferência registraria hash da entrada, hash do adaptador liberado, saída JSON, validação Pydantic e a decisão humana sobre contenção. O Art. 14(4)(b) acrescenta o viés de automação, que exige medidas de interface ou treinamento além da aprovação.
- *Aprovação escrita vs. verificável.* Uma aprovação escrita vinculada a hashes é uma atestação. Sem assinatura criptográfica (OMS/Sigstore, D-12) nem layout de etapas (in-toto, D-11), um terceiro não consegue verificar que o adaptador carregado é o liberado nem que as etapas exigidas (inspeção de tokens, avaliação) ocorreram. D-15 mostra por que verificar na carga importa.
- *Aprovação por família de sintéticos sem gerador declarado.* Fica aquém de AI Act Art. 10(2)(c) e 10(3), que pedem documentar a rotulagem e buscar dados livres de erros, de NIST MS-2.5-005 e MS-2.11-005 e do campo de sintéticos do Croissant RAI. D-14 sugere que a amostragem pode não detectar envenenamento de baixa taxa. No mínimo, seria preciso registrar regra, tamanho e resultado da amostra, a fração sintética por versão e avaliações estratificadas (real vs. sintético).
- *Pseudonimização ≠ anonimização.* Pela LGPD (art. 12 e art. 13, § 4º) e por D-17, recortes pseudonimizados continuam potencialmente pessoais. A tabela de correspondência precisa de controle de acesso próprio. Falta uma avaliação documentada do risco de reidentificação antes de qualquer publicação.
- *Separação de funções.* O mesmo responsável cura, aprova e libera. D-5 e o espírito do Art. 14(5) do AI Act (dupla verificação humana, exigida só para biometria) apontam para revisão independente ao menos por amostragem. Hoje isso é uma limitação a declarar no artigo, não necessariamente um defeito.
- *Inventário da cadeia de suprimento.* Pesos base (Gemma) e rival derivado têm licenças próprias. NIST GV-1.6-003 e MAP 4.1 pedem inventariar versões, modos de acesso e riscos de componentes de terceiros. Uma ML-BOM (D-13) com licença declarada e licença concluída para pesos, datasets e adaptadores formalizaria o que hoje está nos diretórios de execução.
