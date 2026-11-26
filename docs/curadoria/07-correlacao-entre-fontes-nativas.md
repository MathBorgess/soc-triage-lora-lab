# Correlação entre registros nativos de rede e autenticação

> Rascunho do lote 13. Os artefatos foram preservados para revisão futura após a [pausa da coleta](08-marco-de-1000-e-proximos-passos.md). A fila consolidada de referência é a do lote 12.

O lote 13 parte de 1.054 unidades tecnicamente validadas, com 415 exemplos aprovados e 639 propostas para revisão. A fila anterior serve tanto para deduplicação quanto para verificar a preservação byte a byte. As reservas de avaliação continuam no manifesto. [Resultado anterior](06-contrastes-de-autenticacao-e-resolucao.md)

## DNS, TLS e desfecho TCP

A curadoria retomou os sensores de firewall e web dos mesmos seis testbeds livres do AIT-LDS v2.1. Um caso exige consulta e resposta DNS no mesmo fluxo, endereço da resposta igual ao destino TCP, SNI igual ao nome consultado e tráfego nas duas direções depois da negociação TLS. O log normalizado usa a última evidência de fluxo como âncora. Os nomes são substituídos por aliases consistentes na janela. [Depósito do AIT-LDS](https://zenodo.org/records/19483937) · [Formato EVE](https://docs.suricata.io/en/latest/output/eve/eve-json-format.html)

Foram encontradas 21.966 sequências correlacionadas. A deduplicação reteve 19 propostas, com 12 sequências DNS/TLS e sete casos de tentativa TCP sem resposta seguida de conexão bem-sucedida ao mesmo destino. Os últimos sete funcionam como negativos difíceis. A releitura confirmou 83 coordenadas nos três arquivos representados pela seleção. A concentração é de 16 propostas Fox, duas Wilson e uma Shaw. Esse recorte amplia os contrastes dentro da linhagem AIT.

## Autenticação com desfecho

No AIT-LDS v1.1, a cronologia de autenticação contém 934 recusas PAM do Dovecot. Em 828 linhas, os dois marcadores de origem concordam. Os quatro recortes repetem a forma, então um caso de Insect representa as recusas contra a mesma conta em seis instantes de uma janela de 18 segundos. A proposta é `malicious/medium`. Em Cup, o ciclo PAM do cron repetiu o da hora anterior em meio a recusas de outro serviço. Essa janela entrou como `expected_admin/info`. [Depósito do AIT-LDS v1.1](https://zenodo.org/records/4264796)

No DEDALE, a proposta `malicious/high` liga aceite de chave para `root`, abertura da sessão PAM, acesso bem-sucedido à base de identidades observado pelo Auditbeat e encerramento PAM. Host, PID, identificador de sessão e horário sustentam a ligação com o cenário adjudicado. A revisão preservou o grupo original e reteve um episódio representativo com desfecho próprio.

## Journal do BOTS v3

O pacote original de 335.251.397 bytes passou no MD5 publicado e no SHA-256 local. A extração seletiva reteve 17 journals e verificou a integridade do gzip interno. A prova de cada proposta aponta para o membro e a posição nos bytes descomprimidos. Os marcadores de texto só orientam a busca. O registro precisa passar pela interpretação nativa do domínio antes de propor um caso. A formatação `stream:*` do índice permanece distinta do EVE Suricata. [Distribuição original BOTS v3, CC0 1.0](https://github.com/splunk/botsv3)
