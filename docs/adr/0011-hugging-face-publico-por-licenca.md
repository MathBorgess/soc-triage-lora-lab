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

## Condição por licença, aceita em 26/11/2026

A v12 junta 57 Fontes. O levantamento em `docs/curadoria/09-licencas-das-fontes.md` classificou
cada uma pela licença na fonte primária.

**Dataset.** O dataset público tem três configurações:

- **"aberta":** as 40 Fontes de licença livre (CC BY, CC0, Apache-2.0, MIT), com 73,4% dos
  registros. Os 9 registros do AIT-ADS (CC BY 4.0) entram aqui, separados do AIT-LDS.
- **"nc-sa":** o AIT-LDS v1.1 e v2.1, sob CC BY-NC-SA 4.0.
- **"gpl":** EVTX-ATTACK-SAMPLES, OTRF e Virtual Network Threat, sob GPL-3.0.

Ficam fora as Fontes "só pesquisa" (Loghub, CyLab e Hybrid-AI-IPS) e as 8 sem licença
encontrada. Quando o LICENSE e o README de uma Fonte divergem, vale o texto mais restritivo. O
card lista o que ficou fora e por quê.

**Adaptadores.** O adaptador do artigo, treinado com todos os dados, sai sob CC BY-NC-SA 4.0.
O card lista a licença de cada Fonte, a licença da base (Gemma 4, Apache-2.0) e avisa que o
status legal de pesos treinados com dados NC ou GPL é incerto. Um segundo adaptador, treinado só
com a configuração "aberta", fica previsto para uso comercial. Este ADR descreve licenças e não
é aconselhamento jurídico.

## Considered Options

- **Repositórios privados até o artigo.** Rejeitada pelo responsável.
- **Publicar a v12 inteira sem filtro.** Rejeitada na proposta. Fontes sem licença ou com
  redistribuição proibida não podem sair.

## Consequences

- A primeira publicação acontece quando a versão do dataset do artigo estiver fixada.
- O Teste real publicado pode ficar menor que o usado no artigo. O artigo diz quais Recortes são
  públicos.
- Publicar deixa os dados indexáveis e cacheáveis, mesmo que depois sejam apagados.
