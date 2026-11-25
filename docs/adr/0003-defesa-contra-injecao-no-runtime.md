---
status: accepted
---

# A defesa contra injeção de prompt fica no Runtime, não no modelo

Em 25/11/2026, o responsável pelo estudo decidiu que a garantia contra injeção de prompt no Guardião vem de regras
determinísticas do Runtime agêntico, não do fine-tuning. O Registro de um Recorte é conteúdo que
o atacante controla: User-Agent, URI, linha de comando, nome de usuário. A literatura mostra três
coisas:

- Nenhum modelo avaliado separa bem instrução de dados (Zverev et al., ICLR 2025).
- Injeção passiva em logs de SOC chegou a 88,2% de sucesso (Karanjai et al., USENIX Security
  2026).
- Ataques adaptativos quebram defesas por fine-tuning com mais de 90% de sucesso (Nasr et al.,
  USENIX Security 2026).

Os pesos do Gemma são públicos, então o atacante pode otimizar contra a base.

Por isso o Projetor marca um Sinal antes do modelo, por regra versionada. Quando o Recorte tem
Sinal e o Relato não é Alerta, o Rebaixamento só vale se alguma Evidência do Relato estiver
literalmente no Contexto. Caso contrário, o caso vai para revisão humana. O Runtime também segue
três regras fixas:

- Nunca fecha sozinho um Recorte incompleto.
- Nunca usa o rationale como gatilho de regra.
- O Projetor escapa no Registro os delimitadores reservados de Contexto e Registro.

## Considered Options

- **Confiar no fine-tuning com Mutações de injeção, no estilo StruQ e SecAlign.** Rejeitada como
  garantia e mantida como reforço. Defesas por treino caem sob ataque adaptativo e de caixa-branca.
- **Exigir Contexto para todo Veredito benigno.** Rejeitada. A maioria dos logs benignos não tem
  Contexto, e o Runtime mandaria quase tudo para um humano.
- **Detectar injeção com um segundo LLM.** Rejeitada. Ele herda o mesmo problema, e a
  autoverificação no mesmo contexto piorou a triagem em ALERT-BENCH (Tsegai et al., 2026,
  preprint).

## Consequences

- Uma injeção pode mudar o Relato, mas não apaga o Sinal. Sem Sinal, o dano máximo é rebaixar um
  Recorte que nenhuma regra marcou. A Suíte adversarial mede esse resíduo nas duas direções.
- A qualidade das regras de Sinal entra no resultado. Regras estreitas deixam passar
  Rebaixamentos; regras largas mandam mais casos para humanos. O artigo reporta a taxa de
  encaminhamento junto do FPR.
- Zero rebaixamentos na suíte estática é um gate de regressão. Qualquer alegação de robustez
  exige a fase adaptativa.

## Emenda de 25/11/2026

Com o ADR 0004, o Guardião passa a chamar Ferramentas de leitura. O que a ferramenta calcula,
como contagens, horários e a estrutura de uma árvore de processos, conta como Contexto. O texto
que ela copia do log conta como Registro. Um Rebaixamento pode citar campos calculados pelas
ferramentas. O Runtime escapa os tokens reservados de chamada e de resposta de ferramenta do
template do Gemma 4 que aparecerem dentro dos logs, antes que cheguem ao modelo.
