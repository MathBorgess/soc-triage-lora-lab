import csv
import json
import runpy
from pathlib import Path

import pytest

BUILD_QUEUE = runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "05_propose_dataset.py"))[
    "build_queue"
]
TIMESTAMP = "2026-01-11T09:00:03Z"
MEMBER = "records/auth.jsonl"


def evidence(kind, line, at=TIMESTAMP, member=MEMBER):
    return {"kind": kind, "line": line, "observed_at": at, "member": member}


def candidate(case_id, group, line, kind):
    return {
        "id": case_id,
        "dataset": "fixture-v1",
        "group": group,
        "incident": f"incident-{group}",
        "log_source": "linux_auth",
        "anchor_at": TIMESTAMP,
        "anchor_member": MEMBER,
        "anchor_line": line,
        "evidence": [evidence(kind, line)],
    }


def write_input(tmp_path, *cases):
    path = tmp_path / "input.jsonl"
    path.write_text("".join(f"{json.dumps(case)}\n" for case in cases), encoding="utf-8")
    return path


def test_queue_prioritizes_linux_malicious_and_hard_negatives_across_groups(tmp_path):
    negative = candidate("authorized", "second", 5, "verified_authorized_change")
    negative["evidence"].append(evidence("correlated_anomaly", 4))
    path = write_input(
        tmp_path,
        candidate("repeated", "first", 8, "verified_privileged_misuse"),
        candidate("malicious", "first", 3, "verified_malicious_attempt"),
        candidate("unclear", "third", 6, "observed_event"),
        negative,
    )

    out = tmp_path / "review"
    stats = BUILD_QUEUE(path, out, limit=3)
    assert sorted(p.name for p in out.iterdir()) == ["auditoria.json", "propostas.csv"]
    with (out / "propostas.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["id"] for row in rows] == ["malicious", "authorized", "unclear"]
    assert [row["veredito_proposto"] for row in rows] == ["malicious", "expected_admin", ""]
    assert [row["severidade_proposta"] for row in rows] == ["medium", "info", ""]
    assert rows[1]["negativo_dificil"] == "sim"
    assert rows[2]["status"] == "precisa_contexto"
    assert all(row["decisao_humana"] == "" for row in rows)
    assert stats["grupos_selecionados"] == 3
    assert stats["linux_auth_malicioso"] == 1
    with pytest.raises(FileExistsError, match="novo diretório"):
        BUILD_QUEUE(path, out)


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        (evidence("correlated_anomaly", 2, "2026-01-11T09:00:04Z"), "evidência após"),
        (evidence("correlated_anomaly", 4), "linha de evidência após"),
        (
            evidence("correlated_anomaly", 1, "2026-01-11T06:00:03-03:00", "records/other.jsonl"),
            "ordem indeterminada",
        ),
        (evidence("correlated_anomaly", 1, "2026-01-11T09:00:02"), "timezone"),
        (evidence("correlated_anomaly", 1, "1768122002"), "ISO 8601"),
    ],
)
def test_queue_rejects_evidence_without_established_causal_order(tmp_path, item, expected):
    case = candidate("anchor", "first", 3, "observed_event")
    case["evidence"].append(item)
    out = tmp_path / "review"
    with pytest.raises(ValueError, match=expected):
        BUILD_QUEUE(write_input(tmp_path, case), out)
    assert not out.exists()


def test_queue_abstains_on_conflicting_evidence(tmp_path):
    case = candidate("anchor", "first", 3, "verified_malicious_attempt")
    case["evidence"].append(evidence("verified_authorized_change", 1))
    stats = BUILD_QUEUE(write_input(tmp_path, case), tmp_path / "review")
    assert stats["por_veredito"] == {"precisa_contexto": 1}


def test_queue_rejects_incident_reassigned_to_another_group(tmp_path):
    first = candidate("first", "first", 3, "observed_event")
    second = candidate("second", "second", 4, "observed_event")
    second["incident"] = first["incident"]
    with pytest.raises(ValueError, match="incidente atribuído a grupos diferentes"):
        BUILD_QUEUE(write_input(tmp_path, first, second), tmp_path / "review")


def test_queue_rotates_incidents_and_preserves_local_log_coordinates(tmp_path):
    first = candidate("a-first", "capture-a", 3, "verified_unauthorized_access")
    repeated = candidate("a-repeat", "capture-a", 4, "verified_malicious_attempt")
    second_incident = candidate("a-other", "capture-a", 5, "observed_event")
    second_incident["incident"] = "capture-a/second-episode"
    second_group = candidate("b-first", "capture-b", 3, "verified_routine_activity")
    path = write_input(tmp_path, repeated, second_incident, second_group, first)

    out = tmp_path / "review"
    stats = BUILD_QUEUE(path, out, limit=3)
    with (out / "propostas.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["id"] for row in rows] == ["a-first", "b-first", "a-other"]
    assert rows[0]["veredito_proposto"] == "malicious"
    assert rows[0]["severidade_proposta"] == "high"
    assert stats["incidentes_selecionados"] == 3
