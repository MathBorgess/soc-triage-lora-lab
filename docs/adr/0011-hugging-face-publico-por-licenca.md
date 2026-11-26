---
status: accepted
---

# Datasets e adaptadores ficam públicos no Hugging Face, respeitando a licença de cada Fonte

Em 26/11/2026, o responsável decidiu que os repositórios do Hugging Face do projeto são
públicos, para o dataset e para os adaptadores.

## Decisão

- O dataset e os adaptadores ficam em repositórios públicos da conta do responsável.
- O token do Hugging Face fica só no Mac. A VM do Colab recebe os dados por `colab upload` e
  devolve os adaptadores por `colab download`. O Mac envia tudo ao Hugging Face.

## Condição proposta, a confirmar

A v12 junta 57 Fontes, e só 11 têm licença registrada nos recibos de aquisição. Publicar um
derivado exige o que cada licença permite. Proposta:

- Cada Fonte só entra no dataset público se a licença permitir redistribuir, conforme a tabela
  em `docs/curadoria/09-licencas-das-fontes.md`.
- Fontes com NC ou SA, como o AIT-LDSv2 (CC BY-NC-SA 4.0), saem numa configuração separada, sob
  a mesma licença.
- Fontes sem licença encontrada ou que proíbem redistribuir ficam fora. O card do dataset lista
  o que ficou fora e por quê.
- O card dos adaptadores declara as licenças dos dados de treino e a licença da base, o Gemma 4
  sob Apache-2.0.

## Considered Options

- **Repositórios privados até o artigo.** Rejeitada pelo responsável.
- **Publicar a v12 inteira sem filtro.** Rejeitada na proposta. Fontes sem licença ou com
  redistribuição proibida não podem sair.

## Consequences

- A primeira publicação espera a tabela de licenças e a confirmação da condição.
- O Teste real publicado pode ficar menor que o usado no artigo. O artigo diz quais Recortes são
  públicos.
- Publicar deixa os dados indexáveis e cacheáveis, mesmo que depois sejam apagados.
