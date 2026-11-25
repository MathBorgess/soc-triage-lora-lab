---
status: accepted
---

# O Guardião é o contrato v2 sobre os Recortes curados

Em 24/11/2026, o responsável pelo estudo decidiu transformar o soc-triage num Guardião que relata ataques e
hipóteses de vulnerabilidade. Um handoff de arquitetura propôs telemetria eBPF como entrada,
com o Shirudo como referência. A decisão manteve como entrada os Recortes de log já curados e
criou um contrato v2 em trilha própria. Assim, os 1.490 alvos verificados pelo responsável
continuam úteis, e a matriz de ablação termina no contrato v1, que fica congelado.

O Shirudo inspira só o Runtime agêntico: um Projetor determinístico antes do modelo, um
modelo que relata e nunca age, contenção por regras e aprovação humana. A documentação dele
não descreve nenhuma interface de IA, então não há formato de entrada ou saída a copiar.

## Considered Options

- **Telemetria eBPF/OTLP como entrada.** Rejeitada. Exigiria um dataset novo e descartaria a
  curadoria. O melhor candidato, o LID-DS, não declara licença para os dados.
- **Pivotar o contrato v1.** Rejeitado. Invalidaria o Run 0 e a v12 como baseline da ablação.
- **Saída com bloco `<reasoning>` em texto livre.** Rejeitada. O alvo v2 continua JSON puro, e
  o raciocínio vai em campos checáveis antes do veredito.

## Consequences

- O alvo v2 é o alvo v1 mais Evidência, Risco de falso positivo e Hipótese de vulnerabilidade.
  A normalização continua no modelo, e a métrica de IoC alucinado segue válida.
- O dataset v2 deriva da v12 e mantém cada exemplo no mesmo split.
- O Runtime agêntico precisa de um Projetor por Modalidade que reproduza os Recortes. Hoje, as
  projeções saem de scripts diferentes em cada lote de curadoria.
