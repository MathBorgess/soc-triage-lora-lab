import json

import pytest
from pydantic import ValidationError

from soc_triage.metrics import validate_json_output
from soc_triage.prompts import SYSTEM_PROMPT, build_chat_record
from soc_triage.schema import SocTriageEvent


@pytest.fixture
def event_payload():
    return {
        "log_source": "linux_auth",
        "normalized_event": {
            "timestamp": "2026-01-11T09:00:00Z",
            "src_ip": "192.0.2.4",
            "dst_ip": "10.0.2.15",
            "user": "root",
            "process_or_action": "sshd_failed_login",
            "iocs": ["192.0.2.4"],
        },
        "triage": {
            "verdict": "suspicious",
            "severity": "medium",
            "mitre_technique": "T1110.001",
            "rationale": "Falha de autenticação SSH registrada para root.",
        },
    }


def test_accepts_canonical_json(event_payload):
    parsed = validate_json_output(json.dumps(event_payload))
    assert isinstance(parsed, SocTriageEvent)
    assert parsed.model_dump() == event_payload


@pytest.mark.parametrize("object_name", [None, "normalized_event", "triage"])
def test_rejects_extra_fields(event_payload, object_name):
    target = event_payload if object_name is None else event_payload[object_name]
    target["unexpected"] = "value"
    with pytest.raises(ValidationError, match="extra_forbidden"):
        validate_json_output(json.dumps(event_payload))


@pytest.mark.parametrize("technique", ["T111", "T1110.1", "X1110.001", "T1110.001x"])
def test_rejects_invalid_mitre_technique(event_payload, technique):
    event_payload["triage"]["mitre_technique"] = technique
    with pytest.raises(ValidationError, match="string_pattern_mismatch"):
        validate_json_output(json.dumps(event_payload))


@pytest.mark.parametrize("technique", ["T1110", "T1110.001"])
def test_accepts_technique_and_subtechnique(event_payload, technique):
    event_payload["triage"]["mitre_technique"] = technique
    assert validate_json_output(json.dumps(event_payload)).triage.mitre_technique == technique


def test_accepts_null_for_missing_evidence(event_payload):
    event_payload["normalized_event"] = {
        key: None for key in event_payload["normalized_event"] if key != "iocs"
    } | {"iocs": []}
    event_payload["triage"]["mitre_technique"] = None
    assert validate_json_output(json.dumps(event_payload)).model_dump() == event_payload


def test_optional_fields_default_to_null(event_payload):
    event_payload["normalized_event"] = {"iocs": []}
    del event_payload["triage"]["mitre_technique"]
    parsed = validate_json_output(json.dumps(event_payload))
    assert parsed.normalized_event.timestamp is None
    assert parsed.triage.mitre_technique is None


def test_does_not_coerce_types(event_payload):
    event_payload["normalized_event"]["src_ip"] = 42
    with pytest.raises(ValidationError, match="string_type"):
        validate_json_output(json.dumps(event_payload))


def test_rejects_unknown_verdict(event_payload):
    event_payload["triage"]["verdict"] = "unknown"
    with pytest.raises(ValidationError, match="literal_error"):
        validate_json_output(json.dumps(event_payload))


@pytest.mark.parametrize("wrapper", ["```json\n{}\n```", "{}\nTexto adicional"])
def test_rejects_non_json_output(event_payload, wrapper):
    with pytest.raises(ValidationError, match="json_invalid"):
        validate_json_output(wrapper.format(json.dumps(event_payload)))


def test_builds_chat_for_inference_and_training(event_payload):
    log = "sshd[412] Failed password for root from 192.0.2.4"
    target = json.dumps(event_payload)
    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": log},
    ]
    assert build_chat_record(log) == {"messages": prompt}
    assert build_chat_record(log, target) == {
        "messages": prompt + [{"role": "assistant", "content": target}]
    }
