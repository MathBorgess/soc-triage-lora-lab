# Revisão de literatura: RL com ferramentas, custo e medição do resultado

> Rascunho de pesquisa, 25/11/2026. Complementa a [revisão 01](01-revisao-de-literatura.md)
> para o desenho do Guardião com Ferramentas de leitura (ADR 0004) e para o artigo único, cujo
> resultado principal é a Carga no analista, com auditabilidade, supervisão humana e governança
> local.

Esta revisão responde quatro perguntas:

1. O resumo colado pelo responsável sobre agentes de SOC está correto?
2. Como treinar por RL um Guardião que investiga com ferramentas, pesando acerto e custo?
3. Em que ambiente treinar e avaliar?
4. Como medir carga, supervisão, auditabilidade e governança de forma defensável?

As fichas completas estão em três notas:

- [E — Verificação e ambientes](notas/E-verificacao-e-ambientes.md): 28 fichas e uma tabela de ambientes.
- [F — RL com ferramentas e custo](notas/F-rl-com-ferramentas-e-custo.md): 22 fichas, infraestrutura e estimativa de tempo.
- [G — Carga, supervisão e governança](notas/G-carga-supervisao-e-governanca.md): 20 fichas e uma tabela de métricas.

## Método e limites

As fichas seguem as regras da revisão 01: página do trabalho aberta na sessão, venue tirado dela
e "NÃO VERIFICADO" quando não abriu. Conferi de novo, na API do arXiv, 16 identificadores citados
nesta síntese, e todos existem com o título informado. Também conferi a publicação de Saju e Azim
no PMLR 318. Os números dentro dos artigos vêm da leitura dos agentes. A maior parte da
literatura de 2025 e 2026 sobre agentes de SOC é preprint.

## 1. O resumo colado não se sustenta como escrito

Nenhuma das seis afirmações do resumo se confirma inteira:

| Afirmação | Veredito | O que a fonte diz |
| --- | --- | --- |
| Self-Refine: 73 descartes corretos viraram escalonamentos, FP de 8 para 65 | Parcial | Os números existem, mas o artigo não diz que os 73 descartes eram corretos [E-1] |
| CoVe converteu ataques em descartes | Confirmada | O F1 caiu de 0,669 para 0,371 [E-1] |
| "Empty-retrieval bias" | Parcial | O fenômeno existe: buscas vazias levam ao descarte de ataques. O termo não aparece [E-1] |
| Sem o Judge, o F1 do AIDA cai de 0,952 para 0,895 | Confirmada, com ressalva | Vale num subconjunto de 300 alertas [E-1] |
| Agentes verbosos perdem para prompts diretos | Parcial, falsa como generalização | O AIDA, multiagente, chegou a 0,958. O artigo diz que a estrutura importa mais que o volume de computação [E-1] |
| CoT destrói a calibração; calibrador separado dá +43,0 e +18,3 pp | Parcial | A perda de calibração é só argumentada. Os ganhos existem, mas a precisão benigna no teste ficou em 90,8%, abaixo da meta de 98% [E-2] |
| Grafos de processos e modelos destilados: 91,7% de precisão e 97% de recall | Parcial | Os números são do DistilBERT, não do melhor modelo. Só o DistilBERT é destilado [E-3] |
| DoLLM supera classificadores tabulares em mais de 35% | Parcial | Ganho de "pelo menos 35,1%", contra baselines que não são só tabulares [E-4] |
| ADÉ valida com retro-hunt e faz mutações automáticas | Parcial | O retro-hunt existe. As mutações são trabalho futuro [E-5] |
| Ensembles de SLMs de 7B a 9B cortam o FPR pela metade | Não confirmada | A única fonte usa o Llama-3.3-70B no ensemble e reduz o FPR em cerca de 22% frente ao melhor modelo isolado [E-6] |

**Leitura para o projeto:** as frentes que o resumo aponta existem. A literatura de agentes de
SOC é recente, quase toda preprint, e números citados de segunda mão costumam sair do contexto.
O artigo só cita números lidos na fonte.

## 2. Ninguém treinou por RL um agente de SOC com custo de erro e de ferramenta

Os trabalhos mais próximos deixam a lacuna aberta:

- **I2C-GRPO** treina com GRPO um agente de 4B para triagem de DDoS, mas com recompensa
  insensível a custo e em formato bandit sobre prefixos fixos [E-7].
- **OpenSec** é o único ambiente público com penalidade de FP, custo por passo e injeção. O RL
  preliminar num modelo de 4B terminou com FP de 0,70 [E-8], [F-22].
- **Khanna et al.** usam GRPO na triagem, mas sem ferramentas e com recompensa binária [E-2].
- **SENTINEL-RL** usa PPO num controlador pequeno, não no LLM [E-10].
- **HESP** separa "o que consultar" de "quando parar" com um controlador externo, sem treino, e
  leva modelos locais de 7B a 8B de quase zero a perto de 1,0 em conclusão verificada [E-12].

Na literatura de RL com ferramentas fora de segurança, as lições são consistentes:

- **Sem custo, o uso de ferramenta cresce.** No ReSearch as buscas aumentam durante o treino, e
  no ReTool a ferramenta chega a 98% das questões [F-9], [F-11].
- **Recompensa aditiva de custo colapsa.** O modelo aprende a cortar chamadas sem acertar. A forma
  multiplicativa, que só aplica o custo quando a resposta está certa, foi estável no OTC e no
  L1 [F-15], [F-16].
- **Uma política condicionada ao orçamento cobre a fronteira inteira** de custo contra acerto,
  sem treinar uma política por ponto [F-16].
- **As respostas da ferramenta precisam ficar fora da loss.** No Search-R1, mascará-las levou o EM
  de 0,343 a 0,431 [F-8].
- **O GRPO original alonga as respostas erradas.** O Dr. GRPO e o DAPO corrigem isso [F-3],
  [F-4].
- **Matriz de custo mal calibrada leva ao colapso numa classe.** Na detecção de vulnerabilidades,
  o modelo passou a marcar quase tudo como vulnerável [F-21]. No Guardião, o risco é convergir
  para `suspicious`.
- **Recompensas aleatórias também melhoram o Qwen2.5** [F-7]. É preciso um controle com
  recompensa embaralhada.
- **Custo de erro clássico:** Lee et al. separam custo de dano, de resposta e operacional, e o
  custo operacional corresponde ao custo de ferramenta [E-21]. Para Elkan, com probabilidade
  calibrada o custo FP/FN vira um limiar [E-20]. Axelsson mostra que, em taxas-base realistas, o
  falso alarme é o fator limitante [E-22].

## 3. Infraestrutura e custo de treino

- **MLX local:** o `mlx-lm-lora` 5.10.2 faz GRPO de turno único, sem laço de ferramentas
  (conferido no código). Serve para o ambiente, as recompensas, os baselines, o SFT de partida e
  um piloto em formato bandit.
- **Colab L4:** o TRL já tem `environment_factory`, máscara das respostas de ferramenta
  (`tool_mask`) e template de treino para o Gemma 4 com `enable_thinking=false`. O vLLM suporta o
  Gemma 4 com LoRA. O Unsloth não acelera a geração do Gemma 4.
- **Estimativa, que é inferência:** uma época com 1.000 alertas e 8 trajetórias por alerta leva
  cerca de 7 a 8 h numa L4 e de 3 a 5 dias no M1 Max. A doc do Unsloth sugere pelo menos 300
  passos antes de a recompensa subir. A vazão real do E4B na L4 precisa ser medida.

## 4. Ambiente de treino e avaliação

Nenhum ambiente liberado tem, ao mesmo tempo, veredito por alerta, alertas benignos e SIEM
executável [E, lacuna 2]:

- **ALERT-BENCH** tem o desenho certo: alertas Wazuh do AIT-LDSv2 com rótulo por alerta,
  ferramentas parametrizadas e somente-leitura. Os dados não foram liberados, mas são
  reconstruíveis com o AIT-ADS e o AIT-LDSv2, que já estão em `data/raw`. Há risco de
  contaminação: os cenários russellmitchell e wardbeck estão no treino da v12, que é onde o
  AIDA foi avaliado. **Correção de 26/11/2026:** nenhum cenário está livre. O `validacao.json`
  da v12 põe fox, russellmitchell, wardbeck, wheeler e wilson no treino, santos e shaw na
  validação e harrison no teste (ADR 0007).
- **ExCyTIn-Bench** (ICML 2026, código MIT) é executável, mas é QA só de ataque, sem benignos, com
  juiz GPT-4o e licença de dados conflitante. Serve só para testar se a política de consulta
  generaliza.
- **Licenças:** o AIT-LDSv2 é CC BY-NC-SA 4.0. A cláusula NC limita o uso comercial de derivados,
  o que importa para consultoria. A cláusula SA vale para qualquer dataset derivado publicado.

## 5. Como medir o resultado principal

- **Proxies computacionais medem a carga encaminhada, não a carga cognitiva.** Sem estudo com
  pessoas, a afirmação defensável é "redução da carga de triagem encaminhada ao SOC". Afirmar
  carga cognitiva exige NASA-TLX, RTLX ou COSS em comparação pareada com e sem Relato
  [G-1], [G-2].
- **O viés de automação pesa mais na direção benigna.** No único ensaio controlado com analistas
  de triagem, 46% dos que viam o veredito do agente não pegaram o falso negativo plantado,
  contra 17% sem o veredito. No falso positivo plantado não houve diferença significativa
  [G-6, preprint do fornecedor].
- **A evidência legível pode aumentar a confiança indevida.** Analistas aceitaram explicações
  com acurácia menor quando elas pareciam apoiadas em evidência [G-7]. Explicações só reduzem
  a dependência excessiva quando barateiam a verificação [G-11].
- **Auditabilidade:** a reprodutibilidade se mede com TARr@N (concordância da saída inteira em N
  execuções) e TARa@N (concordância da resposta extraída) [G-14]. Não há medição publicada de
  determinismo do llama.cpp em CPU, então o artigo precisa medir. A integridade do Diário se
  mede com a taxa de detecção de adulterações injetadas e o custo por linha [G-15].
- **Governança:** fator de redução de egress (bytes do Recorte bruto ÷ bytes da Remessa),
  identificadores pessoais por Remessa, perda de detecção frente a um classificador central com
  log bruto e finalidade documentada para cada campo enviado [G-17], [G-19].
- **Estudo com analistas no Brasil:** pela Res. CNS 466/2012, item VII.1, pesquisa com seres
  humanos, inclusive com seus dados, passa pelo sistema CEP/CONEP. A dispensa da Res. 510/2016
  só vale se o protocolo inteiro couber nos casos listados (Ofício CONEP 17/2022). Pelo texto,
  um experimento com triagem, NASA-TLX e erros plantados não cabe. Quem decide o enquadramento é
  o CEP da instituição [G-20]. Isto descreve o texto e não é aconselhamento jurídico.

## 6. O que muda no desenho

| Ponto | Encaminhamento proposto | Base |
| --- | --- | --- |
| Afirmação sobre carga | Proxies como resultado quantitativo principal. Piloto com analistas submetido ao CEP; sem aprovação a tempo, o artigo fala só em carga de triagem encaminhada | G-1, G-2, G-20 |
| Fechamento automático | Nenhum Relato fecha sozinho no estudo. Benignos vão para uma fila de confirmação em lote, e a carga dessa fila entra na medida | G-6, G-8 |
| Recompensa | Gate de validade e Evidência; utilidade por matriz de custo explícita; custo só nas respostas certas, com piso; chamada desnecessária definida por regra; descarte só com evidência recuperada | F-15, F-16, E-21, E-1 |
| Fronteira | Uma política condicionada ao peso de custo no prompt, com 2 ou 3 políticas fixas para conferir | F-16 |
| Algoritmo | Dr. GRPO ou DAPO, máscara das respostas de ferramenta, filtro de grupos sem variância, KL pequeno como ablação | F-3, F-4, F-8, F-12 |
| Stack | MLX para ambiente, recompensas, SFT e piloto; GRPO multi-turno no Colab L4 com TRL | F, infraestrutura |
| Ambientes | Ambiente de treino da v12 mais uma reconstrução do ALERT-BENCH sobre AIT-ADS e AIT-LDSv2, seguindo os splits da v12: harrison na avaliação, santos e shaw na seleção (ADR 0007); ExCyTIn opcional | E-1, E-23, E-27, `validacao.json` |
| Baselines | Guardião sem ferramentas, Direct-Prompt com 3 chamadas, controlador externo estilo HESP, regras ou TF-IDF, controle com recompensa embaralhada | E-12, F-7 |
| Calibração | Manter o enum de risco e medir a calibração na validação; calibrador separado fica fora do escopo | E-2, E-20 |
| Diário | Cadeia de hash com checkpoints assinados; taxa de detecção de adulteração e TARr@N | G-14, G-15 |

## Lacunas que o artigo ocupa

1. RL de um agente de SOC com ferramentas e recompensa sensível a custo de erro e de
   investigação, sobre logs reais [E, lacuna 1; F, lacuna 1].
2. Um ambiente com veredito por alerta, alertas benignos e ferramentas somente-leitura,
   reconstruído de dados públicos [E, lacuna 2].
3. Modelo pequeno e local em triagem agêntica: o Gemma 4 E4B não foi avaliado em nenhum
   ambiente encontrado [E, lacuna 5].
4. Determinismo de inferência local em CPU como base de auditoria [G, lacunas].
5. Comparação medida entre enviar logs brutos e processar na máquina, em volume e exposição de
   dados pessoais [G, lacunas].
