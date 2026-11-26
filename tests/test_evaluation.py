import json

import pytest

from soc_triage.evaluation import (
    INVALID,
    meets_targets,
    score_response,
    strict_triage_metrics,
    summarize,
)

LOG = "Failed password for root from 203.0.113.9 port 22"


def response(verdict="malicious", iocs=("203.0.113.9",), src_ip="203.0.113.9"):
    return json.dumps(
        {
            "log_source": "linux_auth",
            "normalized_event": {
                "timestamp": None,
                "src_ip": src_ip,
                "dst_ip": None,
                "user": "root",
                "process_or_action": "sshd",
                "iocs": list(iocs),
            },
            "triage": {
                "verdict": verdict,
                "severity": "high",
                "mitre_technique": "T1110",
                "rationale": "Falha de senha.",
            },
        }
    )


def record(text, true_verdict="malicious", source="linux_auth"):
    scored = score_response(text, LOG)
    return {
        "true_log_source": source,
        "true_verdict": true_verdict,
        "finish_reason": "stop",
        **scored,
    }


def test_valid_response_is_scored_and_iocs_are_checked_literally():
    scored = score_response(response(iocs=("203.0.113.9", "198.51.100.1")), LOG)
    assert scored["valid"] and scored["predicted_verdict"] == "malicious"
    assert scored["ioc_candidates"] == 2
    assert scored["ioc_hallucinated"] == ["198.51.100.1"]


@pytest.mark.parametrize(
    "text",
    ["```json\n" + response() + "\n```", "Resposta: " + response(), "{}", "", '{"log_source": 1}'],
)
def test_text_around_the_json_or_a_bad_schema_is_invalid(text):
    scored = score_response(text, LOG)
    assert scored["valid"] is False
    assert scored["predicted_verdict"] == INVALID
    assert scored["error"]


def test_invalid_responses_count_as_errors_but_not_as_false_positives():
    result = strict_triage_metrics(
        ["benign", "benign", "malicious"], [INVALID, "malicious", "malicious"]
    )
    assert result["false_positives"] == 1
    assert result["false_positive_rate"] == 0.5
    assert result["macro_f1"] < 1


def test_summary_reports_coverage_and_pooled_ioc_rate():
    records = [
        record(response()),
        record(response(iocs=("203.0.113.9", "missing.invalid"))),
        record("not json", true_verdict="benign"),
    ]
    summary = summarize(records)
    assert summary["pydantic_pass_rate"] == pytest.approx(2 / 3)
    assert summary["ioc_candidates"] == 3 and summary["ioc_hallucinated"] == 1
    assert summary["ioc_hallucination_rate"] == pytest.approx(1 / 3)
    assert summary["triage_valid_only"]["false_positive_rate"] is None
    assert summary["by_log_source"]["linux_auth"]["examples"] == 3
    assert summary["errors"]
    assert meets_targets(summary) == {
        "pydantic_pass_rate_ge_98": False,
        "ioc_hallucination_rate_lt_1": False,
    }


def test_targets_are_undefined_without_ioc_candidates():
    summary = summarize([record(response(iocs=(), src_ip=None))])
    assert summary["ioc_hallucination_rate"] is None
    assert meets_targets(summary)["ioc_hallucination_rate_lt_1"] is None


def test_empty_summary_is_rejected():
    with pytest.raises(ValueError):
        summarize([])
