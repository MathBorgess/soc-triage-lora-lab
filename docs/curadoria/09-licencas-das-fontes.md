# Licenças das Fontes da v12

Em 26/11/2026, o responsável decidiu publicar o dataset e os adaptadores no Hugging Face. A
condição do [ADR 0011](../adr/0011-hugging-face-publico-por-licenca.md) exige saber o que cada
licença permite redistribuir. Este levantamento cobre as 57 Fontes da v12. Uma Fonte é o prefixo
antes da `/` nos grupos de `splits.<split>.groups` em `validacao.json`.

A tabela não interpreta a lei. Ela cita o trecho que sustenta cada classificação. A decisão de
publicar continua com o responsável.

## Resumo

### Fontes por categoria

| Categoria | Fontes | Treino | Validação | Teste | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| publicável | 40 | 860 | 100 | 133 | 1.093 |
| publicável com restrição | 9 | 223 | 56 | 20 | 299 |
| não publicável | 0 | 0 | 0 | 0 | 0 |
| desconhecida | 8 | 64 | 21 | 13 | 98 |
| **total** | **57** | **1.147** | **177** | **166** | **1.490** |

### Fração dos registros por split

| Split | Publicável | Com restrição | Desconhecida |
| --- | ---: | ---: | ---: |
| treino | 75,0% | 19,4% | 5,6% |
| validação | 56,5% | 31,6% | 11,9% |
| teste | 80,1% | 12,0% | 7,8% |
| todos | 73,4% | 20,1% | 6,6% |

- Nenhuma Fonte proíbe redistribuir. Nenhuma exige aceite individual, cadastro ou login.
- As restrições se dividem em três tipos:
  - **NC e SA** (CC BY-NC-SA 4.0): `ait-lds-v1.1` e `ait-lds-v2.1`. São 105 / 32 / 11 registros.
  - **Copyleft** (GPL-3.0, com efeito parecido com SA): `evtx-attack-samples`,
    `otrf-apt29`, `otrf-atomic-windows` e `virtual-network-threat-92b4a86`. São 83 / 2 / 9.
  - **Só pesquisa** (ou pesquisa e educação): `loghub-openssh`, `cylab-apt-persistence` e
    `hybrid-ai-ips-2026`. São 35 / 22 / 0.
- As Fontes fora de “publicável” com mais registros são `ait-lds-v2.1` (125), `otrf-apt29` (47),
  `evtx-attack-samples` (40), `loghub-openssh` (31), `musar-msas` (23), `ait-lds-v1.1` (23) e
  `cylab-apt-persistence` (22).
- A validação é o split mais afetado. Só 56,5% dos registros são publicáveis sem restrição.
- Os 9 registros de treino do AIT-ADS estão no prefixo `ait-lds-v2.1`, mas o AIT-ADS é CC BY 4.0.
  Se forem separados, o treino publicável sobe para 869 registros (75,8%).

### Pontos para decisão do responsável

1. **Conflito no OTRF.** O LICENSE da revisão usada é MIT, mas o README diz GPL-3.0. A tabela
   adota o GPL-3.0. As duas licenças permitem redistribuir.
2. **Conflito no Hybrid-AI-IPS.** O LICENSE é MIT, mas o README limita o uso a pesquisa e educação.
3. **CyLab.** O texto limita o uso a pesquisa e educação e não autoriza redistribuir de forma
   expressa. Convém confirmar com o publicador antes de incluir.
4. **Loghub.** O registro no Zenodo marca CC BY 4.0. O LICENSE do repositório e a própria descrição
   do registro limitam o uso a pesquisa ou trabalho acadêmico. A tabela adota o texto mais restritivo.
5. **Registro L11-LA-03.** Fica em `honeynet-pslss`, mas também usa a cópia do Loghub
   (`Linux.tar.gz`). Trocar o localizador pelo original do PSLSS ou tratar o registro como restrito.

## Método

- **Ligação com os grupos.** O `revisao.csv` tem 1.490 linhas, na mesma ordem dos três JSONL.
  Conferi `entrada` com a mensagem `user` e `alvo_json` com a mensagem `assistant`. As 1.490
  linhas coincidem. Em 16 registros do `loghub-openssh` o texto tem CRLF. Eles só coincidem quando
  o CSV é lido sem normalizar as quebras de linha (`newline=""`).
- **Contagem.** Os 57 prefixos do `revisao.csv` são os mesmos de `validacao.json`. Os grupos de
  cada split também coincidem.
- **Fontes primárias.** Consultei a página oficial ou a API oficial do repositório de cada Fonte:
  Zenodo (`/api/records/<id>`), GitHub (`LICENSE` e README na revisão usada), Hugging Face (card
  na revisão usada), Mendeley Data (API pública), Harvard Dataverse, Recherche Data Gouv, GitLab
  da CyLab e Bitbucket. Também li as páginas do CIC, DEDALE, PSLSS, Security Repo, ASCEND, RIT e
  USENIX CFDR. Todos os acessos foram em 2026-11-26.
- **Revisão.** Quando o projeto fixa uma revisão, conferi a licença nessa revisão.
- **Recibos.** Os 11 recibos com licença conferem com a fonte primária: AIT-ADS, AIT-LDS v1.1,
  Cyber Czech, `lucz-forstner-waf`, Multi-source LAN, Nextron, Rootly, Security-Gym, SOC-MLD,
  BOTS v1 e SR-BH.
- **Escopo.** Não baixei datasets e não fiz login. Li só metadados, páginas e arquivos de licença.
- **Busca adicional.** Para as Fontes sem licença, procurei outra fonte primária (página do dataset,
  Zenodo ou artigo). Não achei licença para os dados. A licença de um artigo não cobre os dados.

## Trechos das licenças padrão

Quando a linha da tabela só traz o identificador da licença, o trecho que sustenta a categoria está
aqui.

| Licença | Trecho | Onde li o texto |
| --- | --- | --- |
| CC BY 4.0 | §2(a)(1): “reproduce and Share the Licensed Material, in whole or in part”. §3(a) exige identificar o criador ao compartilhar. | <https://ascend-data.sri.com/experiment-ogames-2025/ascend-data-license.txt> |
| CC BY-NC-SA 4.0 | §2(a)(1): “for NonCommercial purposes only”. §3(b)(1): “a Creative Commons license with the same License Elements”. | <https://raw.githubusercontent.com/spdx/license-list-data/main/text/CC-BY-NC-SA-4.0.txt> |
| CC0 1.0 | “waives, abandons, and surrenders all of Affirmer's Copyright and Related Rights”. | <https://github.com/splunk/botsv1/blob/97fb3f25d2b6dcdcd4d0aa23864587ac2093a321/LICENSE> |
| Apache-2.0 | §4: “You may reproduce and distribute copies of the Work or Derivative Works”. §4(a) exige entregar uma cópia da licença. | <https://github.com/splunk/attack_data/blob/68ab23c7527fa826ed4986c7bab7e3d18ec20eaf/LICENSE> |
| MIT | “use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies”. O aviso de licença deve acompanhar as cópias. | <https://github.com/fkie-cad/socbed-eval-acsac-2021/blob/c264060f0e65ea69c2d891525ae835a543f851ca/LICENSE> |
| GPL-3.0 | §5(c): “You must license the entire work, as a whole, under this License”. | <https://raw.githubusercontent.com/spdx/license-list-data/main/text/GPL-3.0-only.txt> |

Os sites creativecommons.org e gnu.org não responderam a partir desta máquina. Por isso, os textos
das licenças Creative Commons e GPL vieram das cópias listadas acima. O identificador de cada licença veio da fonte
primária da Fonte.

## Tabela por Fonte

A coluna de registros mostra treino / validação / teste. A data de acesso é 2026-11-26 em todas as
linhas.

| Fonte | Licença | URL da prova | Categoria | Restrição | Treino / Val. / Teste | Observação |
| --- | --- | --- | --- | --- | ---: | --- |
| `ainception-v1` | CC BY 4.0 | <https://zenodo.org/records/17659656> | publicável | Atribuição. | 0 / 0 / 7 | Registro declara `cc-by-4.0`. SL100, SL300 variante 7 e SL700 vêm do mesmo depósito. |
| `ait-attackbed` | CC BY 4.0 | <https://zenodo.org/records/18861762><br><https://zenodo.org/records/19810174> | publicável | Atribuição. | 0 / 4 / 1 | CAM-LDS v2 (4 de validação) e AttackMate (1 de teste). Os dois registros declaram `cc-by-4.0`. |
| `ait-lds-v1.1` | CC BY-NC-SA 4.0 | <https://zenodo.org/records/4264796> | publicável com restrição | NC e SA. | 19 / 4 / 0 | Registro declara `cc-by-nc-sa-4.0`. Confere com o recibo. |
| `ait-lds-v2.1` | CC BY-NC-SA 4.0 (e CC BY 4.0 no AIT-ADS) | <https://zenodo.org/records/19483937><br><https://zenodo.org/records/8263181> | publicável com restrição | NC e SA. | 86 / 28 / 11 | AIT-LDS v2.1 declara `cc-by-nc-sa-4.0`. O prefixo inclui 9 registros de treino do AIT-ADS, que declara `cc-by-4.0` (confere com o recibo). Separados, esses 9 seriam publicáveis. |
| `ascend-ogames-2025` | CC BY 4.0 | <https://ascend-data.sri.com/experiment-ogames-2025/ascend-data-license.txt> | publicável | Atribuição. | 3 / 0 / 0 | O arquivo é o texto do CC BY 4.0. A página diz: “Downloading or using any data in this repository indicates acceptance of these terms.” Não há cadastro nem aceite individual. |
| `atlasv2` | Nenhuma encontrada | <https://bitbucket.org/sts-lab/atlasv2/src/2fd77199fd7225b2387cbaded2b5b5de5da0de5b/README.md> | desconhecida | Não publicar. | 0 / 0 / 4 | O README não declara licença. Os dados ficam numa pasta Box. O arXiv 2401.01341 só licencia o artigo. |
| `cam-lds-scenario-3` | CC BY 4.0 | <https://zenodo.org/records/18390561> | publicável | Atribuição. | 0 / 7 / 0 | Registro declara `cc-by-4.0`. |
| `casinolimit-v2` | CC BY 4.0 | <https://zenodo.org/records/17256954> | publicável | Atribuição. | 22 / 0 / 0 | Registro declara `cc-by-4.0`. |
| `cerberus-trace` | Apache-2.0 | <https://github.com/bazz-066/cerberus-trace/blob/69933c61491fa966068c44c11172889898fbe789/LICENSE> | publicável | Aviso de licença e atribuição. | 3 / 0 / 0 | LICENSE na revisão usada é Apache 2.0. |
| `comiset-lab-15375146` | CC BY 4.0 | <https://zenodo.org/records/15375146> | publicável | Atribuição. | 0 / 2 / 0 | Registro declara `cc-by-4.0`. |
| `cptc3-rit-2018` | Nenhuma encontrada | <https://mirrors.rit.edu/cptc/> | desconhecida | Não publicar. | 21 / 0 / 0 | O espelho não tem LICENSE nem README. A página da RIT só diz “collect, anonymize, and publicize research data”. |
| `cptc4-rit-2019` | Nenhuma encontrada | <https://mirrors.rit.edu/cptc/cptc4/mirrors/> | desconhecida | Não publicar. | 18 / 0 / 0 | Mesma situação do CPTC3. Inclui edições nacional (14) e regional (4). |
| `crs-paranoia-benchmark` | CC BY 4.0 (dados) e MIT (código) | <https://github.com/stephenedlin/crs-paranoia-benchmark/blob/f3eb21b262882375f6e3b47036ab74a68f4b9efe/LICENSE> | publicável | Atribuição. | 33 / 0 / 0 | Trecho: “DATA, LOGS, AND FIGURES … are licensed under the Creative Commons Attribution 4.0”. |
| `cse-cic-ids2018` | Licença própria do CIC | <https://www.unb.ca/cic/datasets/ids-2018.html> | publicável | Citação e link obrigatórios. | 0 / 14 / 0 | Trecho: “You may redistribute, republish, and mirror the CSE-CIC-IDS2018 dataset in any form.” Exige citação e link para a página na AWS. |
| `cyber-czech-2019` | CC BY 4.0 | <https://zenodo.org/records/3746129> | publicável | Atribuição. | 14 / 0 / 0 | Registro declara `cc-by-4.0`. Confere com o recibo. |
| `cylab-apt-persistence` | Termo próprio: pesquisa e educação | <https://gitlab.cylab.be/cylab/datasets/apt-persistence/-/blob/c373881ab08c772270a090f06362bb71da819751/README.md> | publicável com restrição | Só pesquisa e educação. | 0 / 22 / 0 | Trecho: “This dataset is provided for research and educational purposes.” Para outros usos, pede contato com o autor. O texto não autoriza redistribuir de forma expressa. Confirmar com o publicador antes de incluir. |
| `dedale-v2` | CC BY 4.0 | <https://doi.org/10.57745/Y5JLDG><br><https://dedale.inria.fr/download.html> | publicável | Citação e link obrigatórios. | 50 / 0 / 0 | O Dataverse declara CC BY 4.0. A página diz: “You may redistribute, republish, and mirror the DEDALE dataset in any form.” |
| `echolake-art-38e19f6` | CC0 1.0 | <https://github.com/daveherrald/echolake-datasets/blob/38e19f60c366ef278e78f9c161c1248c812f7a4f/README.md> | publicável | Nenhuma. | 5 / 0 / 0 | O README da revisão põe os conjuntos ART sob CC0 1.0. O LICENSE é o CC0. |
| `echolake-cloud-data-exfiltration` | CC0 1.0 | <https://github.com/daveherrald/echolake-datasets/blob/01aeb66088bb465ed0414fb3ee07647d3303ff43/README.md> | publicável | Nenhuma. | 0 / 0 / 15 | O README da revisão usada põe “Cloud Data Exfiltration” sob CC0 1.0. |
| `echolake-paws-38e19f6` | CC0 1.0 | <https://github.com/daveherrald/echolake-datasets/blob/38e19f60c366ef278e78f9c161c1248c812f7a4f/README.md> | publicável | Nenhuma. | 0 / 15 / 0 | O README da revisão põe os conjuntos PAWS sob CC0 1.0. |
| `evtx-attack-samples` | GPL-3.0 | <https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES/blob/4ceed2f4706daf601c212a8f91c113dd85349a2c/LICENSE.GPL> | publicável com restrição | Copyleft (efeito de SA). | 36 / 2 / 2 | O README remete ao LICENSE.GPL. Ver o trecho do GPL-3.0 na legenda. |
| `honeynet-pslss` | Permissão própria do PSLSS | <https://log-sharing.dreamhosters.com/> | publicável | Nenhuma exigida; atribuição pedida. | 6 / 0 / 0 | Trecho: “License / permission to use: public; use for whatever you want.” O registro L11-LA-03 também usa a cópia do Loghub (Linux.tar.gz), que tem a licença do Loghub. Trocar o localizador pelo original do PSLSS ou tratar esse registro como restrito. |
| `hybrid-ai-ips-2026` | MIT (LICENSE) e termo de pesquisa (README) | <https://github.com/Eugen548/Hybrid-AI-IPS/blob/10997e39552eda0ab0f8b97193080ee9e22a77ea/README.md> | publicável com restrição | Pesquisa e educação (conflito). | 4 / 0 / 0 | O LICENSE é MIT. O README diz: “This repository is released for research and educational purposes.” Adotei a leitura mais restritiva. O responsável decide. |
| `lightids-v2` | CC BY 4.0 | <https://zenodo.org/records/21872151> | publicável | Atribuição. | 0 / 0 / 29 | Registro declara `cc-by-4.0`. |
| `linux-apt-v2` | CC BY 4.0 | <https://data.mendeley.com/datasets/5x68fv63sh/2> | publicável | Atribuição. | 2 / 0 / 0 | A API do Mendeley Data declara “CC BY 4.0” na versão 2. |
| `locked-shields-2024` | CC0 1.0 | <https://zenodo.org/records/14900873> | publicável | Nenhuma. | 0 / 0 / 21 | Registro declara `cc-zero`. |
| `locked-shields-2024-partners-run` | CC0 1.0 | <https://zenodo.org/records/14900873> | publicável | Nenhuma. | 0 / 0 / 1 | Mesmo `eve.log` do LSPR24 que o prefixo anterior. |
| `loghub-openssh` | Licença do Loghub (pesquisa ou trabalho acadêmico) | <https://github.com/logpai/loghub/blob/dd61d0952749ee7963bde24220d1be5ede023033/LICENSE><br><https://zenodo.org/records/8196385> | publicável com restrição | Só pesquisa ou trabalho acadêmico; citar e manter o aviso. | 31 / 0 / 0 | Trecho: “The datasets are freely available for research or academic work”. O Zenodo marca `cc-by-4.0`, mas a descrição repete esse texto. Adotei o mais restritivo. |
| `lucz-forstner-waf` | CC BY 4.0 | <https://zenodo.org/records/17178461> | publicável | Atribuição. | 191 / 0 / 0 | Registro declara `cc-by-4.0`. Confere com o recibo. |
| `mawa-v1` | CC BY 4.0 | <https://zenodo.org/records/23308212> | publicável | Atribuição. | 17 / 0 / 0 | Registro declara `cc-by-4.0`. |
| `mitre-brawl-public-game-001` | CC BY 4.0 | <https://github.com/mitre/brawl-public-game-001/blob/7ec51fac8fc05ea01da210f604b821ef52818173/README.md> | publicável | Atribuição. | 8 / 0 / 0 | Trecho: “This data is released under the Creative Commons BY License”. |
| `mitre-wizard-spider-v1` | Apache-2.0 | <https://huggingface.co/datasets/the-mitre-corporation/wizard-spider-cyberattack-timeline-reconstruction/blob/76c0988b497def0ce2d5cc5935a24423b7d1e25a/README.md> | publicável | Aviso de licença e atribuição. | 0 / 0 / 27 | Trecho: “This dataset, including the EVTX and PCAPNG captures, … is released under the Apache License”. |
| `multi-source-lan-v2.0` | CC BY 4.0 | <https://zenodo.org/records/24394558> | publicável | Atribuição. | 4 / 0 / 0 | Registro declara `cc-by-4.0`. Confere com o recibo. |
| `musar-msas` | Nenhuma encontrada | <https://github.com/zisenXu/MuSAR/tree/be4085b709f384d85a04a6db3bed1035673c4b5b> | desconhecida | Não publicar. | 23 / 0 / 0 | O repositório não tem LICENSE. O README não fala em licença. Os dados ficam no Google Drive. |
| `nextron-evtx-baseline` | Apache-2.0 | <https://github.com/NextronSystems/evtx-baseline/blob/v0.8.5/LICENSE> | publicável | Aviso de licença e atribuição. | 173 / 0 / 0 | LICENSE da tag v0.8.5 é Apache 2.0. Confere com o recibo. |
| `online-shop-v1` | CC BY 4.0 | <https://zenodo.org/records/18895701> | publicável | Atribuição. | 15 / 0 / 0 | Registro declara `cc-by-4.0`. |
| `otrf-apt29` | MIT (LICENSE) e GPL-3.0 (README) | <https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/README.md> | publicável com restrição | Possível copyleft (conflito). | 47 / 0 / 0 | O LICENSE da revisão é MIT. O README diz “License: GPL-3.0”. Adotei o GPL-3.0, que é o mais restritivo. As duas permitem redistribuir. |
| `otrf-atomic-windows` | MIT (LICENSE) e GPL-3.0 (README) | <https://github.com/OTRF/Security-Datasets/blob/d9d40ef123d2c87d5d3df28c96bcab4f0faccc87/LICENSE> | publicável com restrição | Possível copyleft (conflito). | 0 / 0 / 6 | Mesmo repositório e mesmo conflito do otrf-apt29. |
| `provcon-57e38a5` | Nenhuma encontrada | <https://github.com/NUS-Curiosity/provcon/tree/57e38a58b3d62d295a20259f7ab49a616a112419> | desconhecida | Não publicar. | 0 / 0 / 6 | O repositório não tem LICENSE. O README só pede citação do artigo. |
| `rootly-ai-labs` | Apache-2.0 | <https://github.com/Rootly-AI-Labs/logs-dataset/blob/5d7448debdf22ad27358fdcc62fc36205496e3f8/LICENSE> | publicável | Aviso de licença e atribuição. | 28 / 0 / 0 | Apache e OpenSSH vêm do mesmo repositório. Confere com o recibo. |
| `secrepo` | CC BY 4.0 | <https://www.secrepo.com/> | publicável | Atribuição. | 15 / 0 / 0 | Trecho: “All data generated and hosted by Security Repo is done so under the following license”. A licença citada é CC BY 4.0. O `auth.log` não tem exceção em https://www.secrepo.com/data/site-links.json. |
| `security-gym-v4.1` | Apache-2.0 | <https://zenodo.org/records/21763493><br><https://huggingface.co/datasets/j-klawson/security-gym-v4> | publicável | Aviso de licença e atribuição. | 0 / 22 / 0 | O Zenodo declara `apache2.0`. O card do Hugging Face diz Apache-2.0. Confere com o recibo. |
| `soc-mld-v2` | CC BY 4.0 | <https://zenodo.org/records/23116148> | publicável | Atribuição. | 0 / 11 / 0 | Trecho da descrição: “License: Creative Commons Attribution 4.0 International (CC BY 4.0).” Confere com o recibo. |
| `socbed-acsac-2021` | MIT | <https://github.com/fkie-cad/socbed-eval-acsac-2021/blob/c264060f0e65ea69c2d891525ae835a543f851ca/LICENSE> | publicável | Manter o aviso de licença. | 0 / 0 / 2 | LICENSE na revisão usada é MIT. |
| `splunk-attack-data` | Apache-2.0 | <https://github.com/splunk/attack_data/blob/269c98382624249521c9a985647283a355ac908b/LICENSE> | publicável | Aviso de licença e atribuição. | 1 / 0 / 0 | LICENSE na revisão 269c983 é Apache 2.0. |
| `splunk-attack-data-68ab23c` | Apache-2.0 | <https://github.com/splunk/attack_data/blob/68ab23c7527fa826ed4986c7bab7e3d18ec20eaf/LICENSE> | publicável | Aviso de licença e atribuição. | 73 / 0 / 0 | Mesmo repositório do prefixo anterior, em outra revisão. |
| `splunk-bots-v1` | CC0 1.0 | <https://github.com/splunk/botsv1/blob/97fb3f25d2b6dcdcd4d0aa23864587ac2093a321/README.md> | publicável | Nenhuma. | 31 / 0 / 0 | O README e o LICENSE dedicam os dados ao domínio público (CC0). Confere com o recibo. |
| `splunk-bots-v2-2017` | CC0 1.0 | <https://github.com/splunk/botsv2/blob/47cd23b259b8c22cdf8decd395455cc614e77f49/README.md> | publicável | Nenhuma. | 1 / 0 / 0 | O README e o LICENSE usam CC0. |
| `sr-bh-2020` | CC0 1.0 | <https://doi.org/10.7910/DVN/OGOIXX> | publicável | Nenhuma. | 0 / 25 / 0 | A API do Harvard Dataverse declara “CC0 1.0” e não tem termos extras. Confere com o recibo. |
| `suricata-sample-data-v4` | MIT | <https://github.com/FrankHassanabad/suricata-sample-data/blob/v4.0.0/LICENSE> | publicável | Manter o aviso de licença. | 49 / 0 / 0 | As saídas do Suricata vêm de pcaps do CCDC. Os termos desses pcaps não foram conferidos. |
| `taltech-atomic-evtx-8de5fa8` | Nenhuma encontrada | <https://github.com/arniki/atomic-evtx/tree/8de5fa8f158b4d72d1e3c6f07053162c90ee6238> | desconhecida | Não publicar. | 0 / 21 / 0 | O repositório não tem LICENSE. O README não fala em licença. |
| `usenix-cfdr-hpc4` | Nenhuma encontrada | <https://www.usenix.org/cfdr-data#hpc4> | desconhecida | Não publicar. | 0 / 0 / 3 | A página do CFDR descreve os logs Liberty e Spirit e pede agradecimento. Não declara licença. |
| `virtual-network-threat-92b4a86` | GPL-3.0 | <https://github.com/Marc-Chamorro/virtual-network-threat-detection/blob/92b4a867f1d289fdcc9b2c7e464c8f13e5f61b6b/LICENSE> | publicável com restrição | Copyleft (efeito de SA). | 0 / 0 / 1 | O README diz “Distributed under the GNU GPLv3 License.” |
| `web-server-log-dataset` | MIT | <https://zenodo.org/records/20001206> | publicável | Manter o aviso de licença. | 62 / 0 / 30 | Registro declara `mit-license`. Inclui Organização X (treino) e Organização Y (teste). |
| `windows-apt-2025-v3` | CC BY 4.0 | <https://data.mendeley.com/datasets/b8fmtzvpy8/3> | publicável | Atribuição. | 31 / 0 / 0 | A API do Mendeley Data declara “CC BY 4.0” na versão 3. |
| `witfoo-precinct6-v2.1.0` | Apache-2.0 | <https://huggingface.co/datasets/witfoo/precinct6-cybersecurity/blob/96311c2e29611d8ddbf1c0d59f531f6a362b8233/README.md> | publicável | Aviso de licença e atribuição. | 23 / 0 / 0 | O card da revisão usada declara Apache License 2.0. |
| `yamato-prevention-0845333` | Nenhuma encontrada | <https://github.com/Yamato-Security/hayabusa-sample-evtx/tree/0845333ecb4afcf64c55c6e10946383f168f308c> | desconhecida | Não publicar. | 2 / 0 / 0 | O repositório não tem LICENSE. O README não fala em licença. |

## Lacunas

- **NÃO VERIFICADO.** Nenhuma licença de Fonte ficou sem verificação. Todas as páginas e APIs
  abriram. Só os textos canônicos em creativecommons.org e gnu.org não abriram. Os trechos vieram
  de cópias oficiais.
- **Termos a montante.** Algumas Fontes derivam de dados de terceiros. Não conferi esses termos:
  os pcaps do CCDC no `suricata-sample-data-v4` e a cópia do Loghub no registro L11-LA-03.
- **Rótulo de dataset.** No `revisao.csv`, o registro L11-LA-02 tem um rótulo `dataset` que cita o
  Loghub, mas a proveniência aponta só o arquivo do PSLSS.
- **Mesma origem em dois prefixos.** `locked-shields-2024` e `locked-shields-2024-partners-run`
  vêm do mesmo `eve.log`. `splunk-attack-data` e `splunk-attack-data-68ab23c` vêm do mesmo
  repositório.
