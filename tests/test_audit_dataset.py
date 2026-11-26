import csv
import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "06_audit_dataset.py"
AUDIT = runpy.run_path(str(SCRIPT))["audit"]
FIELDS = ("split", "id", "grupo", "origem", "revisao", "veredito", "severidade")


def write_review(path, rows, *, include_incident=False):
    columns = (*FIELDS, "dataset", "incidente") if include_incident else FIELDS
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(rows)


def test_audit_reports_tallies_gaps_and_source_concentration(tmp_path):
    path = tmp_path / "review.csv"
    rows = [
        ("train", "t1", "group-1", "linux_auth", "human_verdict", "benign", "info", "a", "case-1"),
        ("train", "t2", "group-1", "apache", "human_verdict", "malicious", "high", "a", "case-1"),
        ("train", "t3", "group-2", "apache", "human_verdict", "benign", "info", "b", ""),
        ("valid", "v1", "group-3", "linux_auth", "proposed", "malicious", "high", "a", "case-2"),
        (
            "test",
            "h1",
            "group-4",
            "linux_auth",
            "human_verdict",
            "malicious",
            "high",
            "a",
            "case-3",
        ),
    ]
    write_review(path, rows, include_incident=True)
    report = AUDIT(path)

    assert report["progress"] == {
        "target_approved_train": 2_000,
        "approved_train": 3,
        "remaining": 1_997,
        "percent": 0.15,
    }
    train = report["splits"]["train"]
    assert train["by_approval"]["approved"] == {
        "rows": 3,
        "groups": 2,
        "named_incidents": 1,
        "rows_with_incident": 2,
    }
    assert train["incidents"][0]["approved"]["rows"] == 2
    assert train["approved_concentration"]["dataset"][0] == {
        "source": "a",
        "rows": 2,
        "share": 0.6667,
    }
    assert train["gaps"] == ["approved_malicious_linux_auth"]
    valid = report["splits"]["valid"]
    assert valid["coverage"]["linux_auth"]["malicious"]["proposed"]["groups"] == 1
    assert valid["gaps"] == ["approved_malicious_linux_auth"]
    assert report["splits"]["test"]["gaps"] == []


@pytest.mark.parametrize(
    ("second_id", "second_group", "second_incident", "message"),
    [
        ("t1", "group-2", "case-2", "ID duplicado"),
        ("v1", "group-1", "case-2", "grupo compartilhado"),
        ("v1", "group-2", "case-1", "incidente compartilhado"),
    ],
)
def test_audit_rejects_cross_split_reuse(
    tmp_path, second_id, second_group, second_incident, message
):
    path = tmp_path / "review.csv"
    rows = [
        ("train", "t1", "group-1", "linux_auth", "human_verdict", "benign", "info", "a", "case-1"),
        (
            "valid",
            second_id,
            second_group,
            "apache",
            "proposed",
            "benign",
            "info",
            "b",
            second_incident,
        ),
    ]
    write_review(path, rows, include_incident=True)
    with pytest.raises(ValueError, match=message):
        AUDIT(path)


def test_cli_accepts_original_review_columns_and_preserves_existing_output(tmp_path):
    path = tmp_path / "review.csv"
    write_review(
        path, [("train", "t1", "group-1", "linux_auth", "human_verdict", "benign", "info")]
    )
    output = tmp_path / "audit.json"
    command = [sys.executable, str(SCRIPT), "--input", str(path), "--output", str(output)]
    subprocess.run(command, check=True, text=True, capture_output=True)
    original = output.read_text(encoding="utf-8")
    assert json.loads(original)["splits"]["train"]["named_incidents"] == 0

    second_attempt = subprocess.run(command, check=False, text=True, capture_output=True)
    assert second_attempt.returncode == 2
    assert output.read_text(encoding="utf-8") == original
