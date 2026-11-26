# Como estou curando um dataset para triagem de logs de SOC

> Rascunho para revisão editorial

Estou montando um dataset para ensinar um modelo compacto a transformar logs de segurança em JSON estruturado. O objetivo é comparar LoRA e QLoRA com o Gemma 4 E4B-it, medindo se o modelo extrai o que o log realmente contém, distingue rotina de incidente e evita falsos positivos. A etapa atual é a construção da base.

## O que entra em um exemplo

A unidade de revisão é uma janela de evidência, ancorada no último evento disponível para a decisão. Um caso registra fonte, horário, localizador, veredito sugerido, severidade e o que ainda falta confirmar. A anotação do publicador ajuda a encontrar o evento. A evidência que o modelo receberá precisa sustentar o veredito por si mesma.

A rodada cobre 346 itens. São 326 propostas rotuladas pendentes, 19 casos que exigem contexto e uma nova aprovação. A versão v5 tem 43 exemplos aprovados de treino, 11 de validação e nove de teste. O número de exemplos exportados mede o progresso do dataset.

## Um caso em que o formato denunciava o rótulo

No recorte inicial do CasinoLimit, os 35 rótulos maliciosos propostos vinham do Auditd de um bastion. Os 35 suspeitos vinham do log de autenticação de outros hosts. Só o formato do registro já permitia separar os vereditos naquela amostra. Isso criava um caminho para o modelo acertar a resposta sem aprender a avaliar o comportamento. [Fonte original](https://zenodo.org/records/17256954)

A revisão encontrou, no mesmo bastion, uma sessão SSH que antecedeu duas operações Ansible via `sudo`. Auditd, PAM e syslog corroboravam uma janela de manutenção. A sessão entrou uma vez como `expected_admin/info`. Dois recortes privilegiados da mesma sessão foram agrupados para revisão, e um aceite SSH isolado ficou como `precisa_contexto`. Ainda faltam controles do mesmo perfil para parte das ações positivas.

Também apareceu uma diferença de tempo no DEDALE. Um alerta de rede foi corroborado segundos depois por uma sessão administrativa do mesmo fluxo. Essa informação serve à investigação retrospectiva. Uma tarefa de triagem no instante do alerta precisa ser avaliada com a evidência disponível naquele instante. [Documentação do dataset](https://dedale.inria.fr/download.html)

## O que dá para reproduzir

1. Manter arquivo, revisão, licença e hash de origem, com localizadores por caso.
2. Agrupar janelas da mesma sessão ou incidente e manter cada família no mesmo split.
3. Comparar ações suspeitas com rotinas parecidas no mesmo tipo de log. Verificar se host, formato ou período já antecipam a classe.
4. Aprovar veredito e severidade por ID. Usar `null` para campos ausentes e encaminhar casos sem evidência suficiente para revisão.
5. Exportar exemplos aprovados. Validar o JSON, conferir se os IoCs aparecem no log e medir truncamento com o tokenizer da rodada.

O [schema](../../src/soc_triage/schema.py), o [exportador](../../scripts/01_curate_dataset.py) e os [testes](../../tests/) permitem revisar essas regras. Logo antes do treino, a versão do dataset, o prompt, os splits e a revisão do modelo devem estar fixados para comparar com o baseline zero-shot.

Na v5, a primeira representação da janela administrativa excedeu o contexto do experimento. Mantive os identificadores de auditoria na trilha do caso e preservei os eventos necessários na entrada. A maior sequência ficou em 942 de 1.024 tokens. O tokenizer do Gemma examinou os 63 registros dos três splits sem cortar respostas.

Este exemplo sintético ilustra uma decisão com campos ausentes. A entrada contém um registro de automação às `2026-01-11T09:00:00Z`, seguido do encerramento bem-sucedido da ação `ansible_stat` para `root` às `2026-01-11T09:00:01Z`. O contexto da entrada inclui uma janela de manutenção aprovada.

```json
{
  "log_source": "linux_auth",
  "normalized_event": {
    "timestamp": "2026-01-11T09:00:01Z",
    "src_ip": null,
    "dst_ip": null,
    "user": "root",
    "process_or_action": "ansible_stat",
    "iocs": []
  },
  "triage": {
    "verdict": "expected_admin",
    "severity": "info",
    "mitre_technique": null,
    "rationale": "A ação foi concluída durante a janela de manutenção aprovada."
  }
}
```

## Material para a comunidade

A primeira publicação proposta é esta nota acompanhada do contrato JSON, dos testes e de exemplos sintéticos identificados. Um release de dados pode trazer uma ficha do dataset, cobertura por grupo, método de rotulagem e exportação aprovada por fonte. A autorização para redistribuir recortes depende dos termos de cada origem e da revisão de privacidade. Campos ausentes, discordâncias e exclusões ficam documentados junto com as decisões.

Uma contribuição concreta seria revisar um par de eventos parecidos e dizer qual evidência mudaria o veredito. Correções aceitas, reproduções independentes e problemas de cobertura encontrados por quem usar o material são formas de validar o trabalho. Os resultados do modelo serão relatados quando houver avaliação no hold-out.
