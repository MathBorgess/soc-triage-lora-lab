---
status: accepted
---

# Nenhum Relato fecha sozinho, e a carga cognitiva só se afirma com Estudo com analistas

Em 26/11/2026, o responsável pelo estudo decidiu como o artigo trata a Carga no analista, que é
o resultado principal. A base está na seção 5 da
[revisão 03](../pesquisa/03-rl-ferramentas-e-medicao.md).

## Decisão

- **Todo Relato chega ao SOC.** Os Relatos não-Alerta entram na Fila de confirmação, que o
  analista confirma em lote. A carga dessa fila entra na medida da Carga no analista.
- **Os indicadores automáticos são o resultado quantitativo principal.** Eles medem a carga de
  triagem que o Runtime agêntico encaminha ao SOC.
- **A carga cognitiva só se afirma com o Estudo com analistas.** O piloto é submetido ao CEP da
  instituição do responsável e compara, de forma pareada, a triagem com e sem Relato. Mede
  NASA-TLX ou RTLX, tempo por Recorte e Erros plantados nos dois sentidos.
- **Sem aprovação do CEP a tempo,** o artigo fala só em "carga de triagem encaminhada ao SOC".

## Considered Options

- **Fechar sozinho os Relatos benignos com Contexto e sem Sinal.** Rejeitada. Reduziria mais a
  carga, mas o viés de automação pesa mais na direção benigna. No único ensaio controlado
  encontrado, 46% dos analistas que viam o veredito do agente não pegaram o falso negativo
  plantado, contra 17% sem o veredito (G-6, preprint do fornecedor).
- **Afirmar redução de carga cognitiva só com indicadores automáticos.** Rejeitada. Eles medem o
  trabalho encaminhado, não o esforço mental do analista (G-1, G-2).
- **Dispensa do CEP pela Res. CNS 510/2016.** Rejeitada como premissa. Pelo texto, um
  experimento com triagem, NASA-TLX e Erros plantados não cabe nos casos dispensados. Quem decide
  o enquadramento é o CEP (G-20).

## Consequences

- O ganho medido de carga é menor do que seria com fechamento automático. Em troca, a supervisão
  humana fica integral, o que é parte da tese.
- A afirmação mais forte do artigo depende do calendário do CEP.
- Os Erros plantados medem a confiança indevida no Relato. Os resultados nos dois sentidos são
  publicados, mesmo se forem desfavoráveis.
- A Fila de confirmação precisa de um formato de lote que o Runtime agêntico e o Estudo com
  analistas usem igual.
