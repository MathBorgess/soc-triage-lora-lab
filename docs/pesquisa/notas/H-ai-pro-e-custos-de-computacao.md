# Tema H — Google AI Pro e custos de computação

- **Data da revisão:** 2026-11-26.
- **Executor:** subagente Claude Code (modelo Opus 5.5), por delegação. As páginas foram abertas nesta sessão com WebFetch, `curl` ou o navegador embutido, sempre **sem login**. Não alterei nenhum outro arquivo do repositório.
- **Leitura local (só leitura):** o Colab CLI oficial instalado pelo responsável (`google-colab-cli` 0.8.0, via `uv tool`). Rodei só `colab version`, `colab readme`, `colab skill` e `colab help <cmd>`, que não autenticam. Li também o código instalado do pacote. Não rodei `usage`, `new`, `run` nem `sessions`.
- **Contexto:** consultei o clone local da `mathai-wiki` (commit de 2026-10-30). Não há nota sobre AI Pro ou Colab. O contexto do projeto veio do pedido, do `AGENTS.md` e da nota F.
- **Convenções:**
  - **Tipo da fonte:** primária oficial, primária não documental, ou **secundária**.
  - **Verificado:** URL aberta nesta sessão, com data de acesso. "NÃO VERIFICADO" quando não abri ou quando a página não trouxe o dado.
  - Toda afirmação de uma ficha vem da URL da própria ficha, salvo outra URL na linha. Nas seções de análise, cito a ficha entre colchetes, por exemplo [H-3].
  - Preço, cota e taxa levam "(as of AAAA-MM-DD)". A data é a do dado na fonte, não a do acesso, quando a fonte diz quando mediu.
  - Tudo marcado **(inferência)** é cálculo ou leitura minha, não um fato das fontes.
- **Fonte primária não documental:** o código JavaScript e a configuração que o site do Colab envia a qualquer navegador. Eles mostram o que a interface exibe hoje. Podem mudar sem aviso e não são um compromisso público do Google.

---

## Resumo em seis linhas

1. O Google AI Pro dá **200 unidades de computação do Colab por mês** (as of 2026-11-26), no Brasil e nos EUA [H-1, H-2]. O plano custa **R$ 96,99/mês** no Brasil (as of 2026-11-26) [H-1].
2. O Google não publica a taxa de unidades por hora de cada acelerador. Ela aparece no painel de recursos do Colab e no `colab usage` [H-3, H-6, H-7].
3. Pelas taxas medidas por terceiros, a **L4 custa ~1,7 a 1,9 unidade/h** e rende mais trabalho por unidade, se o modelo couber em 24 GB (inferência) [H-10, H-9].
4. O AI Pro não inclui execução em segundo plano. Isso fica com o AI Ultra e o Colab Pro+ [H-5, H-4, H-6].
5. As taxas subiram entre o fim de outubro e novembro de 2026, segundo relatos no issue tracker do Colab. Há também falhas de alocação de L4, A100 e G4 desde ~16/11/2026 [H-9].
6. O plano de execução cabe em **~120–170 unidades na L4** (inferência), ou seja, menos de um mês de AI Pro.

---

## 1. Colab no Google AI Pro

### [H-1] Google One — Planos com IA do Google (versões Brasil e EUA). — [one.google.com/about/google-ai-plans](https://one.google.com/about/google-ai-plans/) · [versão EN/US](https://one.google.com/intl/en/about/google-ai-plans/?gl=US) · Primária oficial · Verificado (acesso 2026-11-26; o servidor entregou a versão "Brasil" pela geolocalização)

**O que diz**
- Preços no Brasil (as of 2026-11-26): AI Plus R$ 24,99/mês; **AI Pro R$ 96,99/mês**; AI Ultra 5x R$ 779,90/mês; AI Ultra 20x R$ 999,90/mês. O preço só aparece com o navegador renderizando a página.
- Tabela "Google Colab — Unidades de computação" (as of 2026-11-26): Plus 50/mês; **Pro 200/mês**; Ultra 5x 1.000/mês; Ultra 20x 2.000/mês. A versão US traz os mesmos números.
- Linha "Acesso a aceleradores avançados, tempos de execução mais longos e limites de uso do Gemini": Plus "Mais"; **Pro "Expandido"**; Ultra 5x "Maior"; Ultra 20x "Máximo".
- O card do AI Pro promete "acesso ampliado a aceleradores avançados e tempos de execução mais longos" no Colab, com 200 unidades por mês.
- Armazenamento do AI Pro: **5 TB** no Gmail, Drive e Fotos (as of 2026-11-26).
- "US$ 10 em créditos mensais do Google Cloud pelo Google Developer Program" no AI Pro. Ultra 5x: US$ 40. Ultra 20x: US$ 100 (as of 2026-11-26).
- Só contas pessoais podem assinar os planos com IA. Contas Workspace não podem.
- A página não lista GPUs, memória, duração de sessão nem validade das unidades.

**Relevância para o projeto (inferência)**
- A preço de Pay As You Go (ver H-4), 200 unidades valem cerca de R$ 116. Isso supera o preço do plano. Para este projeto, o Colab sozinho já paga o AI Pro.

### [H-2] Central de Ajuda do Google One — Benefícios do Google AI Pro. — [support.google.com/googleone/answer/14534406](https://support.google.com/googleone/answer/14534406?hl=en) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- "Google AI Pro members get 200 CCUs." (as of 2026-11-26)
- O benefício do Colab é: "Only available on the web", para maiores de 18 anos, "Available to Google One family plan managers" e "Not available to Google One trial memberships."
- A lista de países do benefício Colab inclui **Brazil**.
- Armazenamento: "5 TB or 10 TB of storage based on your specific Google AI Pro membership plan."
- Google Developer Program premium no AI Pro: "Gemini Code Assist: Get higher quotas"; "This includes a $10 Google Cloud credits each month"; "This includes 30 Firebase Studio workspaces." O benefício não pode ser compartilhado com a família e exige um perfil de desenvolvedor vinculado.
- AI Studio: "With Google AI Pro, you can have higher limits with Gemini 4 Neon and Nano Banana Pro."

**Relevância para o projeto (inferência)**
- O benefício Colab vai só para o gestor do plano família. Membros da família não ganham unidades.
- Um período de teste gratuito do Google One não dá unidades. O responsável precisa estar em período pago.

### [H-3] FAQ do Colab. — [research.google.com/colaboratory/faq.html](https://research.google.com/colaboratory/faq.html) · Primária oficial · Verificado (acesso 2026-11-26; sem data na página)

**O que diz**
- **Benefício dos planos de IA** ([#g1-what-is-google-one-ai](https://research.google.com/colaboratory/faq.html#g1-what-is-google-one-ai)): o plano dá "a monthly allotment of Colab compute units" e GPUs e TPUs mais fortes. A execução em segundo plano vem só "on higher plans". "The exact benefits depend on your plan".
- **Elegibilidade** (#g1-eligibility): não vale em período de teste. "Google AI plan benefits are only honored in countries where Colab offers its paid option."
- **Recarga** (#g1-recurrence): as unidades do Google One entram todo mês na data de início do plano. Para contas migradas, a data segue a chegada no país: "Europe, South America, Africa: September 10th".
- **Soma com assinatura avulsa** (#g1-pro-plus-and-g1): "the compute units from each are added to the same balance". As duas recargas podem cair em datas diferentes.
- **Limites** (#usage-limits): o timeout por inatividade, a vida máxima da VM e os tipos de GPU mudam com o tempo. "**Colab does not publish these limits**". Com saldo zerado, o usuário pago "will revert to the free-of-charge tier policies and restrictions".
- **Duração** (#idle-timeouts): em geral, "notebooks can run for at most 12 hours", conforme disponibilidade e padrão de uso. Esgotar as unidades pode encerrar a sessão. O Pro+ aceita execução contínua de até 24 h com saldo suficiente.
- **GPUs** (#gpu-availability): "The types of GPUs and TPUs that are available in Colab vary over time." A FAQ não lista os modelos.
- **Memória** (#available-memory): planos pagos acessam "a high memory system profile subject to availability". "All GPU chips have the same memory profile."
- Comprar espaço no Drive não aumenta o disco da VM do Colab (#drive-full).

**Relevância para o projeto (inferência)**
- O AI Pro é um "plano pago" para o Colab. Então vale o teto geral de **12 h por sessão** e o timeout por inatividade não publicado.
- Zerar o saldo no meio de um treino derruba a sessão. O monitoramento do saldo faz parte do plano de execução.

### [H-4] Colab — página de preços. — [colab.research.google.com/signup](https://colab.research.google.com/signup) · Primária oficial · Verificado (acesso 2026-11-26; renderizada no navegador sem login, preços em reais)

**O que diz**
- Preços no Brasil (as of 2026-11-26): **Pay As You Go R$ 58,00 por 100 unidades e R$ 258,00 por 500**. Colab Pro R$ 58,00/mês com 100 unidades. Colab Pro+ R$ 258,00/mês com 600 unidades.
- Validade: as unidades de Pay As You Go, Pro e Pro+ são "not refundable and not transferable, and **expire after 90 days**".
- Card "Google AI Plans": "monthly compute unit allotments for priority access to faster accelerators and more powerful machines" e "uninterrupted background execution and Premium GPU access". O card cobre todos os planos de IA e não separa Pro de Ultra.
- Pro+ tem "Background execution": o notebook "will continue running for up to 24hrs, even if you close your browser".
- "Colab Pro users will see extended execution times and saving of output to Drive based on availability." "Users without a paid subscription should not rely on execution to continue in the background".
- Países com a oferta paga: a lista inclui **Brazil**.

**Relevância para o projeto (inferência)**
- Uma unidade custa R$ 0,58 no pacote de 100 e R$ 0,516 no de 500. Use esses valores para converter unidades em reais.
- A página não diz se as unidades do Google One também vencem em 90 dias. Ver Lacunas.

### [H-5] Blog Google Developers — "Colab is now part of your Google AI plan" (2026-09-22). — [developers.googleblog.com](https://developers.googleblog.com/en/colab-is-now-part-of-your-google-ai-plan/) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- Assinantes dos planos de IA ganham "priority access to faster accelerators and more powerful machines".
- Só para o **AI Ultra**: "uninterrupted background execution and Premium GPU access".
- Para quem já assina o Colab, "there are no changes to your subscription", e os benefícios podem ser somados.
- O post não traz número de unidades, modelos de GPU nem memória.

**Relevância para o projeto (inferência)**
- O AI Pro dá prioridade, mas não dá execução em segundo plano nem "Premium GPU". O treino precisa de checkpoints e retomada.

### [H-6] Cliente web do Colab (configuração e código servidos ao navegador). — [colab.research.google.com/notebooks/pro.ipynb](https://colab.research.google.com/notebooks/pro.ipynb) e o bundle `external_binary.js` que ela carrega de `ssl.gstatic.com` · Primária não documental · Verificado (acesso 2026-11-26, sem login)

**O que diz**
- Chave `user_visible_accelerator_models`: `T4`, `A100`, `G4`, `H100`, `L4`, `V5E1`, `V6E1` (as of 2026-11-26).
- Chave `google_one_eligible_countries`: a lista inclui `BR` (as of 2026-11-26).
- Painel de recursos: o código monta as linhas "Available: N compute units" e "Usage rate: approximately X per hour". Também calcula "At your current usage pre-paid resources may last up to N hours."
- Aviso de upgrade: para recursos de nível Pro o texto é "Upgrade to Google AI Pro"; para recursos de nível Pro+ é "Upgrade to Google AI Ultra".
- Aviso para quem tem Colab Pro e plano de IA: "Your Google AI Plan already includes Colab Pro's compute benefits". O texto sugere cancelar o Colab Pro para evitar cobrança dupla.
- Mensagem de desconexão de assinante Pro: os timeouts são "more lenient", mas a duração segue "not guaranteed or unlimited".

**Relevância para o projeto (inferência)**
- O mapeamento é AI Pro ≈ Colab Pro e AI Ultra ≈ Colab Pro+. Isso confirma H-5: o AI Pro não tem execução em segundo plano.
- Assinar o Colab Pro avulso junto com o AI Pro só soma 100 unidades por R$ 58. É o mesmo preço do Pay As You Go, com renovação automática.

### [H-7] Colab CLI oficial (`google-colab-cli` 0.8.0). — README, SKILL e `colab help` locais · [github.com/googlecolab/google-colab-cli](https://github.com/googlecolab/google-colab-cli) (licença Apache-2.0; último push 2026-11-25) · Primária oficial (projeto da organização `googlecolab`) · Verificado (acesso 2026-11-26)

**O que diz**
- GPUs aceitas em `--gpu`: `T4`, `L4`, `G4`, `H100`, `A100`. TPUs em `--tpu`: `V5E1`, `V6E1`. "Availability varies by Colab subscription tier."
- `--high-mem`: "Requires Colab Pro or Pro+ entitlement". A L4 e as TPUs ignoram a opção, porque têm um só formato.
- `colab usage`: "Show account compute-unit usage rate and balance". O código chama `GET /tun/m/ccu-info` e imprime "Current balance", "Usage rate: X/hr" e "Active assignments".
- `colab run` = `new` + `exec` + `stop`. Ele libera a VM no fim, mesmo se o script falhar. Um caminho de script inexistente falha antes de alocar VM.
- SKILL: "Always `colab stop -s <name>` when done — idle VMs burn compute units." "Accelerator availability is tier-gated; most accounts can only get CPU." Um `400` em `colab new` com acelerador indica falta de cota ou direito.
- SKILL: um valor de `--gpu` desconhecido cai em silêncio para **A100**.
- `colab drivemount` e `colab auth` são interativos: "genuinely require a human at the terminal".
- Doc de sessões do repositório (registro de 2026-09-25): "VM liveness is automatically maintained by the Colab backend based on kernel activity." O CLI não tem mais daemon de keep-alive.
- O README remete aos termos em [tos_v6.html](https://research.google.com/colaboratory/tos_v6.html) (ver H-8).

**Relevância para o projeto (inferência)**
- O "Usage rate" do `colab usage` é da conta, somando as sessões ativas. Para ler a taxa da L4, é preciso ter uma sessão L4 ativa no momento da leitura.
- Um treino longo via `colab exec` mantém o kernel ocupado. A doc diz que isso mantém a VM viva. O teto de duração do H-3 continua valendo. Testar no piloto.
- Sempre passe `--gpu` com grafia exata. Um erro de digitação aloca uma A100 e gasta ~3–5× mais unidades.

### [H-8] Termos Adicionais do Colab, versão 6. — [research.google.com/colaboratory/tos_v6.html](https://research.google.com/colaboratory/tos_v6.html) · Primária oficial · Verificado (acesso 2026-11-26; "Last Modified: August 13, 2026")

**O que diz**
- "You agree to those policies and usage limitations", referindo-se à FAQ (H-3).
- É proibido "share access to your account or use someone else's account". Também é proibido acessar o Colab fora do autorizado e revender acesso a terceiros.
- Na compra pelo Google One, "the Google One Additional Terms of Service also apply".
- Direito de arrependimento para consumidor no Brasil: 14 dias, também "using our support channels".
- Os termos não falam de unidades, de validade nem de uso automatizado.

### [H-9] Issue tracker do Colab no GitHub. — [github.com/googlecolab/colabtools/issues](https://github.com/googlecolab/colabtools/issues) · Primária quanto ao que está escrito; relatos de usuários não são fatos oficiais · Verificado (acesso 2026-11-26, via `gh`)

**O que diz**
- [#6076](https://github.com/googlecolab/colabtools/issues/6076), comentário de 2026-08-10 de uma conta que fala em nome da equipe (associação no GitHub: "NONE"): "H100 and G4(RTX Pro 6000) runtimes are only available to Pro+ users for the time being". O comentário diz que a mudança da H100 deve ser permanente e que a G4 pode voltar ao Pro.
- [#6194](https://github.com/googlecolab/colabtools/issues/6194), relatos de usuários (não oficiais):
  - A100 80 GB de 6,77 para 8,88 unidades/h (as of 2026-10-29).
  - A100 40 GB "close to 7" (as of 2026-10-31).
  - L4 de ~1,6 para 1,94 unidade/h (as of 2026-11-02).
  - G4 "more than 10 units per hour" e A100 8,96 (as of 2026-11-03).
  - "they just increased it again today" (as of 2026-11-24).
  - Nenhuma resposta do Google até o acesso.
- [#6289](https://github.com/googlecolab/colabtools/issues/6289) (aberta em 2026-11-22): assinantes de AI Pro, Pro+ e Pay As You Go relatam L4, A100 e G4 presos em "Allocating" ou com `503`. Um relato diz que as falhas começaram por volta de 2026-11-16. Sem resposta do Google até o acesso.
- [#6193](https://github.com/googlecolab/colabtools/issues/6193) e [#6236](https://github.com/googlecolab/colabtools/issues/6236): respostas que remetem à data de recarga regional (#g1-recurrence) e lembram que testes gratuitos não dão unidades.
- [#6136](https://github.com/googlecolab/colabtools/issues/6136): conta AI Pro bloqueada por "suspected abusive activity". A conta `colaboratory-team` (associação "CONTRIBUTOR") desbloqueou "as a one-time courtesy". [#6269](https://github.com/googlecolab/colabtools/issues/6269) e [#6285](https://github.com/googlecolab/colabtools/issues/6285) relatam bloqueios parecidos, ainda abertos.

**Relevância para o projeto (inferência)**
- Use as taxas de novembro de 2026 como cenário central, não as de março.
- A disponibilidade da L4 e da A100 estava instável na semana do acesso. Planeje o piloto com folga de datas.

---

## 2. Taxa de unidades por hora de cada acelerador

**Não existe tabela oficial de taxas.** A FAQ diz que o Colab não publica limites [H-3]. A página de preços também não traz taxas [H-4]. O responsável vê a taxa em dois lugares:
- **Interface web:** menu do botão de conexão → "View resources" (painel de recursos). Com a sessão conectada, o painel mostra "Usage rate: approximately X per hour" [H-6].
- **CLI:** `colab usage`, com uma sessão do acelerador ativa. Ele mostra "Usage rate: X/hr" [H-7].

### [H-10] McCormick, C. "Colab GPUs Features & Pricing" (post de 2024-04-23, atualizado em março de 2026). — [mccormickml.com](http://mccormickml.com/2024/04/23/colab-gpus-features-and-pricing/) · **Secundária** · Verificado (acesso 2026-11-26)

**O que diz**
- Taxas lidas no painel de recursos em 2026-03-10, no sul da Califórnia (as of 2026-03-10): T4 1,19; L4 1,71; A100 40 GB 5,40; A100 80 GB 7,52; G4 (RTX PRO 6000) 8,71 unidades/h. O autor não conseguiu medir a H100.
- A A100 80 GB sai pelo seletor "High RAM".
- O autor diz que as taxas podem variar com o local e a demanda.

### [H-11] Fastero, "Google Colab GPU: Which GPU You Get…" (2026-11-11). — [fastero.com/blog/google-colab-gpu](https://fastero.com/blog/google-colab-gpu) · **Secundária** (agrega medições de terceiros) · Verificado (acesso 2026-11-26)

**O que diz**
- H100 80 GB: "about 18" unidades/h, com uma única medição (as of 2026-11-11; não abri a medição original).
- G4: "about 8.7 to 8.9" unidades/h. O artigo cita os relatos de alta do #6194.

### [H-12] Post oficial do Colab no LinkedIn sobre a G4. — [linkedin.com/posts/google-colab_…](https://www.linkedin.com/posts/google-colab_we-just-added-support-for-nvidia-g4-rtx-activity-7435739505883619328-G5sp) · Primária oficial (página da empresa "Google Colab") · Verificado (acesso 2026-11-26; o LinkedIn mostra só "8mo")

**O que diz**
- "We just added support for Nvidia G4 (RTX PRO 6000 Blackwell Server Edition) GPUs in Google Colab!"
- "peak rating of 960 BF16 TFLOPS (50% more than the A100-80G) and 96 GB of VRAM".
- A data decodificada do ID do post é 2026-03-06 (inferência).

### Tabela de taxas e memória

| Acelerador | O que é (fonte) | Memória da GPU | Taxa (unidades/h) | Status da taxa |
| --- | --- | --- | --- | --- |
| T4 | NVIDIA T4 [H-13] | 16 GB GDDR6 [H-13] | 1,19 (as of 2026-03-10) [H-10] | Secundária |
| L4 | NVIDIA L4 [H-13] | 24 GB GDDR6 [H-13] | 1,71 (as of 2026-03-10) [H-10]; 1,94 (as of 2026-11-02) [H-9] | Secundária + relato |
| A100 40 GB | A2 Standard [H-13] | 40 GB HBM2 [H-13] | 5,40 (as of 2026-03-10) [H-10]; ~7 (as of 2026-10-31) [H-9] | Secundária + relato |
| A100 80 GB | A2 Ultra [H-13]; sai com "High RAM" [H-10] | 80 GB HBM2e [H-13] | 7,52 (as of 2026-03-10) [H-10]; 8,88–8,96 (as of 2026-11-03) [H-9] | Secundária + relato |
| G4 | NVIDIA RTX PRO 6000 Blackwell Server Edition [H-12, H-9] | 96 GB GDDR7 [H-12, H-13] | 8,71 (as of 2026-03-10) [H-10]; >10 (as of 2026-11-03) [H-9] | Secundária + relato |
| H100 | NVIDIA H100 [H-7] | 80 GB HBM3 nas VMs A3 [H-13]; variante do Colab NÃO VERIFICADA | ~18 (as of 2026-11-11) [H-11] | Secundária, uma medição |
| TPU v5e-1 / v6e-1 | TPUs do Google [H-6, H-7] | NÃO VERIFICADO | NÃO VERIFICADO | — |

- **Acesso pelo AI Pro:** nenhuma fonte primária lista as GPUs por plano. H100 e G4 ficaram só para Pro+ desde agosto de 2026 [H-9]. O AI Ultra ganha "Premium GPU access" [H-5]. Leitura provável (inferência): o AI Pro acessa T4, L4 e A100. A G4 e a H100 ficam fora. **Confirmar na conta.**
- **TPUs:** a stack do projeto (TRL + vLLM em CUDA) não roda nelas sem trabalho extra (inferência). Não as considerei.

---

## 3. Qual acelerador rende mais trabalho por unidade

**Dados medidos:** não encontrei nenhuma medição publicada de GRPO com vLLM e LoRA no Gemma 4 E4B em GPUs do Colab. O único número de vazão do Gemma 4 em L4 é o do E2B quantizado, num post comunitário, citado na nota F. Tudo abaixo é **inferência** a partir de especificações e taxas.

### [H-13] Google Cloud — GPU machine types. — [docs.cloud.google.com/compute/docs/gpus](https://docs.cloud.google.com/compute/docs/gpus) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- "G4 (RTX PRO 6000) | 96 GB GDDR7 (1.597 TBps)".
- "A3 Mega, A3 High, A3 Edge (H100) | 80 GB HBM3 (3.35 TBps)".
- "A2 Standard (A100 40GB) | 40 GB HBM2 (1.6 TBps)"; "A2 Ultra (A100 80GB) | 80 GB HBM2e (1.9 TBps)".
- "G2 (L4) | 24 GB GDDR6 (300 GBps)"; "N1 (T4) | 16 GB GDDR6 (320 GBps)".

### [H-14] NVIDIA — páginas de especificação. — [A100](https://www.nvidia.com/en-us/data-center/a100/) · [H100](https://www.nvidia.com/en-us/data-center/h100/) · [RTX PRO 6000 Server](https://www.nvidia.com/en-us/data-center/rtx-pro-6000-blackwell-server-edition/) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- A100: BF16 "312 TFLOPS | 624 TFLOPS*", com "* With sparsity".
- H100 SXM: "BFLOAT16 Tensor Core* | 1,979 teraFLOPS", com "* With sparsity".
- RTX PRO 6000 Server: "FP16 | BF16 Tensor Core" "1 PFLOP". A página não diz se o valor usa esparsidade.
- L4: 121 TFLOPS BF16 denso (dado da nota F, da página oficial da NVIDIA; não reaberta).

### [H-15] TRL — vLLM Integration (docs `main`). — [huggingface.co/docs/trl/main/en/vllm_integration](https://huggingface.co/docs/trl/main/en/vllm_integration) · Primária oficial (documentação) · Verificado (acesso 2026-11-26)

**O que diz**
- Modo colocate: "vLLM runs inside the trainer process and shares GPU memory with the training model". Isso "may lead to memory contention".
- O modo server exige "separate CUDA devices".
- "To reduce GPU memory usage when running vLLM, consider enabling vLLM sleep mode."
- A doc aceita vLLM "from `0.23.0` to `0.34.x`".

### Comparação por unidade (toda a tabela é inferência)

Cada passo de GRPO tem duas partes de peso parecido, segundo a nota F: a geração, limitada pela banda de memória, e a atualização, limitada pelo cálculo. Por isso a tabela mostra as duas razões.

| Acelerador | Banda / (unid./h) | TFLOPS BF16 denso / (unid./h) | Ganho de velocidade suposto vs L4 | Trabalho por unidade vs L4 |
| --- | --- | --- | --- | --- |
| L4 | 155–175 | 62–71 | 1× | **1,0** |
| A100 40 GB | 229–296 | 45–58 | 2,5–3,5× | 0,69–1,11 |
| A100 80 GB | 213–253 | 35–41 | 2,5–4× | 0,54–0,91 |
| G4 | 160–183 | 48–55 (se o denso for ~480) | 3–4× | 0,58–0,79 |
| H100 | 186 | 55 (989 denso) | 4–7× | 0,38–0,75 |
| T4 | — | — | não serve | — |

- **Como calculei:**
  - Usei as taxas de março e de novembro da tabela anterior.
  - O "ganho de velocidade" é menor que a razão das especificações. Com G = 8 e 8 prompts por passo, há pouca concorrência. As chamadas de ferramenta e o Python também têm custo fixo.
  - O BF16 denso da G4 (~480) é inferência. O pico de 960 do post é 1,54× o pico com esparsidade da A100 (624), não o denso (312).
- **Conclusão (inferência):**
  - A **L4 rende mais trabalho por unidade**, com a A100 40 GB perto dela.
  - G4 e H100 rendem ~20% a 60% menos trabalho por unidade. Elas só ganham em tempo de relógio. Além disso, provavelmente nem estão disponíveis no AI Pro [H-9].
  - A T4 fica fora: tem 16 GB e não tem BF16 (nota F).
- **Risco de memória na L4 (inferência a medir no piloto):**
  - O E4B tem ~8B parâmetros com embeddings. Em BF16, são ~16 GB de pesos.
  - No modo colocate, o vLLM e o trainer dividem a GPU [H-15]. Se cada um carregar uma cópia, a soma passa de 24 GB.
  - Saídas possíveis: sleep mode do vLLM, base do trainer em 4-bit, ou `vllm_gpu_memory_utilization` baixo.
  - Se nada disso couber, a A100 40 GB vira a opção mais barata que cabe. Nas taxas recentes, ela rende até ~30% menos por unidade, mas é ~3× mais rápida no relógio.

---

## 4. Armazenamento

### [H-16] Ajuda do Google Drive — arquivos que você pode guardar. — [support.google.com/drive/answer/37603](https://support.google.com/drive/answer/37603?hl=en) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- "All other files": "Up to 5 TB" por arquivo. A página não fala de limite diário de upload.

### [H-17] Google Workspace — Storage and upload limits. — [knowledge.workspace.google.com](https://knowledge.workspace.google.com/admin/drive/storage-and-upload-limits-for-google-workspace?hl=en) · Primária oficial, **só para contas Workspace** · Verificado (acesso 2026-11-26)

**O que diz**
- "Each user can upload and copy 750 GB to Drive within 24 hours." "Files larger than 750 GB can't be copied."
- A página não diz se o limite vale para contas pessoais. Para a conta pessoal do responsável: **NÃO VERIFICADO**.

### O que vale para o projeto

- **Espaço:** o AI Pro dá 5 TB (as of 2026-11-26) [H-1]. A ajuda fala em "5 TB or 10 TB" conforme o plano [H-2]. Um adaptador LoRA de rank 16 e os checkpoints do otimizador ficam na ordem de dezenas a centenas de MB (inferência). O espaço não é o gargalo.
- **Cuidados ao montar o Drive no Colab** [H-3]:
  - Pastas com muitos itens fazem o `drive.mount()` dar timeout. A FAQ fala em ~10 mil itens na raiz e pede no máximo 10 mil itens por pasta.
  - O Drive tem cotas de operações e de banda por usuário e por arquivo. Estourar a cota dá `OSError: [Errno 5] Input/output error`. A FAQ recomenda copiar um `.zip` ou `.tar.gz` para a VM e descompactar lá.
  - O Drive pode estar numa região distante da VM. A FAQ pede poucas leituras e escritas.
  - Uma movimentação interrompida dentro do Drive montado "may lose all of the data in transit".
  - Montar o Drive dá ao código do notebook acesso a **todos** os arquivos do Drive.
  - O Drive não monta em runtime local, GCP Marketplace nem Colab Enterprise.
- **Pelo CLI:** `colab drivemount` é interativo e exige uma pessoa no terminal [H-7].
- **Recomendação (inferência):**
  - Grave os checkpoints no disco da VM (`/content`).
  - A cada N passos, copie um arquivo compactado para o Drive. Ou baixe para o Mac com `colab download`.
  - Não guarde logs reais confidenciais no mesmo Drive que o notebook monta.

---

## 5. Outros benefícios do AI Pro úteis ao projeto

### [H-18] Google Developer Program — Benefits FAQ. — [developers.google.com/profile/help/benefits](https://developers.google.com/profile/help/benefits) · Primária oficial · Verificado (acesso 2026-11-26; sem data na página)

**O que diz**
- Os créditos mensais são de US$ 10, 40 ou 100, conforme o plano. O AI Pro recebe **US$ 10** (as of 2026-11-26).
- Os créditos servem para "usage of Google Cloud and Google Maps Platform products, including the Gemini API, Google AI Studio, Firebase", com as exclusões padrão de créditos promocionais.
- "Monthly Google Cloud credits expire one year after the date they are granted."
- Os planos com IA do Google One são agora o único caminho para o nível premium do Google Developer Program.

### [H-19] Blog do Google — "New developer tools for Google AI Pro and Ultra subscribers" (2026-01-27). — [blog.google](https://blog.google/innovation-and-ai/technology/developers-tools/gdp-premium-ai-pro-ultra/) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- "$10 per month in Google Cloud credits for Google AI Pro subscribers". O uso citado é Vertex AI, Cloud Run e Gemini API.

### [H-20] Blog do Google — "Claim your Google Cloud Credits in Google AI Studio" (2026-11-13). — [blog.google](https://blog.google/innovation-and-ai/technology/developers-tools/google-cloud-credits-gdp-ai-studio/) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- Usar a Gemini API com faturamento do Cloud "requires a **$5 minimum prepayment** and balance in order to draw down promotional credits".
- "Grants stack month to month." "Each monthly credit is valid for 12 months from issue."

### [H-21] Gemini API Additional Terms of Service. — [ai.google.dev/gemini-api/terms](https://ai.google.dev/gemini-api/terms) · Primária oficial · Verificado (acesso 2026-11-26; "Effective March 23, 2026")

**O que diz**
- O uso é "for professional or business purposes, not for consumer use".
- "**You may not use the Services to develop models that compete with the Services**".
- Serviços não pagos: "human reviewers may read, annotate, and process your API input and output." "**Do not submit sensitive, confidential, or personal information to the Unpaid Services.**"
- Serviços pagos: "Google doesn't use your prompts … or responses to improve our products". A Gemini API só é paga "when accessing the API through a Cloud Project associated with an active billing account."

### [H-22] Gemini CLI — cotas, termos e modo headless. — [quota-and-pricing](https://www.geminicli.com/docs/resources/quota-and-pricing.md) · [tos-privacy](https://www.geminicli.com/docs/resources/tos-privacy.md) · [headless](https://www.geminicli.com/docs/cli/headless.md) · Primária oficial (docs do projeto Google) · Verificado (acesso 2026-11-26; sem data nas páginas)

**O que diz**
- Com login Google: "Google AI Pro | 1,500 requests" por usuário por dia (as of 2026-11-26). "Requests are limited per user per minute".
- Termos com AI Pro: "Google Terms of Service, Google One Additional Terms of Service and Google Privacy Policy".
- Acessar o backend do Gemini CLI com software de terceiros "is a violation of applicable terms and policies" e pode suspender a conta.
- Modo headless: "Headless mode provides a programmatic interface to Gemini CLI", ativado por `-p` ou fora de um TTY, com saída JSON.

### [H-23] Gemini Code Assist — Quotas. — [docs.cloud.google.com/gemini/docs/quotas](https://docs.cloud.google.com/gemini/docs/quotas) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- "Quotas for requests from Gemini Code Assist agent mode and Gemini CLI are combined." Ao atingir o limite diário, nenhuma requisição passa até a cota renovar.
- A página não traz a linha do AI Pro. O número de 1.500 vem de H-22.

### [H-24] Jules — Limits and Plans. — [jules.google/docs/usage-limits](https://jules.google/docs/usage-limits/) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- "Jules in Pro": 100 tarefas por 24 h móveis e 15 tarefas simultâneas (as of 2026-11-26). "We may adjust limits and features".
- A página cita "Gemini 3 Pro" como modelo. Parece desatualizada em relação à página de planos (H-1).

### [H-25] Termos de Serviço do Google. — [policies.google.com/terms](https://policies.google.com/terms?hl=en-US) · Primária oficial · Verificado (acesso 2026-11-26; "Effective July 30, 2026"; "Country version: Brazil")

**O que diz**
- Na lista do que não se deve fazer: "**using AI-generated content from our services to develop machine learning models or related AI technology**".
- Também proíbe acesso automatizado que viole as instruções legíveis por máquina das páginas, como o `robots.txt`.

### [H-26] Termos Adicionais do Google One. — [one.google.com/terms-of-service](https://one.google.com/terms-of-service?hl=en) · Primária oficial · Verificado (acesso 2026-11-26; "Last Modified: October 1, 2026")

**O que diz**
- Cada benefício extra segue os termos do próprio serviço. Assim, as unidades do Colab seguem os termos do Colab (H-8).

### Tabela de benefícios e uso automatizado

Não faço interpretação jurídica. A coluna "Uso automatizado" só cita o que os termos dizem. A decisão é do responsável.

| Benefício (as of 2026-11-26) | O que dá ao AI Pro | Uso automatizado, por exemplo um juiz em lote | Trecho dos termos |
| --- | --- | --- | --- |
| **Créditos do Google Cloud** [H-18, H-19, H-20] | US$ 10/mês; valem 12 meses; exigem pré-pagamento de US$ 5 para a Gemini API | É uso pago e programático por desenho. A Gemini API é uma API. | Gemini API: "You may not use the Services to develop models that compete with the Services" [H-21] |
| **Gemini API paga** (com os créditos) [H-21] | Cobrança por token, descontada dos créditos | Permitido como API. Com faturamento ativo, os prompts não treinam modelos do Google. | "Google doesn't use your prompts … or responses to improve our products" [H-21] |
| **Gemini API sem pagar / AI Studio grátis** [H-21] | Cota grátis; AI Studio com limites maiores para o AI Pro [H-2] | API automatizável. Mas há revisão humana dos dados. Não envie logs reais. | "Do not submit sensitive, confidential, or personal information to the Unpaid Services" [H-21] |
| **Gemini CLI** [H-22] | 1.500 req/dia | O modo headless existe e é documentado. Os termos são os de consumidor (Google + Google One). | "using AI-generated content from our services to develop machine learning models or related AI technology" [H-25]; acesso por ferramenta de terceiros com o OAuth do CLI é violação [H-22] |
| **Gemini Code Assist** [H-2, H-23] | Cota maior, a mesma do CLI | Ferramenta de IDE. Não serve para lote. | Mesmos termos do CLI [H-22] |
| **Jules** [H-24] | 100 tarefas/dia, 15 simultâneas | A página não fala de API nem de automação. **NÃO VERIFICADO.** | — |
| **Antigravity** [H-1, H-2] | Limites maiores | IDE agêntica. Termos próprios **NÃO VERIFICADOS**. | — |
| **Gemini Notebook** [H-1] | Limites maiores | Ferramenta de consumidor, sem API. Útil para ler artigos. | Termos de consumidor [H-25] |
| **Firebase Studio** [H-2] | 30 workspaces | Pouca relevância para o projeto. | — |
| **Horas extras de GPU no Kaggle** [H-27] | Colab Pro ganha +15 h/semana; Pro+ ganha +30 h/semana | Não consome unidades do Colab. Se o AI Pro conta como "Colab Pro": **NÃO VERIFICADO**. | "Kaggle reserves the right to end or suspend the Promotion at any time" [H-27] |

**Leitura para o projeto (inferência)**
- A nota F já recomenda recompensa 100% por regras, sem LLM-juiz no treino. Isso evita o risco da cláusula do H-25.
- Se o responsável quiser um juiz só para avaliação, o caminho mais limpo é a **Gemini API paga** com os créditos. Ela é uma API, os dados não treinam modelos do Google e não há a cláusula ampla do H-25. A cláusula de "modelos que competem" do H-21 continua lá. Não a interpreto.
- Não use o Gemini CLI com login AI Pro para gerar rótulos, recompensas ou dados de treino.

---

## 6. Alternativas gratuitas para complementar

### [H-27] Kaggle Notebooks — documentação. — [kaggle.com/docs/notebooks](https://www.kaggle.com/docs/notebooks) · [efficient-gpu-usage](https://www.kaggle.com/docs/efficient-gpu-usage) · [tpu](https://www.kaggle.com/docs/tpu) · Primária oficial · Verificado (acesso 2026-11-26, navegador sem login)

**O que diz**
- Sessão: 12 h para CPU e GPU; 9 h para TPU.
- Disco: "20 Gigabytes of auto-saved disk space (/kaggle/working)".
- GPUs: "1 Nvidia Tesla P100 GPU" ou "2 Nvidia Tesla T4 GPUs", com 29 GB de RAM. TPU v3-8.
- Cota de GPU (as of 2026-11-26): renova toda semana e "is 30 hours or sometimes higher". Cota de TPU: até 20 h por semana e até 9 h por sessão.
- Inatividade: "20 minutes of idle time for your interactive session" (página de specs). A página de GPU diz "60 minute idle timeout limit". As duas páginas divergem.
- "Save & Run All" roda o notebook numa sessão separada, em segundo plano, até 12 h.
- Promoção experimental: Colab Pro ganha +15 h e Pro+ ganha +30 h de GPU por semana no Kaggle. "These extra GPU hours don't consume your Colab compute units."

### [H-28] Amazon SageMaker Studio Lab — FAQ. — [studiolab.sagemaker.aws/faq](https://studiolab.sagemaker.aws/faq) · Primária oficial · Verificado (acesso 2026-11-26, navegador; WebFetch recebeu 403)

**O que diz**
- GPU: no máximo 4 h por sessão e 4 h por 24 h. A GPU roda em "G4dn.xlarge instances" (as of 2026-11-26).
- "15 GB of persistent storage and 16 GB of RAM."

### [H-29] Lightning AI — Pricing. — [lightning.ai/pricing](https://lightning.ai/pricing) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- Grátis: até 30 créditos (5 no cadastro e mais 25 com cartão), "~50 GPU hours on interruptible machines". Os créditos vencem em 12 meses. Os Studios gratuitos reiniciam a cada 4 h (as of 2026-11-26).

### [H-30] Modal — Pricing. — [modal.com/pricing](https://modal.com/pricing) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- Plano Starter: "$30 / month free credits", em vigor desde 2026-09-01. Preços **por segundo** (as of 2026-11-26): L4 US$ 0,000222; A100 40 GB US$ 0,000583; A100 80 GB US$ 0,000694; H100 US$ 0,001097; RTX PRO 6000 US$ 0,000842. Por hora, isso dá cerca de US$ 0,80 na L4, US$ 2,10 na A100 40 GB e US$ 2,50 na A100 80 GB. CPU e memória do contêiner são cobrados à parte.
- **Correção de 26/11/2026:** a primeira versão desta ficha leu os preços como valores por hora. Conferido na página, que diz "/ sec".

### [H-31] Google Cloud — Free Program. — [docs.cloud.google.com/free/docs/free-cloud-features](https://docs.cloud.google.com/free/docs/free-cloud-features) · Primária oficial · Verificado (acesso 2026-11-26)

**O que diz**
- Teste grátis: "$300 in free Welcome credit which is valid for 90 days". Durante o teste não se pode "Add GPUs to your VM instances". "GPUs and TPUs are not included in the Free Tier offer."

### Tabela de alternativas

| Opção | Cota gratuita (as of 2026-11-26) | GPU | Limite de sessão | Uso para o projeto (inferência) |
| --- | --- | --- | --- | --- |
| **Colab grátis** [H-3, H-4] | Não publicada; o painel fala em "daily free of charge resource allowance" [H-6] | "very limited access to GPUs" [H-4] | Até 12 h; SSH, desktop remoto e UI web proibidos [H-3] | Testes rápidos de código. Não serve para GRPO. |
| **Kaggle** [H-27] | 30 h/semana de GPU; 20 h/semana de TPU | P100 16 GB ou 2× T4 | 12 h por sessão; "Save & Run All" roda sem navegador | Avaliação em lote, pré-processamento, smoke tests em fp16. As 2× T4 permitem o modo server do TRL (vLLM numa GPU, treino na outra). O E4B em 16 bits não cabe em 16 GB. |
| **SageMaker Studio Lab** [H-28] | 4 h de GPU por 24 h | G4dn.xlarge | 4 h | Pouco útil: sessões curtas demais. |
| **Lightning AI** [H-29] | ~30 créditos, únicos, não mensais | Várias; A100 e H100 com sessão de 4 h | 4 h nos Studios grátis | Um teste pontual de vazão. |
| **Modal** [H-30] | US$ 30/mês | L4, A100, H100, RTX PRO 6000 | Cobrança por segundo | US$ 30 ≈ 37 h de L4 ou 14 h de A100 40 GB por mês, antes do custo de CPU e memória (inferência). Exige código adaptado ao Modal. |
| **Google Cloud (teste)** [H-31] | US$ 300 por 90 dias | **Nenhuma** no teste | — | Não serve para GPU. |

---

## 7. Regras de uso do Colab que afetam treinos longos

- **Proibido em qualquer runtime gerenciado** [H-3, #disallowed-activities]:
  - hospedar arquivos ou servir mídia e serviços web sem relação com computação interativa;
  - torrents e P2P;
  - "connecting to remote proxies";
  - mineração de criptomoeda;
  - ataques de negação de serviço;
  - "password cracking";
  - "using multiple accounts to work around access or resource usage restrictions";
  - deepfakes;
  - "employing techniques such as containerization to circumvent anti-abuse policies".
- **Proibido sem saldo positivo**, com risco de encerramento "at any time without warning" [H-3]:
  - "remote control such as SSH shells, remote desktops";
  - "bypassing the notebook UI to interact primarily via a web UI";
  - "running distributed computing workers".
- **Contas:** os termos proíbem compartilhar a conta ou usar a de outra pessoa [H-8]. A FAQ proíbe usar várias contas para driblar limites [H-3].
- **Inatividade e duração:**
  - Os valores não são publicados [H-3].
  - Com assinatura, os timeouts são "more lenient", mas "not guaranteed or unlimited" [H-6].
  - O teto geral é de 12 h [H-3]. Execução em segundo plano por até 24 h só no Pro+ [H-4], e no AI Ultra pelo post [H-5].
- **Saldo zerado:** a conta volta às regras gratuitas e a sessão pode cair [H-3].
- **Bloqueios automáticos:** há relatos de assinantes AI Pro bloqueados por "suspected abusive activity". Num caso, o próprio usuário atribui o bloqueio a um app de desktop remoto ativo junto com a sessão [H-9].
- **Leitura para o projeto (inferência):**
  - O `colab ssh` do CLI usa SSH. Com saldo zero, isso cai na lista do que é proibido no nível gratuito. **Mantenha saldo positivo** ao usar o CLI.
  - O laço do GRPO roda localmente na VM. O Ambiente de treino é replay local e não precisa de proxy nem de servidor web exposto. O vLLM em modo colocate roda dentro do processo do trainer [H-15]. Nada disso está na lista de proibições.
  - Não exponha o vLLM nem um painel web por túnel para fora da VM.
  - Não divida o treino entre contas.

---

## 8. Recomendações para o orçamento (inferência)

1. **Use a L4 como padrão e meça antes de gastar.**
   - No piloto, leia a taxa real com `colab usage` com a sessão L4 ativa.
   - Meça também o pico de memória do E4B com vLLM colocate e os tokens/s.
   - Se não couber em 24 GB, passe para a A100 40 GB. Evite G4 e H100: custam mais por trabalho e provavelmente não estão no AI Pro.
2. **Não deixe VM ociosa e prepare a retomada.**
   - Use `colab run` (libera a VM sozinho) ou `colab stop` ao fim de cada etapa.
   - Salve checkpoint a cada ~30–60 min. O AI Pro tem teto de ~12 h por sessão e não tem execução em segundo plano.
   - Mantenha o saldo positivo durante as sessões.
3. **Orce em unidades, com margem de 25–50% para altas de taxa.**
   - O plano completo na L4 custa ~120–170 unidades. Os 200 mensais do AI Pro cobrem isso.
   - Se faltar, 100 unidades custam R$ 58,00 (as of 2026-11-26). O pacote de 500 sai a R$ 0,516 por unidade.
   - As taxas da L4 e da A100 subiram de 13% a 30% entre março e novembro de 2026 [H-9, H-10].
4. Teste se a conta ganha as horas extras do Kaggle: Kaggle → File → "Link to Colab" [H-27]. Use o Kaggle para avaliação e pré-processamento, que não precisam de BF16.
5. Não assine o Colab Pro avulso. Ele dá 100 unidades por R$ 58,00/mês, o mesmo preço do Pay As You Go, e vira cobrança recorrente [H-4, H-6].

---

## Custo estimado do plano de execução (toda a seção é inferência)

**Suposições**
- **S1. Época:** 1.000 alertas × 8 trajetórias ≈ **7,5 h na L4** (faixa de 5 a 11 h). É a estimativa interna da nota F, não uma medida.
- **S2. Piloto:** ~1.000 trajetórias (125 prompts × 8) mais instalação e aquecimento do vLLM ≈ 2 h (faixa de 1 a 3 h).
- **S3. Política principal:** 2 épocas, ≈ 300 passos de 8 prompts, o mínimo sugerido na nota F ≈ 15 h (faixa de 10 a 22 h).
- **S4. Controle com recompensa embaralhada:** mesmo orçamento da principal, para ser um controle justo.
- **S5. Políticas de peso fixo:** cada uma custa o mesmo que a principal.
- **S6. Folga de 15%:** instalação, avaliações na validação (~3–5 min cada na L4), retomadas e ociosidade.
- **S7. Taxas:** "antiga" = março de 2026 [H-10]; "recente" = relatos de outubro e novembro de 2026 [H-9, H-11]. Ganhos de velocidade como na seção 3.
- **S8. Preço:** R$ 0,58 por unidade, o pacote de 100 do Pay As You Go (as of 2026-11-26) [H-4].

**Tabela A — por rodada, na L4**

| Rodada | Horas de L4 (central; faixa) | Unidades a 1,71/h | Unidades a 1,94/h | Sessões de até 12 h |
| --- | --- | --- | --- | --- |
| Piloto | 2 (1–3) | 3,4 | 3,9 | 1 |
| Política principal | 15 (10–22) | 25,6 | 29,1 | 2 |
| Controle com recompensa embaralhada | 15 (10–22) | 25,6 | 29,1 | 2 |
| 2 políticas de peso fixo | 30 (20–44) | 51,3 | 58,2 | 3–4 |
| 3ª política de peso fixo (se sobrar saldo) | 15 (10–22) | 25,6 | 29,1 | 2 |
| **Total com 2 fixas + folga de 15%** | **71 (47–105)** | **122** | **138** | ~6–9 |
| **Total com 3 fixas + folga de 15%** | **89 (59–130)** | **151** | **172** | ~8–11 |

**Tabela B — plano completo por acelerador**

| Acelerador | Ganho vs L4 (suposto) | Horas, 2 fixas | Unidades, 2 fixas (antiga–recente) | Horas, 3 fixas | Unidades, 3 fixas (antiga–recente) | Faixa extrema de unidades | Meses de AI Pro (200/mês) | R$ se tudo fosse Pay As You Go |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **L4** | 1× | 71 | **122–138** | 89 | **151–172** | 81–252 | **0,6–0,9** | R$ 71–100 |
| A100 40 GB | 3× (2,5–3,5) | 24 | 128–166 | 30 | 159–207 | 73–364 | 0,6–1,0 | R$ 74–120 |
| A100 80 GB | 3,25× (2,5–4) | 22 | 165–195 | 27 | 205–242 | 89–463 | 0,8–1,2 | R$ 96–140 |
| G4 (provável só Pro+/Ultra) | 3,5× (3–4) | 20 | 177–204 | 25 | 220–253 | 103–433 | 0,9–1,3 | R$ 103–147 |
| H100 (só Pro+, segundo H-9) | 5,5× (4–7) | 13 | 233 | 16 | 290 | 121–585 | 1,2–1,5 | R$ 135–168 |
| T4 | não serve (16 GB, sem BF16) | — | — | — | — | — | — | — |

**Leitura**
- Com 200 unidades/mês, o AI Pro dá ~103–117 h de L4 ou ~29–37 h de A100 40 GB por mês, nas taxas da tabela.
- O plano completo na L4 cabe num mês de AI Pro, mesmo no cenário central com 3 políticas de peso fixo. A faixa extrema (até ~250 unidades) pede um segundo mês ou ~R$ 30 de Pay As You Go.
- A faixa é larga porque a S1 não foi medida. O piloto deve trocar a S1 por um número medido antes da política principal.

---

## Lacunas

Itens que só o responsável vê na conta, e onde ver cada um:

| Lacuna | Onde ver |
| --- | --- |
| **Saldo atual de unidades** | Colab web: menu do botão de conexão → "View resources" mostra "Available: N compute units" [H-6]. Ou `colab usage` → "Current balance" [H-7]. Em 26/11/2026, o responsável autorizou o CLI por OAuth no terminal e leu o saldo. O valor fica fora deste repositório público. |
| **Taxa real de cada acelerador na conta** | Com uma sessão do acelerador ativa: painel de recursos ("Usage rate: approximately X per hour") ou `colab usage` ("Usage rate: X/hr"). Leia e pare a sessão logo em seguida [H-6, H-7]. |
| **Quais GPUs o AI Pro libera** | Colab web: Runtime → Change runtime type. As opções sem direito aparecem esmaecidas [H-9]. Pelo CLI, um `400` em `colab new --gpu X` indica falta de direito, mas a tentativa pode alocar uma VM [H-7]. |
| **Se a assinatura AI Pro é paga e não de teste** | one.google.com → plano atual; Colab → Settings → Subscription [H-3]. |
| **Data da recarga mensal das 200 unidades** | Segue a data de início do plano ou a data regional de migração (América do Sul: 10 de setembro) [H-3]. Confira o saldo no painel de recursos perto dessa data. |
| **Se as unidades do Google One vencem em 90 dias** | NÃO VERIFICADO. A regra de 90 dias está escrita para Pay As You Go, Pro e Pro+ [H-4]. Observe o saldo após 90 dias ou pergunte ao suporte do Colab. |
| **Duração máxima e timeout por inatividade na conta** | Não publicados [H-3]. Meça no piloto: rode um `colab exec` longo sem navegador aberto e registre quando a VM cai. |
| **Se o E4B em BF16 + vLLM colocate cabe na L4** | Medir no piloto com `nvidia-smi` dentro da VM [H-7, H-15]. |
| **Créditos de US$ 10/mês do Cloud** | developers.google.com/profile → Benefits, ou o diálogo de créditos do AI Studio. Exigem perfil do Google Developer Program, conta de faturamento e pré-pagamento de US$ 5 para a Gemini API [H-18, H-20]. |
| **Horas extras do Kaggle para quem tem AI Pro** | Kaggle → File → "Link to Colab"; depois Settings → cotas [H-27]. NÃO VERIFICADO se o AI Pro conta como "Colab Pro". |
| **Cota restante do Gemini CLI** | NÃO VERIFICADO. A documentação não mostra como consultar. |
| **Espaço livre no Drive** | one.google.com → Armazenamento [H-1]. |
| **Limite diário de upload do Drive em conta pessoal** | NÃO VERIFICADO. Só achei a regra de 750 GB/dia para contas Workspace [H-17]. |
| **Taxa da H100 e variante da H100 no Colab** | Só uma medição secundária (~18/h) [H-11]. Fonte primária: NÃO VERIFICADO. |
| **Memória e taxa das TPUs v5e-1 e v6e-1 no Colab** | NÃO VERIFICADO. Fora da stack CUDA do projeto. |
| **Estado da alocação de L4, A100 e G4** | Relatos de falha desde ~16/11/2026, sem resposta oficial até 2026-11-26 [H-9]. Acompanhe a [#6289](https://github.com/googlecolab/colabtools/issues/6289) antes de marcar o piloto. |
