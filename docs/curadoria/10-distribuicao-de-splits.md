# Distribuição entre treino, validação e teste (v11 e v12)

Em 24/11/2026 os splits foram redistribuídos para chegar à meta de 80/10/10 do estudo. A v10
tinha 1.283 / 11 / 9 exemplos, e a validação e o teste só continham Apache e autenticação Linux.

## Resultado

| Split | v11 | v11 (parcela) | v12 | v12 (parcela) |
| --- | ---: | ---: | ---: | ---: |
| treino | 1.147 | 80,0% | 1.147 | 77,0% |
| validação | 143 | 10,0% | 177 | 11,9% |
| teste | 143 | 10,0% | 166 | 11,1% |

A v12 acrescentou 57 exemplos só à validação e ao teste, para cobrir células fracas. O treino é
idêntico ao da v11, e a validação e o teste da v11 estão contidos na v12.

Os três splits têm as cinco modalidades. A composição por modalidade e veredito fica em
`data/processed/redistribuicao-v11/RELATORIO.md`, fora do Git.

## Regras de alocação

- **Bloco indivisível.** Todos os grupos da mesma família de dataset ficam no mesmo split. Isso
  impede que dias ou hosts da mesma captura caiam em lados diferentes.
- **Exceções, em que cada grupo é um ambiente independente:** os cenários do AIT-LDS, as
  organizações do web-server-log-dataset (a política de reservas já separa a X da Y) e as
  amostras isoladas do EVTX-ATTACK-SAMPLES.
- **Família pelo nome do grupo**, não pelo campo `dataset`, que varia dentro do mesmo grupo.
- **Reservas mantidas:** `ait-lds-v2.1/santos` na validação, `ait-lds-v2.1/harrison` no teste,
  CSE-CIC na validação, EchoLake Cloud e Organização Y no teste.
- **Teto por bloco:** nenhum bloco passa de 20% de um split de avaliação. Na v12 o teste tem a
  Organização Y com 18%, o LightIDS com 17% e o MITRE wizard-spider com 16%, e a validação tem
  o sr-bh com 10%.
- **Busca local com semente 42**, minimizando o desvio das metas por modalidade e veredito.

## Limites conhecidos

- **CSE-CIC:** o arquivo local não tem logs de SSH nem de autenticação, só Windows System e
  syslog do Ubuntu. O grupo reservado da validação não cobre a campanha de força bruta.
- **Células pequenas:** na v12, Suricata tem 24 exemplos na validação e 24 no teste, WAF tem 25 e
  29, e Apache tem 24 e 39. As métricas por modalidade ainda têm intervalos largos. Suricata
  `expected_admin` tem 1 exemplo por split e WAF `expected_admin` não existe.
- **Ambiente repetido:** o laboratório soc-mld repete 40 rodadas quase idênticas de ataque, e os
  6 exemplos dele na validação compartilham um único ambiente.
- **Suspicious orgânico é raro** nos logs do AIT. Parte dos suspicious de Apache da validação é o
  início de um ataque ou uma janela curta.
- **A proporção saiu da meta de 80/10/10** (77,0 / 11,9 / 11,1). Voltar a ela exigiria mais
  exemplos de treino.
- **Moldes parecidos:** 3 moldes benignos genéricos de Suricata, de ambientes diferentes, cruzam
  treino e validação com o mesmo rótulo.
- Os exemplos novos de avaliação entraram como `human_verdict` por decisão do responsável, sem
  revisão individual.
