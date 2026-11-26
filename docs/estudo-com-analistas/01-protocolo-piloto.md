# Protocolo do piloto: triagem de SOC com e sem Relato do Guardião

> Rascunho, 26/11/2026, para o Estudo com analistas do
> [ADR 0006](../adr/0006-nenhum-relato-fecha-sozinho.md). O responsável pelo estudo submete o
> protocolo ao CEP da sua instituição pela Plataforma Brasil. Os modelos de projeto e de TCLE do
> CEP prevalecem sobre este texto. Este rascunho descreve normas, mas não é aconselhamento
> jurídico. Nenhum dado de participante entra neste repositório.

## 1. Justificativa

- Analistas de SOC relatam que a maior parte dos alarmes é falso positivo (G-3).
- O Guardião quer reduzir a carga de triagem que chega ao analista. Indicadores automáticos
  medem o trabalho encaminhado, mas não o esforço mental (G-1). Para afirmar redução de carga
  cognitiva, é preciso medir com pessoas.
- Agentes de triagem aumentam a produtividade, mas criam viés de automação. No único ensaio
  controlado com analistas encontrado, quem via o veredito do agente deixou passar mais o falso
  negativo plantado: 46% contra 17% (G-6, preprint do fornecedor).

## 2. Objetivos e hipóteses

**Objetivo primário:** estimar a diferença pareada de carga de trabalho percebida (RTLX) entre
triar Recortes com o Relato do Guardião e sem ele.

**Objetivos secundários:**

- tempo por Recorte;
- acurácia do Veredito do analista contra a referência;
- detecção de Erros plantados, separada por direção;
- dependência excessiva: P(concorda | Relato errado) contra P(concorda | Relato certo).

**Hipóteses:**

- **H1:** o RTLX é menor com Relato.
- **H2:** o tempo por Recorte é menor com Relato.
- **H3:** a acurácia com Relato não é pior que sem Relato.
- **H4:** com Relato, o analista detecta menos o malicious perdido plantado do que o Falso
  positivo plantado. É uma tentativa de replicar G-6.

Por ser um piloto, as hipóteses são exploratórias. O piloto estima tamanhos de efeito para um
estudo confirmatório.

## 3. Desenho

- **Intra-sujeito, cruzado e contrabalançado.** Cada participante faz dois blocos: um com Relato
  e outro só com o Recorte. Metade começa com Relato. Os dois conjuntos de Recortes também se
  alternam entre as condições, num quadrado latino 2 × 2.
- **Blocos:** 24 Recortes do Teste real da v12 por bloco. Cada bloco tem 10 Alertas de
  referência, 12 benign ou expected_admin e 2 Recortes incompletos, com Modalidades
  equilibradas entre os blocos.
- **Relatos:** os do adaptador do Guardião escolhido para o estudo, sem edição.
- **Erros plantados:** no bloco com Relato, dois Relatos são trocados por Relatos errados de
  propósito, em Recortes em que o Guardião acertou. Um é um malicious perdido, com Relato benign
  num Recorte malicious. O outro é um Falso positivo, com Relato malicious num Recorte benign. Os
  erros naturais do Guardião são analisados à parte.
- **Tarefa:** para cada Recorte, o participante escolhe um dos quatro Vereditos e marca a
  confiança de 1 a 5. O tempo é registrado automaticamente.

**Sessão (cerca de 70 minutos):**

1. TCLE e questionário de perfil: faixa de experiência e função.
2. Treino com 4 Recortes fora dos blocos.
3. Bloco 1 e RTLX.
4. Pausa de 5 minutos.
5. Bloco 2 e RTLX.
6. Questionário final de preferência.
7. Debriefing, que revela os Erros plantados.

## 4. Participantes

- **Tamanho:** de 8 a 12 participantes. Com 12 pares, um teste pareado bilateral com α = 0,05
  tem cerca de 80% de poder para um efeito d ≈ 0,9. Esse cálculo é inferência e só detecta
  efeitos grandes.
- **Inclusão:** 18 anos ou mais e, de preferência, pelo menos 6 meses de triagem de alertas
  num SOC. Na falta deles, pós-graduandos com disciplina de segurança e prática em análise de
  logs. O artigo declara esse limite.
- **Exclusão:** quem participou da curadoria dos dados ou do desenvolvimento do Guardião.
- **Recrutamento:** convite sem vínculo de subordinação com o pesquisador, para não haver
  coerção. A participação é voluntária e sem remuneração, com ressarcimento de despesas quando
  houver.

## 5. Medidas e análise

| Medida | Como | Análise |
| --- | --- | --- |
| RTLX | Seis subescalas de 0 a 100, sem pesos, após cada bloco | Diferença pareada, teste de Wilcoxon e checagem de efeito de ordem |
| Tempo por Recorte | Registro automático | Mediana por participante e diferença pareada |
| Acurácia | Veredito contra a referência | Macro-F1 e malicious perdidos por condição |
| Erros plantados | Analista corrigiu ou aceitou | Proporção por direção, com intervalo exato |
| Dependência excessiva | Concordância com o Relato, certo ou errado | Comparação descritiva |
| Preferência | Questionário final | Descritiva |

- O plano de análise fica registrado neste repositório antes da primeira coleta.
- Todos os resultados são publicados, inclusive os desfavoráveis ao Guardião (ADR 0006).

## 6. Riscos, benefícios e cuidados

- **Riscos mínimos:** cansaço, desconforto ao errar e constrangimento com o desempenho.
- **Cuidados:**
  - a sessão tem pausa;
  - o participante pode parar a qualquer momento sem prejuízo;
  - o desempenho individual nunca é divulgado nem repassado a empregadores.
- **Material:** os Recortes vêm de datasets públicos da v12. Nenhum log confidencial do
  participante ou do empregador entra no estudo.
- **Benefícios:** indiretos, como contribuição ao conhecimento. O participante pode pedir o
  próprio resultado.
- **Omissão parcial:** o TCLE informa que os Relatos podem conter erros, mas não diz quais nem
  que alguns são plantados. Saber disso mudaria a vigilância medida. O debriefing revela tudo, e
  o participante pode retirar seus dados depois dele. Esta omissão precisa de justificativa
  aceita pelo CEP.

## 7. Dados e confidencialidade

- **Dados coletados:** código do participante, faixa de experiência, Vereditos, confiança,
  tempos, RTLX e preferência.
- **Separação:** os TCLEs assinados ficam separados dos dados de análise, que só levam o código.
- **Armazenamento:** cifrado, na máquina do pesquisador, fora do Git e do wiki.
- **Retenção:** 5 anos após o término da pesquisa, sob guarda do pesquisador (Res. CNS 466/2012,
  item XI.2.f, conferido na BVS-MS em 26/11/2026), ou o prazo maior que o CEP exigir.
- **Publicação:** só dados agregados. Um conjunto de dados anonimizado só é publicado com
  consentimento específico no TCLE.

## 8. Itens mínimos do TCLE

O TCLE segue o modelo do CEP. Pela Res. CNS 466/2012 (conferida na BVS-MS em 26/11/2026), ele
cobre:

- justificativa, objetivos e procedimentos, incluindo a alocação em condições (IV.3.a);
- desconfortos, riscos, benefícios e cuidados (IV.3.b);
- acompanhamento e assistência (IV.3.c);
- liberdade de recusar e de retirar o consentimento sem penalização (IV.3.d);
- sigilo e privacidade (IV.3.e);
- uma via para o participante (IV.3.f);
- ressarcimento de despesas e indenização por danos (IV.3.g e IV.3.h);
- duas vias assinadas, com contatos do pesquisador, do CEP e da CONEP quando pertinente (IV.5.d).

## 9. Orçamento e cronograma

- **Orçamento:** sem financiamento. A interface roda localmente na máquina do pesquisador.
- **Cronograma:** a coleta só começa depois da aprovação do CEP. O piloto usa o adaptador do
  Guardião que existir nessa data, e a versão dele é registrada.

## 10. Pendências do responsável

- Escolher o CEP e o pesquisador responsável na Plataforma Brasil.
- Escolher sessão presencial ou remota.
- Escolher a fonte de recrutamento.
- Decidir se o desenho também testa a variante em que o analista decide antes de ver o Relato
  (G-10).
