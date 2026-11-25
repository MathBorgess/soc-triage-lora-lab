# Régua de rótulos: autenticação Linux e escalada de privilégio

Decisão de Matheus em 23/11/2026, tomada ao reconciliar convenções que as rodadas anteriores
aplicavam de forma diferente. A régua vale para os três splits e para novas propostas.

## Regras aprovadas

| Situação no recorte, até a âncora | Rótulo |
| --- | --- |
| Conta de serviço web troca de conta com `su` e a conta obtém root com `sudo` | `malicious/high` |
| Recusas de SSH da mesma origem, sem aceite: 5 ou mais falhas em 3 ou mais contas, ou 10 ou mais falhas | `malicious/medium` |
| Recusas de SSH da mesma origem, sem aceite, abaixo desse volume | `suspicious/medium` |
| Recusas de SSH com origem loopback, sem aceite | `suspicious/medium` |
| Aceite da mesma origem durante ou logo depois de uma rajada que cumpre a régua de volume | `malicious/high` |
| Acesso root por senha em vários hosts pela mesma origem que acumula a rajada | `malicious/high` |
| Poucas falhas em ritmo humano seguidas de aceite, com uso legítimo anterior da mesma origem e conta visível no recorte | `benign/info` |
| Poucas falhas em ritmo humano seguidas de aceite, sem esse histórico no recorte | `suspicious/low` |

Contagens. Falha é uma recusa de senha ou uma tentativa com usuário inválido da mesma origem.
Conta é um nome de conta distinto nessas tentativas. A janela termina na âncora. Eventos
posteriores não entram nem nas contagens.

Rótulos `suspicious/low` que já existiam não mudam por esta régua.

O bloqueio do sensor (Fail2Ban) conta como evidência extra: uma rajada abaixo do volume, mas com
bloqueio da origem, fica `malicious/medium`.

## Evidência exigida

- Um aceite de SSH precisa vir com as falhas da **mesma origem contra qualquer conta**, não só
  contra a conta aceita. Filtrar por conta esconde a rajada e transforma um acesso por força
  bruta num exemplo que parece erro de digitação.
- Quando houver muitas linhas, resuma com contagens explícitas e mostre de 3 a 8 linhas, entre
  elas a da âncora.

## Alcance

- A régua de volume vale para SSH e para o PAM do Dovecot. Com origem loopback e abaixo do
  volume, o Dovecot também fica `suspicious/medium`. Outros serviços aguardam decisão própria.
- A regra do aceite depois de rajada vale para todos os casos, não só para o que a motivou.
- Ao mudar o rótulo de um exemplo, atualize a justificativa. Ela precisa descrever a mesma
  decisão e usar só números que aparecem na evidência.

## Impacto na v10

A v10 aplica esta régua sobre a v9 e preserva a v9 como foi aprovada. A tabela por exemplo, os
rótulos antigos e as contagens ficam em `data/processed/integracao-v10/` e
`data/processed/soc-triage-v10/correcoes-v10.json`, fora do Git.
