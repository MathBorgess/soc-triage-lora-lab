# Reprodução dos Recortes da v12 pelo Projetor

> Gerado por `scripts/09_reproduzir_v12.py` em 26/11/2026, na revisão `d396034`, com `projetor-0.1` e `recorte-v2.0`. Python 3.12.1 em Darwin arm64. A execução levou 46 s. Os números valem para a cópia local de `data/raw` e `data/processed`, que fica fora do Git.

## Pergunta

A ordem de construção da arquitetura pede um Projetor por Modalidade que reproduza os Recortes aprovados da v12 a partir dos logs de origem, com os mesmos hashes. Este relatório mede isso para linux_auth, apache e suricata.

Reproduzir significa: com as linhas citadas pelo localizador nativo do lote e com a janela que o lote registrou, o perfil do Projetor gera a mesma `entrada` byte a byte, e portanto o mesmo SHA-256. A escolha da âncora e das linhas mostradas é decisão da curadoria e entra como dado. O que o perfil calcula (cabeçalho, contagens, janela, renderização) tem de sair dos logs.

## Resultado

| Medida | Recortes | Parcela |
| --- | ---: | ---: |
| Recortes da v12 nas três Modalidades | 674 | 100% |
| Com linha nativa em `data/raw` | 425 | 63,1% |
| Com todas as linhas citadas conferidas por SHA-256 | 425 | 63,1% |
| Com alguma linha da entrada copiada literalmente do log | 87 | 12,9% |
| **Reproduzidos byte a byte (mesmo SHA-256)** | **48** | **7,1%** |

### Por Modalidade e split

| Modalidade | Recortes | Treino | Validação | Teste | Byte a byte |
| --- | ---: | ---: | ---: | ---: | ---: |
| linux_auth | 272 | 21/206 | 14/42 | 0/24 | 35 (12,9%) |
| apache | 205 | 0/142 | 0/24 | 0/39 | 0 (0,0%) |
| suricata | 197 | 12/149 | 1/24 | 0/24 | 13 (6,6%) |

### Perfis portados

| Perfil | Família | Aplicado a | Byte a byte |
| --- | --- | ---: | ---: |
| `lote08_cas` | CAS | 21 | 21 |
| `lote15_rsva_validacao` | L15-RSVA | 14 | 14 |
| `lote13_aittls` | AITTLS | 13 | 13 |

O perfil `lote15_rsva_validacao` usa um parâmetro de episódio transcrito do script do lote 15: em três episódios (`tmpfiles-22`, `tcpdump-cron-18`, `tcpdump-cron-27`) a curadoria acrescentou a linha da última sessão de ubuntu. O texto dessa linha sai dos logs; só a decisão de incluí-la vem do script. Os outros dois perfis não usam parâmetro de episódio.

## Divergências

Cada Recorte não reproduzido tem uma causa. A tabela por Recorte está em [`11-reproducao-da-v12.csv`](11-reproducao-da-v12.csv).

| Causa | Recortes |
| --- | ---: |
| perfil não portado | 377 |
| sem linha nativa | 249 |
| reproduzido | 48 |

- **sem linha nativa**: o lote não guardou linha de arquivo de `data/raw` (localizador textual, registro de exportação do Splunk, offset de journal, banco SQLite ou parquet) ou o arquivo citado não está na cópia local.
- **fonte ilegível**: o arquivo citado existe, mas a linha não pôde ser lida.
- **linha citada não confere com data/raw**: o SHA-256 da linha não bate com nenhuma das três convenções dos lotes (linha sem `\n`, linha com `\n`, SHA do membro).
- **perfil não portado**: as linhas conferem, mas o formato da família não tem perfil. A tabela abaixo diz por quê.
- **caso fora do perfil**: a família tem perfil, mas o exemplo foge do caso que ele cobre.
- **perfil diverge**: o perfil gerou texto diferente; o detalhe dá a primeira linha e coluna.

### Por família

| Família | Lote | Recortes | Linhas conferidas | Byte a byte | Causa principal | Por quê |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `OX` | lote-08, lote-12 | 62 | 0 | 0 | sem linha nativa | classes de rota e pseudônimos de recurso do lote 07; localizador textual ou arquivo do organization-x fora de data/raw (formato) |
| `L14-APA` | lote-14 | 45 | 45 | 0 | perfil não portado | especificação por episódio (cabeçalho, frase da janela, linhas e opções de renderização escolhidas à mão); linhas do Registro reescritas em forma compacta (script) |
| `L14-SUR` | lote-14 | 43 | 43 | 0 | perfil não portado | especificação por episódio (título, frase da janela, filtros e opções de renderização); a renderização das linhas e as contagens de assinatura são regra comum (script) |
| `L14-LNXA` | lote-14 | 40 | 40 | 0 | perfil não portado | cinco moldes (rajada, sessão, explícito, origem isolada, cron) com janela escolhida à mão, que o localizador não registra, e apelidos conta-NN (script) |
| `L14-LNXB` | lote-14 | 33 | 33 | 0 | perfil não portado | casos escritos por episódio, cada um com resumo próprio, sobre auth.log do MuSAR reconstruído do CSV do Filebeat e do MAWA (script) |
| `DED` | soc-triage-v6 | 29 | 0 | 0 | sem linha nativa | linhas reescritas em JSON em português e invocação do cliente AURA, que não está no log (formato) |
| `L15-RSVA` | lote-15 | 29 | 29 | 14 | perfil não portado | teste do EchoLake: resumo escrito por episódio; a validação tem perfil (script) |
| `L15-RSVY` | lote-15 | 28 | 28 | 0 | perfil não portado | especificação por episódio, como em L14-APA (script) |
| `L15-TSS` | lote-15 | 27 | 27 | 0 | perfil não portado | especificação por episódio, como em L14-SUR (script) |
| `AIT-RM` | sem prova de lote | 26 | 0 | 0 | sem linha nativa | piloto AIT sem localizador nativo; entrada em prosa ou JSON da curadoria (formato) |
| `L16-SUR` | lote-16 | 25 | 25 | 0 | perfil não portado | especificação por episódio, como em L14-SUR (script) |
| `CAS` | lote-08 | 21 | 21 | 21 | reproduzido | reproduzida |
| `RITW` | lote-12 | 18 | 0 | 0 | sem linha nativa | registros de exportação do Splunk; classes de rota e pseudônimos (formato) |
| `AIT1W` | lote-12 | 16 | 16 | 0 | perfil não portado | classes de rota, classe do corpo e pseudônimos de recurso calculados pela cadeia de scripts dos lotes 07, 09 e 12; portável, não portado nesta rodada (script) |
| `L16-APA` | lote-16 | 15 | 15 | 0 | perfil não portado | especificação por episódio, como em L14-APA (script) |
| `cc` | lote-08 | 14 | 0 | 0 | sem linha nativa | localizador textual em data.json.gz do Cyber Czech; molde do lote 07 (script) |
| `AITTLS` | lote-14 | 13 | 13 | 13 | reproduzido | reproduzida |
| `AIT-SA` | sem prova de lote | 11 | 0 | 0 | sem linha nativa | piloto AIT sem localizador nativo; entrada em prosa da curadoria (formato) |
| `BOTSEVE` | lote-12 | 11 | 11 | 0 | perfil não portado | classes semânticas de recurso e pseudônimos (C1, R1) do lote 12 (formato) |
| `SG` | lote-08, soc-triage-v3, soc-triage-v4 | 11 | 0 | 0 | sem linha nativa | evento em banco SQLite do security-gym; prosa dos lotes 03 e 04 (formato) |
| `RIT4W` | lote-12 | 10 | 0 | 0 | sem linha nativa | registros de exportação do Splunk; classes de rota e pseudônimos (formato) |
| `AIT-H` | sem prova de lote | 9 | 0 | 0 | sem linha nativa | piloto AIT sem localizador nativo; entrada em prosa da curadoria (formato) |
| `AITDNS` | lote-12 | 9 | 9 | 0 | perfil não portado | pseudônimos de nome (nome_1) e campos do lote 12 (formato) |
| `LH` | lote-08, soc-triage-v3, soc-triage-v4 | 9 | 2 | 0 | sem linha nativa | prosa dos lotes 03 e 04 com aceites anteriores (formato) |
| `AITADS` | lote-08 | 8 | 8 | 0 | perfil não portado | agregado JSON da curadoria do lote 08 sobre alertas do Wazuh (formato) |
| `CPTC4` | lote-12 | 8 | 0 | 0 | sem linha nativa | offsets em journal do Splunk; classes de rota e pseudônimos (formato) |
| `AC` | lote-08 | 7 | 7 | 0 | perfil não portado | prosa do lote 08 com aceites anteriores (formato) |
| `sg` | lote-08 | 6 | 0 | 0 | sem linha nativa | evento em banco SQLite do security-gym; molde do lote 07 (formato) |
| `AITHTTP` | lote-12 | 5 | 0 | 0 | sem linha nativa | registros numerados do EVE; classes de rota e pseudônimos (formato) |
| `CAM` | lote-08 | 5 | 5 | 0 | perfil não portado | frase de janela do lote 08 com contagens de tipos do EVE (formato) |
| `MSAS` | lote-12 | 5 | 0 | 0 | sem linha nativa | registro do CSV do Filebeat, sem linha do auth.log (formato) |
| `SMLD` | lote-12 | 5 | 5 | 0 | perfil não portado | classes semânticas de recurso e pseudônimos do lote 12 (formato) |
| `sg41-base` | lote-08 | 5 | 0 | 0 | sem linha nativa | evento em banco SQLite comprimido do security-gym; prosa do lote 08 (formato) |
| `BOTSDNS` | lote-12 | 4 | 4 | 0 | perfil não portado | pseudônimos de consulta do lote 12 (formato) |
| `L11-LA` | lote-12 | 4 | 4 | 0 | perfil não portado | eventos normalizados com pseudônimos (origem-01, conta-01) do lote 12 (formato) |
| `ASC` | lote-12 | 3 | 3 | 0 | perfil não portado | eventos normalizados com pseudônimos do lote 12 (formato) |
| `L09-CPTC` | lote-12 | 3 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L09-MAWA` | lote-12 | 3 | 2 | 0 | perfil não portado | família pequena, não analisada |
| `L11-HY` | lote-12 | 3 | 3 | 0 | perfil não portado | eventos normalizados com pseudônimos do lote 12 (formato) |
| `L12-LNX` | lote-12 | 3 | 3 | 0 | perfil não portado | eventos normalizados com pseudônimos do lote 12 (formato) |
| `MAWAP` | lote-12 | 3 | 3 | 0 | perfil não portado | mesma cadeia de classes de rota de AIT1W (formato) |
| `RMX` | lote-08 | 3 | 3 | 0 | perfil não portado | família pequena, não analisada |
| `AITW` | lote-14 | 2 | 2 | 0 | perfil não portado | família pequena, não analisada |
| `EVE` | lote-12 | 2 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L09-LAPT` | lote-12 | 2 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L10-SL700` | lote-12 | 2 | 2 | 0 | perfil não portado | família pequena, não analisada |
| `L11-HPC` | lote-12 | 2 | 2 | 0 | perfil não portado | família pequena, não analisada |
| `L13-AIT-AUTH` | lote-14 | 2 | 2 | 0 | perfil não portado | família pequena, não analisada |
| `RTA` | lote-12 | 2 | 2 | 0 | perfil não portado | mesma cadeia de classes de rota de AIT1W (script) |
| `WF` | lote-08, lote-12 | 2 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `WFX` | lote-08 | 2 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `AC05-LH` | lote-08 | 1 | 1 | 0 | perfil não portado | família pequena, não analisada |
| `AC05-RM` | lote-08 | 1 | 1 | 0 | perfil não portado | família pequena, não analisada |
| `AINC09-SL100` | lote-12 | 1 | 1 | 0 | perfil não portado | família pequena, não analisada |
| `AITAUTH` | lote-08 | 1 | 1 | 0 | perfil não portado | agregado JSON da curadoria do lote 08 sobre alertas do Wazuh (formato) |
| `B2AUTH` | lote-12 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `CT-CAS01` | soc-triage-v5 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L09-AM` | lote-12 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L09-CAM` | lote-12 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L09-FOX-AUTH` | lote-12 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L09-FOX-HTTP` | lote-12 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `L10-SL300` | lote-12 | 1 | 1 | 0 | perfil não portado | família pequena, não analisada |
| `L11-LIB` | lote-12 | 1 | 1 | 0 | perfil não portado | família pequena, não analisada |
| `L13-DED-AUTH` | lote-14 | 1 | 1 | 0 | perfil não portado | família pequena, não analisada |
| `LAN07-coleta_de_metricas` | lote-08 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `LAN07-rotinas_diarias` | lote-08 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `LAN07-rotinas_horarias` | lote-08 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `LAN07-verificacao_de_volume` | lote-08 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `LSPR24-U` | lote-12 | 1 | 0 | 0 | sem linha nativa | família pequena, não analisada |
| `VNL10-DNS-REFUSED` | lote-12 | 1 | 1 | 0 | perfil não portado | família pequena, não analisada |

Na coluna "Por quê", "script" quer dizer que li o script do lote e "formato" que a conclusão vem da forma da entrada e do localizador.

## Leitura

- A v12 não tem um formato de Recorte: tem dezenas de famílias, uma por script de lote. As três famílias portadas aplicam um molde de família calculado só das linhas citadas e se reproduzem por inteiro. Outras famílias parecem ter molde de família (AIT1W, BOTSEVE, AITDNS, os eventos normalizados do lote 12) e são as próximas candidatas a perfil.
- Nos lotes 14, 15 e 16, que somam a maior parte das linhas conferidas, o script guarda uma especificação por episódio: título, frase da janela, filtros e opções de renderização escritos à mão. Reproduzir esses Recortes exige transcrever as especificações, o que equivale a copiar a curadoria para dentro do Projetor.
- Os lotes 03 a 12 usaram prosa, pseudônimos (conta-01, R1, nome_1) e classes semânticas (rota=página_php). Pseudônimos e classes são determinísticos e portáveis; prosa não.
- A escolha da janela e das linhas mostradas é parâmetro da curadoria. Quando o lote a registrou (`janela_agregada` no lote 15), o perfil a usa. Quando não registrou (L14-LNXA), a reprodução exigiria inferir a janela do próprio texto aprovado.

## Decisão pendente

O Projetor do Runtime agêntico precisa gerar Recortes no mesmo formato do treino. Com os números acima, há dois caminhos, e a escolha é do responsável pelo estudo:

1. **Reprojetar a v12 no formato canônico do Projetor** para o dataset v2, mantendo IDs, splits e rótulos, e revisar os rótulos cuja evidência mude de forma.
2. **Manter os formatos da v12 como perfis**, portando família por família. Isso cobre os moldes de família, mas não as especificações por episódio nem a prosa.

Até essa decisão, o Projetor canônico (`soc_triage.guardiao.projetor`) e os três perfis ficam disponíveis, e este relatório serve de linha de base para medir o próximo passo.
