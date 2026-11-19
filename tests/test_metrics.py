import pytest

from soc_triage.metrics import check_ioc_hallucinations, compute_triage_metrics
from soc_triage.schema import NormalizedEvent, SocTriageEvent, Triage


def test_detects_hallucinated_iocs_and_ips():
    parsed = SocTriageEvent(
        log_source="suricata",
        normalized_event=NormalizedEvent(
            src_ip="192.0.2.4",
            dst_ip="198.51.100.8",
            iocs=["Example.invalid", "192.0.2.4", "Missing.invalid", "MISSING.INVALID"],
        ),
        triage=Triage(verdict="suspicious", severity="medium", rationale="Alerta do sensor."),
    )
    result = check_ioc_hallucinations(parsed, "src=192.0.2.4 host=EXAMPLE.INVALID")
    assert result == {"rate": 0.5, "hallucinated": ["Missing.invalid", "198.51.100.8"]}


def test_ioc_rate_is_zero_when_there_are_no_candidates():
    parsed = SocTriageEvent(
        log_source="waf",
        normalized_event=NormalizedEvent(iocs=[]),
        triage=Triage(verdict="benign", severity="info", rationale="Verificação de saúde."),
    )
    assert check_ioc_hallucinations(parsed, "GET /health") == {"rate": 0.0, "hallucinated": []}


def test_calculates_macro_f1_and_alerts_on_benign_events():
    actual = ["malicious", "suspicious", "benign", "benign", "expected_admin", "expected_admin"]
    predicted = ["malicious", "suspicious", "malicious", "benign", "suspicious", "expected_admin"]
    result = compute_triage_metrics(actual, predicted)
    assert result["macro_f1"] == pytest.approx(2 / 3)
    assert result["false_positive_rate"] == 0.5


def test_macro_f1_keeps_all_four_verdicts_and_fpr_can_be_undefined():
    result = compute_triage_metrics(["malicious", "suspicious"], ["malicious", "suspicious"])
    assert result == {"macro_f1": 0.5, "false_positive_rate": None}


def test_confusing_benign_verdicts_does_not_count_as_an_alert():
    result = compute_triage_metrics(["benign"], ["expected_admin"])
    assert result == {"macro_f1": 0.0, "false_positive_rate": 0.0}


@pytest.mark.parametrize("actual,predicted", [([], []), (["benign"], []), (["benign"], ["other"])])
def test_rejects_invalid_metric_inputs(actual, predicted):
    with pytest.raises(ValueError):
        compute_triage_metrics(actual, predicted)
