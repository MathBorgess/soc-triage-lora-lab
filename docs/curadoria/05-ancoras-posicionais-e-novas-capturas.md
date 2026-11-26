# Âncoras posicionais e novas capturas para triagem SOC

Continuação do [lote anterior](04-fontes-adicionais-e-controles.md), em 23/11/2026. O lote 11 parte de 415 exemplos aprovados na v7 e de 462 propostas já validadas. A curadoria verifica novos casos antes de atualizar a fila acumulada de revisão.

## Autenticação com horário local incompleto

Parte dos syslogs de autenticação conserva o relógio local sem ano ou fuso. Nesses casos, a ocasião da decisão é identificada pelo membro de origem e pela posição da última prova. O evento normalizado recebe `timestamp: null`. As demais regras do schema, verificação literal de IoCs, deduplicação e limite de tokens continuam aplicáveis.

A seleção usa relógio local e ordem de origem dentro da mesma janela para sustentar a relação entre eventos. Quando a ordenação de um arquivo agregado é inconsistente, a curadoria relê a captura original e admite somente uma janela em que os pontos antecedem a decisão.

O BOTS v2 ilustra a diferença prática. Um journal com 3.739 registros `sshd` forneceu 1.831 recusas com coordenadas nativas. Uma proposta sobreviveu à deduplicação das rajadas. O localizador da projeção aponta para os offsets e hashes no journal. As 14 provas foram relidas. [BOTS v2 oficial](https://github.com/splunk/botsv2)

## Linhagem e rendimento

O Loghub Linux e o Honeynet Bundle 4 têm 4.400 linhas `messages` idênticas. Os arquivos complementares de autenticação compartilham a família de origem. As capturas independentes Rootly, Hybrid-AI-IPS e HPC fornecem controles e contrastes, incluindo encerramentos PAM observáveis e bloqueios registrados por Fail2Ban. [Loghub](https://github.com/logpai/loghub) · [Honeynet original](https://chuvakin.org/honeynet/)

O Splunk Attack Data foi fixado por commit. Foram adquiridos 536 objetos distintos de log, com 8.876.685.868 bytes e recibos sem divergências de digest. O texto da proposta usa eventos nativos e efeito observado. Nomes de diretórios, ações do catálogo e referências de cenário permanecem na proveniência. Foram aplicados aliases a seis propostas cujos nomes de ferramentas podiam identificar a família da captura. [Revisão de origem](https://github.com/splunk/attack_data/tree/68ab23c7527fa826ed4986c7bab7e3d18ec20eaf)

A leitura dos 509 objetos Sysmon apresentou 4.857.238 registros elegíveis. A deduplicação reteve 100 janelas para revisão por episódio e agrupou 26 delas. A regra reúne janelas do mesmo host e perfil com âncoras separadas em até 120 segundos. A revisão também reuniu casos de perfis diferentes com vínculo pelo GUID e um episódio provável por continuidade temporal no mesmo objeto. Cada conjunto conserva o caso com maior diversidade de eventos e os IDs agrupados no relatório. Nas 74 janelas resultantes, a auditoria reabriu 167 coordenadas em 52 objetos e conferiu digest, provedor, relógio e RecordID. A consolidação reteve 73 propostas dessa fonte após excluir uma evidência que se tornou equivalente depois da substituição de nomes. Os 22 objetos EVE renderam zero propostas novas após as verificações de contexto e deduplicação.

A leitura nacional completa do CPTC4 e a amostra regional renderam oito propostas após verificação por episódio. Foram examinados 5.548.802 HTTP EVE nacionais adicionais e 3.909.688 regionais dentro dos recortes oficiais. A deduplicação reuniu respostas do mesmo cliente, destino e host HTTP em intervalos próximos. [Acervo CPTC4](https://mirrors.rit.edu/cptc/cptc4/)

O prefixo de 16 MiB do Liberty cobriu 3.973.257 linhas completas. Entre elas, 1.192 sessões passaram pela autenticação. Uma proposta adicional preservou as duas sessões completas, por senha e por chave, do mesmo par conta e origem. O caso ilustra a variação que a curadoria consegue sustentar com PAM e coordenadas nativas. [USENIX CFDR](https://www.usenix.org/cfdr-data)

No LMD-2023, marcas temporais divergentes afetaram a repetição da mesma identidade Sysmon no CSV. As janelas remanescentes foram comparadas por posição, RecordID e relógio registrado. O EVTX original do LMD-2022 permitiu releitura nativa. Suas 29 janelas preliminares repetiam formas anteriores. Os dois recortes somaram zero propostas novas. [Catálogo LMD](https://github.com/ChristosSmiliotopoulos/Lateral-Movement-Dataset--LMD_Collections)

## Fechamento do lote 11

Foram incorporadas 94 propostas à fila de revisão, incluindo 75 Sysmon, 11 de autenticação Linux e oito Suricata. São 83 suspeitas, sete benignas, duas rotinas administrativas e duas maliciosas. Cinco usam âncora posicional. O lote passou no schema, na checagem literal de IoCs e no tokenizer do Gemma 4 E4B-it, com máximo de 933 tokens. O máximo da fila acumulada foi 1.014 de 1.024. A fila anterior de 462 propostas foi preservada byte a byte.

A soma técnica chegou a 971 de 1.200, com 415 exemplos aprovados e 556 propostas para revisão humana. As reservas ficam fora dessa conta. Os splits da v7 continuam em 415/11/9 e foram conferidos por SHA-256. O treino permanece pendente de autorização.

## Piloto Locked Shields 2024

O `eve.log` foi conferido com o MD5 publicado. Os 180.044 registros trazem alertas e anomalias, com metadados HTTP embutidos em parte deles. O mesmo cliente recebeu 200 e depois 304 para dois recursos, com as duas revalidações observadas no mesmo fluxo. A janela resultou em uma proposta adicional `benign/info` com 901 tokens. Categorias e IDs de regras ficaram de fora da projeção. Uma janela de redirecionamento aguarda contexto. O piloto separa a edição inteira e acrescenta uma unidade à soma técnica, que passa a 972. [Depósito oficial, CC0 1.0](https://zenodo.org/records/14900873)
