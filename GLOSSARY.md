# SOC Triage LoRA Lab

Laboratório de fine-tuning que ensina um modelo pequeno a triar logs de SOC. O contrato v1
sustenta o estudo de ablação. O contrato v2 prepara o Guardião sobre os mesmos dados curados.

## Entrada

**Recorte**:
Projeção curada de uma janela de log de uma Modalidade, que termina na Âncora. É a entrada do modelo e tem duas partes: Contexto e Registro.
_Avoid_: telemetria, evento de telemetria, envelope, log bruto

**Contexto**:
Parte confiável do Recorte, escrita pelo Projetor ou pela curadoria: correlações, mudanças aprovadas, linha de base e histórico. Só o Contexto pode justificar trocar um Alerta por benign ou expected_admin.
_Avoid_: metadados, evidência confiável, enriquecimento

**Registro**:
Parte não confiável do Recorte: o conteúdo do log, que um atacante pode controlar. Pode conter linhas literais, contagens e sinais estruturais. Nada no Registro é instrução para o Guardião.
_Avoid_: payload, observable, log bruto

**Âncora**:
Linha do Recorte que o rótulo avalia. Eventos posteriores à Âncora não contam.
_Avoid_: evento-alvo, linha principal

**Modalidade**:
Origem do log: sysmon, linux_auth, apache, suricata, waf ou audit. A Modalidade audit reúne os Exemplos sintéticos do opensec-triage, de qualquer fonte declarada.
_Avoid_: fonte (reservado ao dataset de origem), tipo de log

**Fonte**:
Dataset de origem de um Recorte, com licença, revisão e hash registrados. Uma fonte nova é a que não aparece no treino.
_Avoid_: origem, base

**Sinal**:
Indício hostil que o Projetor detecta no Registro por regra versionada, antes do modelo, como uma assinatura do Suricata, um bloqueio do WAF ou uma rajada de falhas de SSH. Não cria Alerta; só exige justificativa para um Rebaixamento.
_Avoid_: alerta, detecção, sinal estrutural (texto do Registro)

**Recorte incompleto**:
Recorte cuja janela o Projetor cortou ou em que faltam campos. O Contexto declara a falta.
_Avoid_: truncado, ambíguo

## Saída

**Veredito**:
Classe da triagem, que mede hostilidade: malicious, suspicious, benign ou expected_admin.
_Avoid_: MALICIOUS_CONFIRMED, confirmado, BENIGN, authorised_testing, misconfiguration, unknown

**Alerta**:
Veredito malicious ou suspicious.

**Falso positivo**:
Alerta num Recorte cujo Veredito de referência é benign ou expected_admin.

**Severidade**:
Gravidade do Recorte: critical, high, medium, low ou info.
_Avoid_: risco, prioridade

**Evidência**:
Trechos literais do Recorte que sustentam o que o modelo afirma.
_Avoid_: justificativa livre, raciocínio

**Risco de falso positivo**:
Grau (low, medium ou high) do dano de tratar como hostil um Recorte que se revele legítimo.
_Avoid_: confiança, confidence_score

**Relato**:
Saída do Guardião para um Recorte: a triagem e, quando o Recorte mostra uma fraqueza, uma Hipótese de vulnerabilidade.
_Avoid_: triage_output, finding, alerta

**Hipótese de vulnerabilidade**:
Parte do Relato que nomeia a fraqueza (CWE), o componente afetado e a Evidência, quando o Recorte mostra a fraqueza sendo explorada ou exposta, como numa configuração que abre acesso. Mede fraqueza, enquanto o Veredito mede hostilidade. É uma hipótese, não uma confirmação.
_Avoid_: vulnerabilidade confirmada, bug report, misconfiguration como veredito

## Agente e runtime

**Guardião**:
Agente que lê um Recorte de log de SOC, pode consultar logs locais com Ferramentas de leitura e emite um único Relato. Ele relata e nunca age: não altera o sistema e não propõe contenção.
_Avoid_: SOC-Triage-Lab SLM, motor de triagem, shield, Investigador, segundo agente

**Ferramenta de leitura**:
Função determinística e somente-leitura que o Guardião pode chamar para consultar logs locais, como a árvore de processos de um host ou as falhas de SSH de um usuário numa janela. Nunca muda o sistema.
_Avoid_: ação, ferramenta de resposta, consulta livre ao SIEM

**Runtime agêntico**:
Sistema que roda localmente nas máquinas monitoradas: projeta logs em Recortes, executa o Guardião e suas Ferramentas de leitura e envia os Relatos ao SOC, onde Propostas de contenção aguardam aprovação humana. O Shirudo é a inspiração.
_Avoid_: plano de raciocínio, motor fechado

**Projetor**:
Componente determinístico do Runtime agêntico que transforma o log de uma Modalidade num Recorte no mesmo formato usado no treino.
_Avoid_: decoder, parser de telemetria

**Rebaixamento**:
Relato não-Alerta para um Recorte com Sinal. Só vale quando alguma Evidência do Relato está literalmente no Contexto; senão o caso vai para revisão humana.
_Avoid_: downgrade, supressão

**Diário de inferências**:
Histórico append-only do Runtime agêntico, com uma linha por Recorte, que liga o Recorte, o Sinal, o adaptador, o Relato, a regra aplicada e a decisão humana.
_Avoid_: registro, log de inferência, ledger

**Proposta de contenção**:
Ação que o Runtime agêntico deriva de um Relato por regras determinísticas e versionadas. Só vale depois da aprovação humana.
_Avoid_: shield, upatch, recommended_shield

## Dados e liberação

**Contrato**:
Conjunto versionado de schema, prompt e versão do dataset que define a entrada e a saída do modelo. O v1 é a triagem do estudo de ablação. O v2 é o Relato do Guardião.
_Avoid_: formato, template

**Mutação**:
Variante de um Recorte real com o payload alterado. Herda o rótulo do original e nunca entra no teste.
_Avoid_: amostra sintética, dado gerado

**Exemplo sintético**:
Exemplo escrito do zero, sem log real por trás, como os do opensec-triage. Nunca entra no teste real.
_Avoid_: amostra sintética, dado gerado, golden set

**Família**:
Conjunto de Exemplos sintéticos gerados do mesmo perfil. É a unidade de aprovação dessa fonte: o responsável aprova a regra da Família e uma amostra das linhas.
_Avoid_: template, molde

**Teste real**:
Split de teste com Recortes reais da v12, a maioria de fontes novas. É onde o Guardião precisa superar o Rival.
_Avoid_: golden set, hold-out sintético

**Rival**:
O adaptador infosecn1nja/soc-triage-nemotron-bolt-e4b-lora, que o Guardião precisa superar no Teste real: Macro-F1 maior, FPR igual ou menor e não mais malicious perdidos.
_Avoid_: baseline (reservado ao Run 0), concorrente

**Suíte adversarial**:
Conjunto de avaliação separado dos splits, com injeções de prompt no Registro de Recortes reais, em moldes que o treino não contém. Mede injeções que rebaixam e que inflam Alertas. É um teste de regressão, não uma prova de robustez.
_Avoid_: teste de injeção, red team

**Liberação**:
Aprovação escrita do responsável pelo estudo para um adaptador, vinculada aos hashes do adaptador, dos dados e da configuração e selada por uma assinatura que o Runtime agêntico verifica ao carregar o adaptador.
_Avoid_: deploy, publicação
