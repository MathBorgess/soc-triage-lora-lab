"""Pontue respostas do modelo no hold-out e agregue as métricas de sucesso do estudo.

As funções são puras. A geração fica em `scripts/03_evaluate.py`.
Uma resposta inválida (JSON fora do schema ou com texto extra) entra nas métricas de triagem
como erro, no veredito `invalid`. A visão "somente válidas" é reportada ao lado da cobertura.
"""

from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import Any, TypedDict, get_args

from pydantic import ValidationError
from sklearn.metrics import f1_score

from soc_triage.metrics import (
    ALERT_VERDICTS,
    BENIGN_VERDICTS,
    VERDICTS,
    check_ioc_hallucinations,
    compute_triage_metrics,
    unique_ioc_candidates,
    validate_json_output,
)
from soc_triage.schema import LogSource

INVALID = "invalid"
LOG_SOURCES = get_args(LogSource)


class Scored(TypedDict):
    valid: bool
    error: str | None
    predicted_verdict: str
    ioc_candidates: int
    ioc_hallucinated: list[str]


def score_response(raw_text: str, raw_log: str) -> Scored:
    """Valide a resposta inteira contra o schema e confira os IoCs no log bruto."""
    try:
        parsed = validate_json_output(raw_text)
    except ValidationError as error:
        first = error.errors()[0]
        reason = f"{first['type']}:{'.'.join(str(part) for part in first['loc'])}"
        return Scored(
            valid=False,
            error=reason,
            predicted_verdict=INVALID,
            ioc_candidates=0,
            ioc_hallucinated=[],
        )
    check = check_ioc_hallucinations(parsed, raw_log)
    return Scored(
        valid=True,
        error=None,
        predicted_verdict=parsed.triage.verdict,
        ioc_candidates=len(unique_ioc_candidates(parsed)),
        ioc_hallucinated=check["hallucinated"],
    )


def strict_triage_metrics(y_true: Sequence[str], y_pred: Sequence[str]) -> dict[str, Any]:
    """Macro-F1 nos quatro vereditos e FPR, com respostas inválidas contadas como erro.

    Um `invalid` em um log benigno não é alerta, então não vira falso positivo.
    """
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("Informe listas não vazias com o mesmo tamanho.")
    benign = [pred for true, pred in zip(y_true, y_pred, strict=True) if true in BENIGN_VERDICTS]
    false_positives = sum(pred in ALERT_VERDICTS for pred in benign)
    macro_f1 = f1_score(y_true, y_pred, labels=VERDICTS, average="macro", zero_division=0)
    return {
        "macro_f1": float(macro_f1),
        "false_positive_rate": false_positives / len(benign) if benign else None,
        "benign_examples": len(benign),
        "false_positives": false_positives,
    }


def _group_metrics(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    valid = [r for r in records if r["valid"]]
    true = [r["true_verdict"] for r in records]
    pred = [r["predicted_verdict"] for r in records]
    candidates = sum(r["ioc_candidates"] for r in valid)
    hallucinated = sum(len(r["ioc_hallucinated"]) for r in valid)
    result: dict[str, Any] = {
        "examples": len(records),
        "valid_responses": len(valid),
        "pydantic_pass_rate": len(valid) / len(records),
        "ioc_candidates": candidates,
        "ioc_hallucinated": hallucinated,
        "ioc_hallucination_rate": hallucinated / candidates if candidates else None,
        "triage_strict": strict_triage_metrics(true, pred),
    }
    if valid:
        result["triage_valid_only"] = compute_triage_metrics(
            [r["true_verdict"] for r in valid], [r["predicted_verdict"] for r in valid]
        )
    return result


def summarize(records: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Agregue registros com valid, true_verdict, predicted_verdict e contagens de IoC."""
    if not records:
        raise ValueError("Nenhum registro para resumir.")
    summary = _group_metrics(records)
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_source[record["true_log_source"]].append(record)
    summary["by_log_source"] = {
        source: _group_metrics(by_source[source]) for source in LOG_SOURCES if by_source[source]
    }
    summary["confusion"] = {
        f"{true}->{pred}": count
        for (true, pred), count in sorted(
            Counter((r["true_verdict"], r["predicted_verdict"]) for r in records).items()
        )
    }
    summary["errors"] = dict(Counter(r["error"] for r in records if r["error"]).most_common())
    summary["finish_reasons"] = dict(Counter(r.get("finish_reason") for r in records))
    return summary


def meets_targets(summary: dict[str, Any]) -> dict[str, bool | None]:
    """Compare com os limiares do AGENTS.md. None indica que a métrica é indefinida."""
    rate = summary["ioc_hallucination_rate"]
    return {
        "pydantic_pass_rate_ge_98": summary["pydantic_pass_rate"] >= 0.98,
        "ioc_hallucination_rate_lt_1": None if rate is None else rate < 0.01,
    }
