---
status: accepted
---

# A v12 é reprojetada no formato canônico do Projetor

Em 26/11/2026, o responsável pelo estudo decidiu o formato dos Recortes do contrato v2.

O PR #4 implementou o Projetor por Modalidade e mediu quanto dele reproduz a v12. Só 48 dos 674
Recortes de linux_auth, apache e suricata saíram iguais byte a byte (7,1%). As divergências têm
duas causas:
- 377 Recortes vêm de lotes com uma especificação escrita à mão por episódio, ou em prosa;
- 249 não guardaram a linha nativa do log.

## Decisão

- Os Recortes do contrato v2 usam o formato canônico do Projetor, o mesmo que o Runtime agêntico
  gera em produção.
- A v12 é reprojetada a partir dos logs de origem nesse formato.
- Quando a reprojeção muda a Evidência que sustenta um rótulo, o Recorte vai para uma fila de
  revisão do responsável. O rótulo só entra no contrato v2 depois da revisão.
- Recortes sem linha nativa ficam fora do contrato v2 até ganharem um localizador, ou são
  declarados como perda.

## Considered Options

- **Portar os formatos da v12 como perfis, família por família.** Rejeitada. Não cobre as
  especificações por episódio nem a prosa, e o treino usaria um formato que o Projetor de
  produção não gera.
- **Manter a v12 como está e treinar o v2 nela.** Rejeitada pelo mesmo motivo. O modelo veria em
  produção um formato diferente do treino.

## Consequences

- O critério do Projetor muda. Antes ele precisava reproduzir os hashes da v12. Agora ele
  precisa reprojetar a v12 e fechar a fila de revisão.
- A v12 do contrato v1 continua intacta para o estudo de ablação.
- O tamanho da fila de revisão e a fração de Recortes perdidos são reportados no artigo.
- O catálogo de Sinais `sinais-0.1` foi aprovado na mesma data: rajada de SSH (5 falhas em
  300 s), sudo negado, travessia, SQLi e alerta de assinatura do Suricata. A taxa de cada Sinal
  na v12 reprojetada é medida antes de rever os limiares.
