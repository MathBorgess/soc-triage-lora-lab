# Rendimento e rastreabilidade na curadoria de logs de SOC

Registro metodológico de 23/11/2026, posterior ao [planejamento da expansão](02-escala-e-pre-treino.md). O lote 09 usa a v7 como base aprovada. O objetivo de 1.200 unidades inclui o treino já adjudicado e as novas propostas tecnicamente válidas que aguardam revisão humana. Os exemplos de avaliação ficam fora dessa contagem.

Em 23/11 foram validadas **797 de 1.200 unidades**. O lote anterior promoveu 323 das 414 decisões aprovadas, levando a v7 a 415 exemplos de treino. A nova fila tem 382 propostas distribuídas em 41 grupos, com limite observado de 1010 tokens. Faltam 403 novas unidades.

## O que fez uma janela entrar na fila

1. O registro traz um sinal observável no Apache, na autenticação Linux, no Sysmon, no Suricata ou no WAF. Identificando o dado por arquivo e coordenada nativa, o revisor consegue reler a evidência.
2. A proposta explica a relação que sustenta o veredito. Um aceite isolado de SSH mostra autenticação bem-sucedida. Falhas repetidas da mesma origem e conta, seguidas de aceite e abertura de sessão, sustentam uma decisão de triagem diferente.
3. A janela termina no último evento necessário à decisão. Quando o log do host traz horário local sem fuso, usa `null` no campo normalizado e registra separadamente a observação pelo coletor, quando disponível em UTC.
4. A evidência entregue ao modelo conserva o comportamento e o desfecho. A projeção omite comandos, credenciais, payloads e gabaritos dos publicadores. Os nomes de artefatos ficam nos localizadores de auditoria.
5. A janela passa pela deduplicação de evidência e de episódio, pelo schema Pydantic e pela checagem de IoCs por presença literal. O tokenizer local do Gemma 4 E4B-it verifica a sequência completa de entrada e saída com limite de 1.024 tokens.

## Decisões de amostragem

- **Cobertura de negativos difíceis.** O lote inclui clientes que recuperam após erro ou redirecionamento e leituras de recursos da mesma aplicação com eventos correlacionados. O status HTTP isolado informa o resultado de uma solicitação. A sequência mostra a navegação que sustenta o controle.
- **Correlação de autenticação.** Nas capturas MSAS e MAWA, falha, aceite, abertura e encerramento têm pesos diferentes. A janela preserva método, relação entre origem e conta, contagem e desfecho. Situações sem atividade posterior observada permanecem limitadas ao que o log confirma. [MSAS](https://github.com/zisenXu/MuSAR#dataset) · [MAWA](https://zenodo.org/records/23308212)
- **Linhagem.** Reedições, recortes e replays da mesma captura permanecem na mesma família. As variantes do testbed MAWA compartilham um grupo. A Organização X tem uma fila própria e a Organização Y continua reservada para teste. [Organizações X e Y](https://zenodo.org/records/20001206)

## Rendimento de fontes grandes

| Recorte verificado | Volume inspecionado | Propostas na triagem da fonte |
| --- | ---: | ---: |
| WitFoo v2.1.0 ampliado | 50.421.340 linhas em 26 partições Parquet | 4 |
| AInception SL300 variante 7 | 647.049 eventos ECS, incluindo 64.712 Sysmon, em 26 membros | 2 |
| BOTS v1 | 3,56 milhões de eventos Suricata no recorte, além de Sysmon | 23 |
| MSAS | 2.505 eventos OpenSSH em cinco hosts | 5 |
| MAWA | 8 arquivos ZIP de um testbed repetido | 6 entre Apache e Linux |
| CPTC3 | 190.749 registros em seis equipes | 3 |
| Honeynet SotM31 | 202.145 linhas de acesso em um proxy de 2004 | 0 |

O catálogo WitFoo tem dezenas de milhões de eventos. A seleção por canal e a deduplicação deixaram 200 janelas para inspeção, das quais 196 repetiam forma ou evidência. As quatro propostas retidas são controles de web. Na variante SL300, 2.016 das 2.018 janelas pré-selecionadas eram equivalentes. Esses rendimentos caracterizam os recortes e os seletores usados nesta rodada. [WitFoo](https://www.witfoo.com/research/precinct-6-dataset/) · [AInception](https://zenodo.org/records/17659656) · [BOTS v1](https://github.com/splunk/botsv1)

A verificação de integridade depende do formato da fonte. Nas partições WitFoo, tamanho e SHA-256 coincidem com a publicação fixada. Nos recortes de ZIP recuperados por intervalos HTTP, foram conferidos os limites da resposta, o CRC32 do membro e seu SHA-256 local. O recibo registra a granularidade da conferência.

## Revisão e publicação

A fila de trabalho fica em `data/processed/`, com as decisões propostas, evidência projetada e localizadores. Os logs de origem ficam em `data/raw/`. Ambos os diretórios são ignorados pelo Git. Os documentos metodológicos guardam resultados agregados, critérios de seleção e referências. A revisão humana decide quais propostas entram na próxima versão. Material derivado para redistribuição exige revisão dos termos e da descaracterização de cada fonte.
