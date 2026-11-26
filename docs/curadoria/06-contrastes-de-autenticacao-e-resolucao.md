# Contrastes de autenticação, navegação e resolução DNS

O lote 12 partiu de 415 exemplos aprovados, 556 propostas da fila anterior e uma proposta do piloto Locked Shields. O objetivo é ampliar a variedade de evidência para a revisão humana, com as reservas de avaliação fora da contagem. [Lote 11](05-ancoras-posicionais-e-novas-capturas.md)

## Rede no AIT-LDS v2.1

A coleção tem versões sem PCAP e arquivos EVE de diferentes sensores. A curadoria reutilizou os ZIPs locais de Fox e Russellmitchell. Em Shaw, Wardbeck, Wheeler e Wilson, 32 membros EVE foram adquiridos por intervalos HTTP, totalizando 480.427.426 bytes de membros comprimidos. O índice do ZIP informa tamanho e CRC de cada membro. O recibo inclui SHA-256 do membro descomprimido. Santos e Harrison permanecem nas reservas. O uso do AIT-LDS é para a pesquisa local sob CC BY-NC-SA 4.0. [Depósito oficial](https://zenodo.org/records/19483937)

O curador usa identificador de fluxo, ID DNS, nome, tipo e pares de endereços para vincular consulta e resposta. A análise procura contrastes em que o log sustenta a distinção, como resposta vazia de uma família IP com resolução na outra pelo mesmo resolvedor. Os nomes são substituídos por aliases consistentes na janela. As coordenadas nativas permitem conferir a igualdade de nomes. A concentração de nomes longos com respostas negativas sustenta suspeita quando há uma rajada observável. A intenção permanece em aberto. [Formato EVE do Suricata](https://docs.suricata.io/en/latest/output/eve/eve-json-format.html)

Na parte HTTP, o mesmo curador validado no CPTC busca efeito observável, como revalidação de cache e falhas de recurso dentro de uma navegação corroborada. A deduplicação cruza formas observáveis e evidências repetidas com a fila anterior. As projeções preservam a relação entre recursos e fluxos e remetem os caminhos completos aos localizadores. [Método anterior](04-fontes-adicionais-e-controles.md)

Os 48 membros, incluindo os 16 locais, forneceram 1.621.497 eventos DNS e 59.153 HTTP. Foram vinculadas 377.686 transações DNS no período da coleta. A deduplicação reteve sete contrastes IPv4/IPv6, duas resoluções de alias e cinco navegações HTTP com recursos correlacionados. As 14 propostas `benign/info` foram conferidas em 51 coordenadas nativas. A seleção independente de DNS descarta aliases quando a consulta seguinte já havia começado antes da resposta que indicava o destino.

## Autenticação Linux

O arquivo SecRepo tem 86.839 linhas e zero aceites explícitos de SSH. Duas propostas `suspicious/medium` preservam a diferença entre muitas origens tentando a mesma conta inválida e uma origem tentando contas distintas. A falha de DNS reverso observada no segundo caso é contexto. Os registros de recusa sustentam o veredito. [Catálogo SecRepo](https://www.secrepo.com/) · [Registro do artefato](https://www.secrepo.com/data/site-links.json)

O Honeynet Bundle 1 reproduz as 3.877 linhas `secure` do Bundle 4 já analisado. A curadoria retirou a sobreposição e colocou a nova proposta no mesmo grupo da coleta anterior. O caso `suspicious/high` tem recusas para a mesma conta e origem em conexões distintas, além de uma recusa seguida de aceite no processo final. No Bundle 7, os 108 aceites careciam do vínculo com recusa anterior para o mesmo par. As três propostas de autenticação foram relidas por posição e digest, com o horário normalizado `null` quando o syslog omite fuso e ano. [Acervo do publicador](https://log-sharing.dreamhosters.com/)

Em três dias do DEDALE, 67 janelas SSH com o ciclo PAM completo repetiram formas cobertas na v7. Outros 33 aceites com erro terminaram em timeout sem fechamento PAM registrado. A amostra de confirmação procurou reconexão pela mesma conta, origem e chave. O recorte rendeu zero novas propostas.

## Apache no AIT-LDS v1.1

Foram adquiridos oito membros Apache, um de acesso e um de erro por testbed. Os intervalos conferidos somam 7.690.480 bytes. A leitura de 500.282 linhas de acesso permitiu cruzar status, método, referenciador e cliente em janelas do mesmo episódio. A v1.1 tem coleta própria e é usada sob CC BY-NC-SA 4.0. [Depósito oficial](https://zenodo.org/records/4264796)

O lote reteve 16 propostas Apache, com três `malicious/medium`, 12 `benign/info` e uma `expected_admin/info`. A rotina administrativa é um contraste difícil para a triagem. Dois casos do mesmo cliente, separados por 74 segundos, foram consolidados em um episódio. Foram relidas 51 provas nativas e o maior exemplo teve 658 tokens no Gemma.

## Controles Sysmon

Os arquivos Nextron de Windows 7 e Windows 11 mais antigo oferecem 34 controles com evidência nativa e nove perfis. Dois casos correlacionam, por GUID, a inicialização de processos, o carregamento de um módulo assinado e acesso a outro processo. São controles para o padrão de acesso sensível presente em lotes anteriores. A revisão preserva a árvore do processo e as permissões observadas. O grupo de origem Nextron permanece indivisível. Os 72 localizadores foram relidos, com máximo de 955 tokens. [Distribuição Nextron v0.8.5](https://github.com/NextronSystems/evtx-baseline/releases/tag/v0.8.5)

A captura do Windows Server Azure acrescentou 14 controles após o cruzamento com Windows 7, Windows 11 e a fila anterior. São 48 propostas Nextron em dez perfis, com 102 localizadores verificados. O maior exemplo contém 1.013 tokens. [Distribuição Nextron v0.8.5](https://github.com/NextronSystems/evtx-baseline/releases/tag/v0.8.5)

O recorte COMISET LAB passou de 112 para 368 MiB comprimidos. Dos 3.157.518 eventos Sysmon, a curadoria reteve uma proposta `suspicious/medium`, apoiada no vínculo entre a criação do processo e o registro de acesso a um processo protegido. O efeito desse acesso fica em aberto. A releitura conferiu as duas coordenadas. O recorte continuou concentrado em um host e um dia. [Depósito COMISET LAB](https://zenodo.org/records/15375146)

## Fechamento do lote 12

A fila acumulada chegou a 639 propostas. O lote incorporou 83, das quais 82 foram verificadas nesta rodada e uma já havia sido contada no piloto Locked Shields. São 49 Sysmon, 16 Apache, 15 Suricata e três de autenticação Linux. A rodada registrou 75 `benign`, quatro `suspicious`, três `malicious` e uma `expected_admin`.

Com os 415 exemplos aprovados, a soma técnica chegou a 1.054 de 1.200. Os checks de Pydantic, IoCs e supervisão da resposta passaram. O máximo foi 1.013 tokens no lote e 1.014 na fila acumulada para limite de 1.024. A fila anterior de 556 propostas foi preservada byte a byte. As reservas permanecem fora da soma e os splits da v7 mantêm os hashes de 415/11/9 exemplos. O treino segue pendente de aprovação.
