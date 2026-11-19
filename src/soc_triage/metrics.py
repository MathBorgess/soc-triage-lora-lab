"""Métricas determinísticas de formato, evidência e qualidade de triagem."""

from collections.abc import Sequence
from typing import TypedDict, get_args

from sklearn.metrics import f1_score

from soc_triage.schema import SocTriageEvent, Verdict

VERDICTS = get_args(Verdict)
ALERT_VERDICTS = {"malicious", "suspicious"}
BENIGN_VERDICTS = {"benign", "expected_admin"}


class IocCheck(TypedDict):
    rate: float
    hallucinated: list[str]


class TriageMetrics(TypedDict):
    macro_f1: float
    false_positive_rate: float | None


def validate_json_output(raw_text: str) -> SocTriageEvent:
    """Valide a saída inteira. JSON inválido ou fora do schema gera ValidationError."""
    return SocTriageEvent.model_validate_json(raw_text)


def check_ioc_hallucinations(parsed_event: SocTriageEvent, raw_log: str) -> IocCheck:
    """Conte cada candidato distinto por evento, ignorando diferenças de caixa."""
    event = parsed_event.normalized_event
    candidates = [*event.iocs, event.src_ip, event.dst_ip]
    unique: dict[str, str] = {}
    for candidate in candidates:
        if candidate is not None:
            unique.setdefault(candidate.casefold(), candidate)

    searchable_log = raw_log.casefold()
    hallucinated = [value for key, value in unique.items() if key not in searchable_log]
    rate = len(hallucinated) / len(unique) if unique else 0.0
    return {"rate": rate, "hallucinated": hallucinated}


def compute_triage_metrics(y_true: Sequence[Verdict], y_pred: Sequence[Verdict]) -> TriageMetrics:
    """Calcule Macro-F1 nos quatro vereditos e FPR nos logs benignos.

    Um alerta em um log benigno é falso positivo. Sem logs benignos, o FPR é indefinido.
    """
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        raise ValueError("Informe listas não vazias de vereditos com o mesmo tamanho.")
    if (set(y_true) | set(y_pred)) - set(VERDICTS):
        raise ValueError("Todos os vereditos devem pertencer ao schema de triagem.")

    benign_predictions = [
        predicted
        for actual, predicted in zip(y_true, y_pred, strict=True)
        if actual in BENIGN_VERDICTS
    ]
    false_positives = sum(predicted in ALERT_VERDICTS for predicted in benign_predictions)
    fpr = false_positives / len(benign_predictions) if benign_predictions else None
    macro_f1 = f1_score(y_true, y_pred, labels=VERDICTS, average="macro", zero_division=0)
    return {"macro_f1": float(macro_f1), "false_positive_rate": fpr}
