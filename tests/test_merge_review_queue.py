import csv
import json
import runpy
from pathlib import Path

import pytest

MERGE = runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "07_merge_review_queue.py"))[
    "merge"
]


@pytest.fixture
def review_inputs(tmp_path):
    reference = tmp_path / "existing.csv"
    reference.write_text(
        "id,split,grupo,revisao,incidente\n"
        "t1,train,train-group,human_verdict,train-incident\n"
        "v1,valid,eval-group,human_verdict,eval-incident\n"
    )
    reservations = tmp_path / "reservations.yaml"
    reservations.write_text(
        "valid: []\ntest:\n  - group: echo/one\n    dataset: echo\n", encoding="utf-8"
    )
    proposal = {
        "id": "c1",
        "group": "new/capture",
        "incident": "new/capture/session-one",
        "log_source": "linux_auth",
        "anchor": "00:10:02",
        "evidence": "Sessão abriu após autenticação, com evidência contextual de rotina.",
        "verdict": "benign",
        "severity": "info",
        "rationale": "O contexto sustenta a hipótese de atividade rotineira.",
        "locator": "auth.log, linha 2",
    }
    return reference, reservations, proposal


def write_batch(path, proposals):
    path.write_text(json.dumps({"source": "Fonte nova", "provenance": {}, "proposals": proposals}))
    return path


def test_merge_counts_proposals_separately_from_human_approvals(tmp_path, review_inputs):
    reference, reservations, row = review_inputs
    unknown = {
        **row,
        "id": "c2",
        "locator": "auth.log, linha 3",
        "verdict": "precisa_contexto",
        "severity": None,
    }
    path = write_batch(tmp_path / "source.json", [row, unknown])
    output = tmp_path / "review"
    report = MERGE([path], reference, reservations, output, 500)
    assert report["faltam_aprovados"] == 499
    assert report["propostas_com_rotulo"] == 1
    assert report["precisa_contexto"] == 1
    with (output / "revisao.csv").open(encoding="utf-8-sig") as stream:
        assert all(not row["decisao_humana"] for row in csv.DictReader(stream))


@pytest.mark.parametrize(("group", "incident"), [("echo/two", "fresh"), ("new", "eval-incident")])
def test_merge_rejects_reserved_dataset_and_incident(tmp_path, review_inputs, group, incident):
    reference, reservations, row = review_inputs
    path = write_batch(tmp_path / "source.json", [{**row, "group": group, "incident": incident}])
    output = tmp_path / "review"
    with pytest.raises(ValueError, match="reservado para avaliação"):
        MERGE([path], reference, reservations, output, 500)
    assert not output.exists()
