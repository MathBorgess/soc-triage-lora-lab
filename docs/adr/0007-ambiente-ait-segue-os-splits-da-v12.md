---
status: accepted
---

# O ambiente sobre o AIT-LDSv2 segue os splits da v12

Em 26/11/2026, o responsável pelo estudo aceitou dois ambientes para o RL: o Ambiente de treino
da v12 e uma reconstrução do ALERT-BENCH sobre o AIT-ADS e o AIT-LDSv2, avaliada nos cenários
santos e harrison. A premissa era que esses dois cenários estavam fora da linhagem do treino.

Ao registrar a decisão, conferi o `validacao.json` da v12. Os oito cenários do AIT-LDSv2 já
estão nos splits:

| Split da v12 | Cenários do AIT-LDSv2 |
| --- | --- |
| Treino | fox, russellmitchell, wardbeck, wheeler, wilson |
| Validação | santos, shaw |
| Teste | harrison |

Não há cenário livre, e santos já serve à seleção do SFT. A regra do AGENTS.md mantém o teste
fora do treino e da seleção de hiperparâmetros.

## Decisão

O responsável confirmou a decisão em 26/11/2026.

- O RL treina nos cinco cenários do split de treino.
- A seleção de checkpoints e do Peso de custo usa santos e shaw.
- A avaliação final no ambiente AIT usa só harrison.
- Russellmitchell e wardbeck são reportados à parte, marcados como contaminados, só para
  comparar com o AIDA.
- O ExCyTIn-Bench é opcional e só entra se der para pontuar sem juiz pago.
- A cláusula NC do AIT-LDSv2 fica registrada como limite para uso comercial de derivados.

## Cobertura

- O ambiente usa só as Modalidades que já existem: linux_auth, apache e suricata.
- Cada alerta do Wazuh vira um Recorte, com a linha de log que o disparou como Âncora. O rótulo
  vem dos rótulos por evento do AIT-LDSv2.
- Alertas de auditd, dnsmasq e outras fontes ficam fora, e o artigo declara quantos foram
  excluídos.
- Se o auditd entrar um dia, ele ganha uma Modalidade com nome próprio, porque `audit` já reúne
  os Exemplos sintéticos do opensec.

## Considered Options

- **Avaliar em santos e harrison, como aceito antes da conferência.** Rejeitada.
  Santos entrou na seleção do SFT, o que viola a regra do hold-out.
- **Refazer a divisão dos cenários do AIT.** Rejeitada. Quebraria a comparação com o Teste real
  da v12 e com o Rival.

## Consequences

- A generalização entre cenários no ambiente AIT fica com um único cenário de teste, e o artigo
  declara esse limite. As métricas por alerta continuam com milhares de alertas.
- O Teste real da v12 continua sendo onde o Guardião precisa superar o Rival.
- As notas de pesquisa que tratavam santos e harrison como reservados foram corrigidas.
