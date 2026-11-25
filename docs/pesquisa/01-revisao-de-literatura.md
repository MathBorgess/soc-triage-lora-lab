# Revisão de literatura: treino, integração e governança de modelos de triagem de SOC

> Rascunho de pesquisa, 25/11/2026. Serve de base para o desenho do Guardião e para um futuro
> artigo sobre cibersegurança, detecção de intrusão e governança e auditabilidade de dados.

Esta revisão responde três perguntas:

1. Como treinar e avaliar modelos que detectam anomalias e intrusões em logs, incluindo LLMs
   com fine-tuning eficiente?
2. Como integrar esses modelos na operação de um SOC sem criar falsos positivos, perda de
   ataques ou uma nova superfície de ataque?
3. Que práticas de governança, proveniência e auditoria se aplicam aos dados e aos modelos?

O texto traz a síntese, o mapa das decisões do projeto contra a evidência, as lacunas que o
artigo pode ocupar e o impacto na rodada 4 do desenho do Guardião. As fichas completas de cada
trabalho, com link, status e relevância, estão em quatro notas:

- [A — Logs e LLMs](notas/A-logs-e-llms.md): detecção de anomalias em logs e LLMs para análise de logs.
- [B — IDS, avaliação e PEFT](notas/B-ids-avaliacao-e-peft.md): armadilhas de ML em segurança e fine-tuning eficiente.
- [C — Integração no SOC e injeção](notas/C-integracao-soc-e-injecao.md): operação de SOC, drift e injeção de prompt.
- [D — Governança e auditabilidade](notas/D-governanca-e-auditabilidade.md): documentação, proveniência, cadeia de suprimento, privacidade e normas.

Os identificadores entre colchetes, como [A-3], apontam para essas fichas.

## Método e limites

- Quatro buscas paralelas, uma por tema, com busca na web e leitura da página do próprio
  trabalho: arXiv, anais da USENIX, NDSS, PMLR, ACL Anthology, EUR-Lex, NIST, planalto.gov.br,
  gov.br/anpd e Câmara. Cada ficha só entrou com uma URL aberta na sessão. Venue e ano vêm
  dessa página.
- Conferência posterior: 25 identificadores arXiv citados nas fichas, a maioria de 2024 a 2026,
  foram consultados na API do arXiv, e todos existem com o título informado. Também foram abertas as
  páginas da USENIX Security 2026 (Karanjai; Nasr), do MITRE ATT&CK (T1698 e T1685.007), do
  PMLR (ExCyTIn-Bench), do NDSS (Philosopher's Stone) e do EUR-Lex (Regulamento 2026/1744).
  A conferência checou existência, título e venue. Ela não releu os números dentro de cada
  artigo; esses números vêm da leitura feita na busca e trazem a seção ou tabela de origem
  na ficha.
- ACM DL e IEEE Xplore bloquearam o acesso. Nesses casos, o venue saiu da cópia do autor, de
  repositório institucional, do campo *comments* do arXiv ou do OpenAlex, e a ficha diz qual.
- Não verificados: a versão em periódico de Karlsen et al. (JNSM 2024), o conteúdo normativo
  da ISO/IEC 42001 (só a página de catálogo foi lida) e o texto do PL 2338/2023 (só a
  tramitação). SecEval, SECURE, CyberSecEval original, DivLog, RAGLog, LogGPT e Loghub 2.0
  ficaram fora das fichas por não terem sido abertos.
- **Tipo de revisão:** é uma revisão narrativa e delimitada, não uma revisão sistemática. Se o
  artigo apresentar a revisão como contribuição, será preciso um protocolo com strings de
  busca, bases, critérios de inclusão e fluxo PRISMA.
- Muitos trabalhos de 2025–2026 são preprints. Eles aparecem marcados assim e não sustentam
  sozinhos nenhuma afirmação central.

São 86 fichas, cerca de 75 trabalhos distintos: a mesma obra pode aparecer em mais de um tema,
como Arp et al. em A-9, B-2, C-12 e D-10.

## Síntese em seis achados

### 1. Resultados quase perfeitos em segurança costumam ser artefato da avaliação

Os dez *pitfalls* de Arp et al. (USENIX Security 2022) aparecem em todos os 30 artigos de
topo analisados, cada um com pelo menos três [A-9]. Entre eles estão viés de amostragem,
*data snooping*, correlações espúrias, baselines inadequados, falácia da taxa-base e avaliação
só em laboratório. Outros estudos mostram o mesmo efeito em números:

- Trocar o split aleatório pelo cronológico derruba o F1 do DeepLog no BGL de 0,927 para
  0,426 [A-3]. O tipo e o tamanho da janela também mudam o resultado.
- Detectores triviais, como "tipo de evento nunca visto", chegam a F1 de 96–99% em HDFS e BGL
  [A-5]. KNN supera deep learning em logs públicos [A-8].
- Mais de 20% dos traces do CICIDS2017 precisaram ser reconstruídos ou rerrotulados [B-4].
  Sete datasets de NIDS têm seis "smells", entre eles diversidade artificial e rótulo vazando
  por features [B-5]. Tráfego sintético difere do real na maioria das features [B-6].
- Um RoBERTa com LoRA empata com XGBoost no mesmo dataset, mas chega a FPR de 0,78 em outra
  rede [B-8]. Esse resultado vem de preprint.
- Classificadores com F1 de 0,99 caem quando se removem o viés espacial e o temporal [B-3].

**Leitura para o projeto:** isso sustenta medir a superioridade sobre o Rival só no Teste
real. Também mostra o que ainda falta no protocolo: baselines simples, hold-out temporal ou por
fonte, intervalos de confiança e FPR projetado para uma taxa-base realista.

### 2. No fine-tuning eficiente, os alvos importam e o resto é disputado

- LoRA em todas as camadas lineares supera LoRA só na atenção. QLoRA e "LoRA Learns Less"
  concordam nisso [B-10, B-13].
- O efeito do rank é controverso. O QLoRA não acha relação com o desempenho final quando todas
  as camadas são adaptadas [B-10]. "LoRA Learns Less" acha desempenho ordenado pelo rank e
  mostra que o melhor learning rate muda com o rank [B-13].
- A paridade entre 4-bit e 16-bit do QLoRA foi mostrada com NF4. O 4-bit do MLX usa outro
  esquema, então a paridade não é garantida (inferência sobre a stack).
- Pôr loss também no prompt ajudou justamente quando a entrada é longa, a saída é curta e há
  poucos exemplos [B-14]. O melhor peso de loss no prompt fica entre 0 e 1 em completions
  curtas [B-15]. É o regime deste projeto.
- DoRA e PiSSA têm ganhos pequenos em benchmarks gerais [B-11, B-12]. Com uma única seed, a
  matriz não separa efeitos desse tamanho de ruído.
- Fine-tuning pode aumentar a acurácia e piorar a calibração [B-21]. Cadeia de raciocínio
  degrada as probabilidades do rótulo [B-18].

### 3. LLMs para logs existem; triagem de segurança multi-fonte quase não

A literatura de LLM para logs gira em torno de parsing e anomalia em datasets de
confiabilidade, como HDFS, BGL e Thunderbird [A-7, A-10 a A-14]. Os trabalhos mais próximos do
Guardião são recentes e quase todos preprints:

- **AIDR:** especialistas LoRA locais emitem JSON pronto para SOAR, com raciocínio comprimido
  [A-17].
- **ALERT-BENCH:** todas as estratégias de agente perdem pelo menos 40,4% dos ataques. Buscas
  sem resultado levam ao descarte do alerta, e a auto-revisão no mesmo contexto piora o
  resultado. Exigir evidência mais forte para descartar derruba a taxa de falso negativo para
  3,1% [A-18].
- A validade de saída estruturada varia muito por modelo [A-16].
- JSON estrito não custa acurácia em classificação, mas pode custar em raciocínio. A ordem dos
  campos muda o resultado [A-19], este revisado por pares.
- **Saju e Azim (2026):** framework de ponta a ponta com dados de produção (detecção, consultas
  ao SIEM e códigos de fechamento). Usa LLMs sem fine-tuning e não trata injeção nem
  fidelidade literal. A leitura integral achou inconsistências nas tabelas. Ver a
  [revisão integral](02-revisao-saju-azim-2026.md).

### 4. Injeção de prompt em logs é uma ameaça documentada e a defesa tem de ser arquitetural

- Injeção passiva em campos de log contra LLMs de produção chegou a 88,2% de sucesso.
  Fragmentar o payload entre linhas (*Context Stitching*) deu 76,4%. A defesa em camadas deixou
  8,4% residual [C-18, USENIX Security 2026].
- Injeções no User-Agent ou na linha de comando fizeram ataques reais serem lidos como normais
  em 67–87% dos casos [A-20, preprint].
- Desde setembro de 2026, o MITRE ATT&CK tem as técnicas T1698 (*Indirect Prompt Injection*) e
  T1685.007 (*Impair Autonomous Defenses*). A segunda descreve o atacante fazendo uma defesa com
  IA deixar de alertar [C-19].
- Nenhum modelo avaliado separa bem instrução de dados, e o fine-tuning não resolve isso
  [C-15, ICLR 2025].
- StruQ e SecAlign reduzem ataques estáticos [C-16]. Ataques adaptativos quebram 12 defesas,
  a maioria com mais de 90% de sucesso [C-17, USENIX Security 2026]. Ataques *white-box* chegam
  a 85–95% contra StruQ e SecAlign. Os pesos do Gemma são públicos, então esse cenário é
  realista.
- CaMeL e os *design patterns* de agentes chegam à mesma conclusão: a segurança vem de limitar
  o que a saída do modelo pode causar, não de tornar o modelo imune [C-20, C-21].

### 5. No SOC, o analista mantém a decisão e o falso positivo dominante é o benign trigger

- Analistas relatam que a maioria dos falsos positivos são *benign triggers*: alarmes
  tecnicamente corretos disparados por atividade legítima [C-1]. É o que o projeto chama de
  `expected_admin`.
- Analistas desconfiam de automação por causa de falsos positivos [C-2]. Usam o LLM para
  entender e redigir, não para decisões de alto risco [C-6]. A falta de um modelo mental de
  como o score é gerado leva a desconfiança ou mau uso [C-4, n = 6].
- Reaproveitar a saída do modelo no relatório mede adoção, não acerto [C-6].
- Drift exige rejeição ou abstenção calibrada fora do modelo [C-9 a C-11]. Não há método
  estabelecido para saída estruturada de LLM.

### 6. Governança: documentar, provar a origem, assinar e registrar a operação

- **Documentação:** Datasheets, Model Cards, Data Cards e Croissant RAI [D-1 a D-4]. O Croissant
  RAI pede o método de geração de dados sintéticos e ainda não define propriedades de
  rastreabilidade.
- **Proveniência e cadeia de suprimento:** W3C PROV [D-7], in-toto e SLSA [D-11], Sigstore e
  OpenSSF Model Signing [D-12], e ML-BOM em CycloneDX e SPDX 3.0 [D-13].
- **Licenças:** nos agregadores, a licença falta em mais de 70% dos datasets de fine-tuning e
  está errada em mais de 50%. Os termos de uso do modelo gerador podem restringir dados
  sintéticos [D-8].
- **Ataques à cadeia:** cerca de 100 exemplos envenenados bastam para implantar um gatilho em
  instruction tuning [D-14]. Adaptadores LoRA podem ser trojanizados mantendo a utilidade
  aparente [D-15].
- **Privacidade:** LLMs memorizam cadeias de alta entropia vistas uma única vez [D-16]. Traces
  pseudonimizados permitem inferir topologia e desanonimizar [D-17]. Pela LGPD, dado
  pseudonimizado continua dado pessoal enquanto houver meio razoável de reversão (arts. 12 e
  13, § 4º). O guia de anonimização da ANPD ainda não tem versão final [D-18].
- **Normas:**
  - AI Act: arts. 10 (governança de dados), 12 e 19 (logs de operação, guardados por pelo
    menos seis meses), 14 (supervisão humana e viés de automação) e 15(5) (envenenamento). O
    Regulamento (UE) 2026/1744 adiou as obrigações do Anexo III para 2/12/2027 [D-19].
  - NIST AI RMF e perfil generativo 600-1 [D-20], com ações para proveniência (GV-1.6-003,
    MS-2.5-005) e para medir a fração sintética (MS-2.11-005).
  - ISO/IEC 42001 [D-21], só a página de catálogo.
  - PL 2338/2023, que aguarda parecer na Comissão Especial da Câmara [D-22].

## Decisões do projeto contra a evidência

| Decisão | O que a literatura diz | Encaminhamento |
| --- | --- | --- |
| Superioridade sobre o Rival medida só no Teste real | Confirma: avaliação só em laboratório e em dados sintéticos infla resultados [A-9, B-5, B-6, B-8] | Manter |
| Split por grupo de incidente ou cenário | Confirma contra vazamento entre grupos [A-3, A-9], mas não trata viés temporal nem de fonte [B-3, C-9] | Acrescentar hold-out temporal ou por fonte onde houver datas |
| Run 0 zero-shot como único baseline | Insuficiente: baselines triviais e lineares empatam em logs [A-5, A-8]; prompting melhorado rende muito [A-12] | Acrescentar TF-IDF + LR, regras por Modalidade, few-shot e um encoder pequeno |
| FPR em `benign` e `expected_admin` | Confirma [A-5, C-1]; a taxa-base de teste não é a da operação [A-9, P8] | Reportar FPR por classe e projetar alertas falsos por dia sob uma prevalência declarada |
| `mask_prompt: true` em todas as rodadas | Desafiado: loss no prompt ajudou no regime do projeto [B-14, B-15] | Priorizar o controle pareado `mask_prompt: false` e medir IoC alucinado nas duas condições |
| Seed 42 única | Reprodutível, mas não separa efeitos pequenos de ruído [A-5, B-11, B-12] | Bootstrap por grupo no teste (compatível com seed fixa); seeds extras são decisão do responsável |
| Run 3 contra Run 2 como efeito da quantização | A paridade do QLoRA vale para NF4 [B-10] | Declarar que o 4-bit do MLX é outro esquema |
| Run 4 com learning rate fixo | O LR ótimo muda com o rank [B-13] | Ajustar LR por rank no valid ou declarar o confundimento |
| all-linear como referência | Confirma [B-10, B-13] | Manter |
| JSON estrito com Evidência e rationale antes do veredito | Confirma: JSON ajuda classificação e a ordem dos campos importa [A-19] | Manter; separar métricas por campo |
| Checagem literal de IoC e Evidência | Nenhum trabalho mede isso; é uma contribuição possível [A, lacuna 2] | Manter e destacar no artigo |
| Contexto confiável separado de Registro não confiável | Necessário e não suficiente [C-15, C-17, C-18] | O Runtime só aceita rebaixamento se a Evidência dele estiver literalmente no Contexto; senão mantém o veredito mais severo (fail-closed). O Projetor escapa delimitadores reservados no Registro, como no StruQ [C-16]. O rationale nunca dispara regra |
| Gate "zero alertas rebaixados" na Suíte adversarial | Suíte estática dá falsa confiança [C-17] | Usar a suíte estática como regressão. Reportar a taxa de sucesso com intervalo de confiança (zero em n casos só limita a cerca de 3/n). Incluir ataques adaptativos, Context Stitching e injeções que inflam alertas |
| Guardião só relata; contenção por regra com aprovação humana | Confirma [C-20, C-21, D-19 art. 14] e corresponde à mitigação M1038 da T1685.007 [C-19] | Manter |
| Recorte de uma Modalidade sem contexto externo | Ausência de evidência leva a descartar ataques [A-18, C-8]; baixa visibilidade é a queixa nº 1 dos SOCs [C-2] | Proibir rebaixamento por falta de dados; avaliar à parte os Recortes truncados |
| opensec com teto 1:1 e aprovação por Família | Desafiado: viés de sintéticos [A-9, B-5, B-6], subjetividade das classes de FPR [B-22], envenenamento com cerca de 100 exemplos [D-14], gerador desconhecido [D-8, D-20], viés de família do gerador [B-20] | Ablação da proporção (0; 0,25; 0,5; 1) medida só no valid real; classificador real contra sintético como diagnóstico; registrar regra, tamanho e resultado da amostra por Família |
| Liberação = aprovação escrita + hashes | Cobre a proveniência do treino [D-20]. Fica aquém em verificação por terceiros [D-11, D-12], logs de operação [D-19 arts. 12 e 19] e separação de funções [D-5] | Assinar o adaptador (OpenSSF Model Signing com chave local) e verificar na carga; registrar cada inferência; declarar que curador e liberador são a mesma pessoa |
| Pseudonimização (`cliente=C1`) | Coerente com a LGPD, mas pseudonimizado não é anônimo [D-17, D-18] | Tabela de correspondência fora do Git; avaliar o risco de reidentificação antes de publicar Recortes |
| Risco de falso positivo como enum | Fine-tuning pode piorar calibração [B-21] | Medir curva risco-cobertura ou concordância do enum com o erro observado |
| Run 0 sobre fontes públicas | Pré-treino pode conter Loghub, Mordor e EVTX [A-7, B-19] | Reportar Run 0 por fonte pública e privada; reservar um subconjunto posterior ao cutoff do modelo base |
| IDs pseudonimizados nos Recortes | Risco de memorização [D-16] e de atalho por identificador [B-2] | Teste de *canaries* no adaptador; baseline que só vê identificadores |

## Lacunas que o artigo pode ocupar

1. **Triagem multi-fonte com modelo pequeno e local.** Não foi encontrado estudo revisado por
   pares com LoRA em LLM de até 4B para triar logs reais de várias Modalidades em JSON
   estrito, com split por incidente [B, lacuna 1; A, lacuna 1].
2. **Fidelidade literal como métrica.** Nenhum trabalho mede IoC ou Evidência alucinados por
   busca literal no log [A, lacuna 2].
3. **FPR de benign trigger sob taxa-base realista.** Quase ninguém relata FPR em
   benignos administrativos, e menos ainda projetado para a operação [A, lacuna 3; C, lacuna 4].
4. **Injeção contra modelo pequeno ajustado e dois canais de dados.** Os estudos usam modelos
   grandes por API. Ninguém avaliou dois canais de dados com autoridade assimétrica (Contexto
   pode rebaixar, Registro não) aplicada pelo runtime [C, lacunas 1 e 2].
5. **Proporção sintético:real medida no teste real.** Não há estudo que varie a proporção e meça
   o efeito em dados reais [B, lacuna 4; A, lacuna 6].
6. **Governança de datasets de logs de segurança para LLM.** Não foi encontrado trabalho
   revisado por pares sobre isso. Também faltam: medida do risco de aprovar por regra e
   amostra em vez de linha a linha, padrão para aceitar sintéticos de gerador desconhecido e
   formato de atestação para uma aprovação humana ligada a hashes. A perspectiva da LGPD é
   rara na literatura internacional [D, lacunas].
7. **Arquitetura "modelo relata, runtime decide, humano aprova".** Os sistemas revisados agem
   ou alimentam SOAR. A separação entre relato e ação não aparece avaliada [A, lacuna 8].
8. **Custo local.** Não há medida de latência e memória de modelos de cerca de 4B em Apple
   Silicon [C, lacuna 6].

## Proposta de enquadramento do artigo

> **Atualizado em 25/11/2026:** o responsável decidiu um artigo único, com um só agente (o
> Guardião com Ferramentas de leitura, ADR 0004). O resultado principal passa a ser a redução da
> carga cognitiva na triagem do SOC, com auditabilidade e supervisão humana, ligada à governança
> dos dados por o modelo e a arquitetura serem locais. Fine-tuning, RL com custo, fidelidade e
> defesa contra injeção viram meios e condições de validade desse resultado. As perguntas abaixo
> são da versão anterior e estão em revisão.

**Tese declarada (25/11/2026):** um Guardião pequeno, que roda na máquina monitorada e investiga
com Ferramentas de leitura, reduz a carga cognitiva da triagem no SOC sem tirar do analista a
decisão, deixa cada Relato auditável e mantém os dados na origem, enviando ao SOC só o necessário.

**Tese de trabalho anterior:** um modelo pequeno, local e ajustado com LoRA pode triar logs de
SOC com fidelidade verificável quando três peças trabalham juntas: dados com proveniência
auditável, avaliação que evita os *pitfalls* conhecidos e um runtime determinístico que limita o
que a saída do modelo pode causar.

**Perguntas de pesquisa candidatas (versão anterior):**

- **QP1, triagem:** o fine-tuning de um modelo de cerca de 4B supera o zero-shot, os baselines
  leves e o Rival no Teste real, em Macro-F1 e em FPR de `benign` e `expected_admin`? Quais
  fatores da matriz (alvos, quantização, rank, máscara) explicam a diferença?
- **QP2, fidelidade:** quanto o modelo alucina IoCs e Evidência, medidos por checagem literal, e
  como isso varia com esses fatores?
- **QP3, robustez:** quanto a injeção em campos do Registro rebaixa ou infla vereditos? Quanto a
  regra aplicada pelo runtime reduz o efeito, comparada à defesa só por treino?
- **QP4, governança:** uma cadeia verificável do hash de origem até a Liberação é viável num
  laboratório pequeno? Quanto custa e quanto arrisca aprovar por Família em vez de por linha?

**Ameaças à validade a declarar desde já:** teste com 166 exemplos, uma única pessoa como
curadora e liberadora, proporção de classes de desenho, fontes públicas possivelmente presentes
no pré-treino, sintéticos de gerador desconhecido e ausência de dados de produção.

**Venues a avaliar (prazos não verificados):** SBSeg, workshop AISec (ACM CCS), DIMVA, ACSAC e
periódicos como Computers & Security. O eixo de governança com LGPD favorece um venue
brasileiro ou uma trilha de privacidade.

## Impacto na rodada 4 do desenho do Guardião

A rodada 4 está pendente. A pesquisa não derruba nenhuma das nove recomendações, mas muda
quatro delas:

- **Q1, Contexto e Registro:** manter a separação, mas a regra "só o Contexto rebaixa" passa a
  ser aplicada pelo Runtime por checagem literal, com fail-closed. O Projetor escapa
  delimitadores reservados no Registro.
- **Q3 e Q9, opensec por Família:** acrescentar ablação da proporção, registro do tamanho e do
  resultado da amostra de cada Família e um diagnóstico real contra sintético.
- **Q5, métricas:** acrescentar baselines leves e few-shot, FPR por classe e projetado,
  intervalos por bootstrap, calibração do risco de falso positivo e taxa de sucesso de ataque
  com intervalo de confiança, nas duas direções. A suíte estática passa a ser gate de
  regressão, não prova de robustez.
- **Q8, AGENTS.md:** o texto precisa refletir os ajustes acima.

Ficam para a rodada 5 as perguntas novas: hold-out temporal ou por fonte, prioridade do
controle `mask_prompt: false`, bootstrap contra seeds extras, modo explícito de evidência
insuficiente, Liberação assinada com registro de inferências e avaliação de reidentificação
antes de publicar Recortes.

## Referências centrais

As fichas completas estão nas notas. Esta lista traz os trabalhos que sustentam as afirmações
centrais desta síntese.

- Arp et al. (2022). *Dos and Don'ts of Machine Learning in Computer Security.* USENIX Security. https://www.usenix.org/conference/usenixsecurity22/presentation/arp
- Pendlebury et al. (2019). *TESSERACT.* USENIX Security. https://www.usenix.org/conference/usenixsecurity19/presentation/pendlebury
- Le e Zhang (2022). *Log-based Anomaly Detection with Deep Learning: How Far Are We?* ICSE. https://arxiv.org/abs/2202.04301
- Landauer, Skopik e Wurzenberger (2024). *A Critical Review of Common Log Data Sets…* FSE (PACMSE). https://arxiv.org/abs/2309.02854
- Yu et al. (2024). *Deep Learning or Classical Machine Learning?* ICSE. https://conf.researchr.org/details/icse-2024/icse-2024-research-track/21/Deep-Learning-or-Classical-Machine-Learning-An-Empirical-Study-on-Log-Based-Anomaly-
- Engelen, Rimmer e Joosen (2021). *Troubleshooting an Intrusion Detection Dataset: the CICIDS2017 Case Study.* IEEE SPW. DOI 10.1109/SPW53761.2021.00009
- Flood et al. (2024). *Bad Design Smells in Benchmark NIDS Datasets.* IEEE EuroS&P. https://detlearsom.github.io/pubs/BadSmells-EuroSP24-finaldraft.pdf
- Dettmers et al. (2023). *QLoRA.* NeurIPS. https://arxiv.org/abs/2305.14314
- Biderman et al. (2024). *LoRA Learns Less and Forgets Less.* TMLR. https://arxiv.org/abs/2405.09673
- Shi et al. (2024). *Instruction Tuning With Loss Over Instructions.* NeurIPS. https://arxiv.org/abs/2405.14394
- Huerta-Enochian e Ko (2024). *Instruction Fine-Tuning: Does Prompt Loss Matter?* EMNLP. https://arxiv.org/abs/2401.13586
- Tam et al. (2024). *Let Me Speak Freely?* EMNLP Industry. https://aclanthology.org/2024.emnlp-industry.91
- Tsegai et al. (2026). *From Investigation Failures to Reliable SOC Agents.* Preprint. https://arxiv.org/abs/2610.10608
- Zhao et al. (2025). *Information-Dense Reasoning for Efficient and Auditable Security Alert Triage.* Preprint. https://arxiv.org/abs/2512.08169
- Saju e Azim (2026). *Toward Autonomous SOC Operations: End-to-End LLM Framework for Threat Detection, Query Generation, and Resolution in Security Operations.* Preprint. https://arxiv.org/abs/2604.27321
- Alahmadi, Axon e Martinovic (2022). *99% False Positives.* USENIX Security. https://www.usenix.org/conference/usenixsecurity22/presentation/alahmadi
- Kokulu et al. (2019). *Matched and Mismatched SOCs.* ACM CCS. DOI 10.1145/3319535.3354239
- Greshake et al. (2023). *Not what you've signed up for.* ACM AISec. https://arxiv.org/abs/2302.12173
- Zverev et al. (2025). *Can LLMs Separate Instructions From Data?* ICLR. https://arxiv.org/abs/2403.06833
- Chen et al. (2025). *StruQ.* USENIX Security. https://www.usenix.org/conference/usenixsecurity25/presentation/chen-sizhe
- Nasr et al. (2026). *The Attacker Moves Second.* USENIX Security. https://www.usenix.org/conference/usenixsecurity26/presentation/nasr
- Karanjai et al. (2026). *Context Contamination in LLM Analysis of Network Security Logs.* USENIX Security. https://www.usenix.org/conference/usenixsecurity26/presentation/karanjai
- Landauer et al. (2026). *Just Testing, Move Along.* Preprint. https://arxiv.org/abs/2607.24174
- Debenedetti et al. (2025). *Defeating Prompt Injections by Design (CaMeL).* Preprint. https://arxiv.org/abs/2503.18813
- Beurer-Kellner et al. (2025). *Design Patterns for Securing LLM Agents against Prompt Injections.* Preprint. https://arxiv.org/abs/2506.08837
- MITRE ATT&CK T1698 e T1685.007 (2026). https://attack.mitre.org/techniques/T1685/007/
- Gebru et al. (2021). *Datasheets for Datasets.* CACM. https://arxiv.org/abs/1803.09010
- Mitchell et al. (2019). *Model Cards for Model Reporting.* FAT*. https://arxiv.org/abs/1810.03993
- Raji et al. (2020). *Closing the AI Accountability Gap.* FAT*. https://arxiv.org/abs/2001.00973
- Longpre et al. (2024). *A large-scale audit of dataset licensing and attribution in AI.* Nature Machine Intelligence. https://arxiv.org/abs/2310.16787
- Torres-Arias et al. (2019). *in-toto.* USENIX Security. https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias
- OpenSSF Model Signing. https://github.com/ossf/model-signing-spec
- Wan et al. (2023). *Poisoning Language Models During Instruction Tuning.* ICML. https://proceedings.mlr.press/v202/wan23b.html
- Dong et al. (2025). *The Philosopher's Stone: Trojaning Plugins of Large Language Models.* NDSS. https://www.ndss-symposium.org/ndss-paper/the-philosophers-stone-trojaning-plugins-of-large-language-models/
- Carlini et al. (2021). *Extracting Training Data from Large Language Models.* USENIX Security. https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting
- Coull et al. (2007). *Playing Devil's Advocate.* NDSS. https://www.ndss-symposium.org/?p=2598
- Brasil. Lei nº 13.709/2018 (LGPD). https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- União Europeia. Regulamento (UE) 2024/1689 (AI Act) e Regulamento (UE) 2026/1744. https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng
- NIST AI 100-1 (2023) e NIST AI 600-1 (2024). https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
