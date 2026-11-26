---
status: accepted
---

# O Guardião investiga com Ferramentas de leitura e roda na máquina monitorada

Em 25/11/2026, o responsável pelo estudo decidiu que o próprio Guardião recebe Ferramentas de
leitura específicas, em vez de criar um segundo agente investigador. O Runtime agêntico roda
localmente nas máquinas monitoradas e envia os Relatos ao SOC. Um único artigo cobre o
fine-tuning, as ferramentas e a otimização por RL com recompensa que pesa custo contra FPR.

O Guardião continua relatando e nunca agindo. As ferramentas só leem logs locais, são
determinísticas e não mudam o sistema. A contenção continua saindo de regras, com aprovação
humana.

## Considered Options

- **Dois agentes: o Guardião de passada única e um Investigador com ferramentas.** Rejeitada.
  Aumenta a pipeline e obriga a manter dois contratos e dois treinos.
- **Investigador central no SOC, consultando o SIEM.** Rejeitada. O alvo é rodar perto dos
  dados, na máquina, e mandar ao SOC só o resultado.
- **Linguagem de consulta livre ou genérica.** Rejeitada a favor de um catálogo de ferramentas
  específicas, que é mais fácil de validar, de ensinar no SFT e de pontuar no RL.

## Consequences

- O Guardião v2 sem ferramentas continua como Comparador: é o ponto de custo zero de
  ferramentas da mesma política.
- O SFT passa a ensinar trajetórias com chamadas de ferramenta, e o RL otimiza quando chamar.
- O que volta das ferramentas entra no Relato como entrada não confiável, salvo regra explícita
  sobre campos calculados pela própria ferramenta.
- O Runtime precisa de inferência local nas máquinas-alvo, e o desempenho tem de ser medido
  nelas, não só no Mac do laboratório.
- O ADR 0003 continua valendo: as regras de Sinal e Rebaixamento se aplicam ao Relato final.
