# Revisão integral: Saju e Azim (2026), framework de LLM de ponta a ponta para SOC

> Leitura integral feita em 25/11/2026 a partir da versão HTML v1 do arXiv. As contas de
> consistência nas seções marcadas como "conta nossa" foram feitas sobre os números publicados
> nas tabelas do artigo.

## Ficha

- **Referência:** Saju, M. H.; Azim, A. (2026). *Toward Autonomous SOC Operations: End-to-End
  LLM Framework for Threat Detection, Query Generation, and Resolution in Security Operations.*
  arXiv:2604.27321v1 [cs.CR], 30/04/2026. https://arxiv.org/abs/2604.27321
- **Status:** preprint. A página não declara venue, *comments* nem *journal-ref*. O HTML traz
  marcas de template de anais, sem nome.
- **Afiliação:** Ontario Tech University, Canadá. É o mesmo grupo do SynRAG (CASCON 2025), sobre
  geração de consultas para SIEM.
- **Licença do texto:** CC BY-SA 4.0.
- **Dados e código:** dados de produção, não publicados. O artigo não traz link para código.

## O que o artigo faz

O framework tem três módulos em sequência.

1. **Detecção.** Classifica cada entrada de log de SIEM como crítica ou não crítica. São 20.000
   entradas de vários fornecedores, com 40% de críticas.
   - Cinco classificadores clássicos usam features tabulares e embeddings MiniLM.
   - Seis LLMs recebem o log convertido em prompt, sem fine-tuning.
   - Um voto majoritário junta os três melhores LLMs: GPT-4o-mini, Gemma-3n-E4B-it e
     Llama-3.3-70B.
   - Um escore de risco combina o *magnitude* do SIEM com a probabilidade prevista.
2. **Coleta de evidência (SQM).** Gera consultas AQL (IBM QRadar) e YARA-L 2.0 (Google SecOps)
   a partir do pedido do analista. Usa três apoios: allow-lists de sintaxe, recuperação de
   consultas de referência por metadados e trechos da documentação oficial. O backbone escolhido
   é o GPT-4o.
3. **Resolução.** Prevê um entre 7 códigos de fechamento de tickets do ServiceNow: Benign
   Positive, External Attack (Unsuccessful ou Successful), Insider Threat (Unsuccessful ou
   Successful), Escalated with No Response e False Positive. O modelo devolve JSON com código,
   justificativa e ações. Usa RAG sobre dois anos de tickets fechados e runbooks, e compara
   resultados com e sem a evidência do SQM.

| Módulo | Resultado reportado |
| --- | --- |
| Detecção, ensemble | Acurácia 0,828; precisão 0,795; recall 0,708; F1 0,749; FPR 0,120 (Tabela 1) |
| Detecção, melhor modelo isolado | GPT-4o-mini: acurácia 0,826; recall 0,792; F1 0,782; FPR 0,153 |
| Detecção, Gemma-3n-E4B-it isolado | Acurácia 0,701; F1 0,663; FPR 0,327 |
| SQM | BLEU 0,384; ROUGE-L 0,731; 88% das consultas executam sem ajuste (Tabela 2 e seção 4.2) |
| Resolução, ensemble ponderado | Acurácia 0,900 e F1 0,857, contra 0,783 do melhor modelo sem SQM (Tabela 3) |
| Recomendação | Nota 8,70 de 10 dada por GPT-5.1 como juiz (Tabela 4) |
| Tempo | De cerca de 4 h para cerca de 10 min por ticket (seção 4.4) |

## Pontos fortes

- **Dados de produção.** Usa logs e tickets reais de SOC, raros na literatura.
- **FPR como métrica central.** O artigo justifica a escolha do ensemble pela queda de FPR, e
  não pela acurácia.
- **Restrição determinística em volta do LLM.** Allow-lists e extração determinística da
  consulta transformam geração aberta em síntese restrita. É a mesma ideia do nosso Validador e
  da lista fechada de CWE.
- **Evidência ajuda modelos pequenos.** O ganho do Gemma-3n-E4B com evidência do SQM foi o maior
  da Tabela 3: a acurácia vai de 0,732 a 0,848. Isso sustenta a aposta em modelo pequeno com
  bom Contexto.
- **Exclusão temporal no RAG.** Tickets recentes do teste ficam fora da base histórica.
- **Taxonomia de fechamento.** Benign Positive e False Positive aparecem separados, como os
  *benign triggers* de Alahmadi et al. (2022).

## Problemas metodológicos

### 1. A linha do ensemble na Tabela 1 é inconsistente (conta nossa)

As outras 11 linhas da Tabela 1 batem com a prevalência declarada de 40%. A acurácia calculada a
partir do recall e do FPR difere da reportada em no máximo 0,004. A linha do ensemble não bate:

- Com 40% de críticos, recall 0,708 e FPR 0,120 dão acurácia de 0,811, não 0,828.
- A precisão reportada (0,795) é compatível com 40%. A acurácia reportada só fecharia com cerca
  de 30% de críticos.

A acurácia de 82,8%, que está no resumo, não é derivável dos outros números da mesma linha.
Pode ser outro subconjunto de avaliação ou um erro de digitação. O artigo não explica.

### 2. Os baselines clássicos ficam perto do classificador trivial

Prever "não crítico" para tudo dá acurácia de 0,600 com 40% de críticos (conta nossa). A
regressão logística (0,590) e o Naive Bayes (0,592) ficam abaixo disso. AdaBoost e XGBoost
(cerca de 0,67) passam pouco, com recall abaixo de 0,25. Baselines tão fracos indicam features
pobres ou rótulo ruidoso, e inflam a vantagem dos LLMs (*inappropriate baseline*, P6 em Arp et
al., 2022).

### 3. O rótulo pode vazar das features

O rótulo crítico ou não crítico vem da "severidade e indicadores de risco contextuais" (seção
3.1). O artigo não diz quem rotulou nem como. O escore de risco usa o *magnitude* do próprio
SIEM. Se o rótulo também deriva da severidade do SIEM, o modelo aprende a reproduzir o SIEM, e
não a julgar o evento (*spurious correlations*, P4).

### 4. O protocolo de split não é descrito

O artigo não descreve split de treino e teste, agrupamento por incidente, ordem temporal nem
quantos dos 20.000 logs passaram pelos LLMs. Os três LLMs do ensemble foram escolhidos como "os
de melhor desempenho", sem dizer em qual conjunto. Se foi no teste, há *data snooping* (P3 e P5).

### 5. O ensemble não domina o melhor modelo isolado

O GPT-4o-mini sozinho tem acurácia quase igual (0,826), recall maior (0,792 contra 0,708) e F1
maior (0,782 contra 0,749). O ensemble só ganha em FPR (0,120 contra 0,153). Chamar isso de
"melhor trade-off" depende de quanto vale cada falso negativo, e o artigo não discute esse
custo. Não há intervalos de confiança.

### 6. A Tabela 3 reporta recall ponderado, não macro

A seção 3.4.3 diz que precisão, recall e F1 são macro. Na Tabela 3, porém, o recall é igual à
acurácia nas 13 linhas. Isso acontece sempre com o recall ponderado pelo suporte, e quase nunca
com o macro. Com 7 classes desbalanceadas, a diferença importa, porque o macro expõe as classes
raras, como Insider Threat.

### 7. O teste de resolução parece pequeno, com denominadores variáveis (conta nossa)

O artigo não informa quantos tickets foram testados. Várias acurácias da Tabela 3 só fecham com
46 tickets: 0,783 = 36/46, 0,848 = 39/46 e 0,717 = 33/46. Outras não fecham com 46: 0,900, 0,732,
0,659 e 0,600. Isso sugere denominadores diferentes por linha, talvez respostas inválidas
descartadas ou subconjuntos diferentes. Com cerca de 46 tickets, ir de 78,3% para 90,0% são
cerca de 5 tickets, sem teste de significância.

### 8. A evidência pode vir de depois do fechamento

Para tickets já fechados, o SQM gera e executa consultas sobre o SIEM. O artigo não diz se a
janela das consultas termina no momento da triagem. Eventos posteriores podem revelar o
desfecho, como Successful contra Unsuccessful, e o ganho com SQM seria em parte vazamento
temporal. É a regra da nossa Âncora: eventos posteriores não contam.

### 9. O SQM é medido com métricas fracas e comparado a um baseline desigual

- BLEU e ROUGE-L medem semelhança textual com uma consulta de referência, não se a consulta
  traz a evidência certa. A executabilidade de 88% mede a sintaxe, não a semântica.
- O artigo não informa o número de pedidos testados.
- Os baselines não têm recuperação, documentação nem allow-lists. Não há ablação dos três
  componentes, mas o texto atribui o ganho "diretamente" a cada um.
- Não fica claro se as consultas de teste foram excluídas do repositório de exemplos. Se não
  foram, a recuperação devolve quase-duplicatas.

### 10. A recomendação é avaliada por um LLM juiz sem calibração humana reportada

As notas da Tabela 4 ficam entre 7,61 e 8,70, uma faixa estreita perto do teto. O artigo diz que
analistas validaram as notas automáticas, mas não traz número de analistas nem medida de
concordância.

### 11. Os 10 minutos não vêm de um experimento controlado

As 4 horas são o tempo total de resolução registrado no ticket, incluindo fila e espera. Os 10
minutos são o tempo de processamento do framework. A comparação não inclui o tempo do analista
para conferir a saída nem descreve como foi a implantação em produção.

### 12. Segurança e governança ficam fora

- **Injeção.** Logs e tickets carregam campos que o atacante controla, e o SQM gera consultas
  que são executadas no SIEM. O artigo não discute injeção de prompt nem consultas que escondam
  eventos (OWASP LLM05, saída mal tratada). As allow-lists garantem sintaxe, não intenção.
- **Privacidade.** Logs e tickets de produção vão para APIs de terceiros (GPT-4o, GPT-4o-mini,
  DeepSeek-V3). O artigo não trata residência de dados nem privacidade.
- **Reprodutibilidade.** Versões dos modelos, datas, temperatura e prompts não são informadas.
  "Qwen3" e "gemma" aparecem sem versão em parte das tabelas. Dados e código não estão
  disponíveis.
- **Autonomia.** O título fala em SOC autônomo, mas o texto descreve apoio ao analista. O
  artigo não discute o que pode ser fechado sem humano.

## Relação com o Guardião

**O artigo confirma:**
- FPR como critério de escolha ([revisão de literatura, achado 1](01-revisao-de-literatura.md)).
- Restrição determinística em volta do LLM: allow-lists e extração determinística, como o nosso
  Validador e a lista fechada de CWE.
- Ganho de modelos pequenos quando recebem evidência, o que sustenta o Contexto no Recorte.
- Separação entre Benign Positive e False Positive, paralela a `expected_admin` e `benign`.

**Onde o Guardião difere:**

| Aspecto | Saju e Azim | Guardião |
| --- | --- | --- |
| Modelo | APIs de terceiros e modelos abertos grandes, sem fine-tuning | Modelo de cerca de 4B, local, com LoRA |
| Unidade de entrada | Uma entrada de SIEM ou um ticket | Recorte multi-linha com Contexto e Registro |
| Saída | Binária (detecção) e 7 códigos de fechamento | Relato com 4 Vereditos, Evidência literal e Hipótese de vulnerabilidade |
| Fidelidade | Não mede alucinação | Checagem literal de IoC e Evidência |
| Injeção | Não trata | Sinal, Rebaixamento e Suíte adversarial |
| Ação | Recomenda ações; consultas executadas automaticamente | Só relata; contenção por regra com aprovação humana |
| Governança | Não trata | Proveniência por hash, Liberação assinada, Diário |
| Avaliação | Split não descrito, sem IC | Split por incidente, fonte nova, bootstrap, Teste real |

**O que vale aproveitar:**
- **A dimensão de desfecho.** Os códigos separam ataque com sucesso de ataque sem sucesso. O
  Veredito mede hostilidade, não desfecho. Um campo de desfecho fica como ideia para depois do
  v2, e não muda o contrato agora.
- **O escore de risco composto.** No Runtime, ordenar a fila humana por Severidade e Risco de
  falso positivo é uma regra simples e determinística no mesmo espírito.
- **O artigo como lição de método.** Os problemas 1, 6 e 7 viram itens de checagem do nosso
  protocolo:
  - reportar o n de cada métrica;
  - conferir que as métricas fecham entre si;
  - dizer se a média é macro ou ponderada;
  - contar as respostas inválidas no denominador.

## Como citar no artigo

Na seção de trabalhos relacionados, o artigo entra como o framework de SOC de ponta a ponta mais
próximo com dados de produção. Ele mostra o valor da restrição determinística e da evidência para
modelos pequenos. Também deixa abertas as lacunas que o Guardião ocupa: fine-tuning local,
fidelidade literal medida, defesa contra injeção, separação entre relato e ação, e governança
dos dados. Ele não serve como baseline numérico, porque dados, código e protocolo de split não
estão disponíveis.
