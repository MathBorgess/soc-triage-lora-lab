import csv
import io
import json
import runpy
import sqlite3
import tarfile
from contextlib import closing
from pathlib import Path
from zipfile import ZipFile

import pytest

EXPORT = runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "01_curate_dataset.py"))[
    "export"
]
MEMBER = "gather/example/logs/auth.log"


@pytest.fixture
def split_fixture(tmp_path):
    manifest = {}
    for split in ("train", "valid", "test"):
        source = f"fixture-{split}"
        archive_name = f"{split}.zip"
        input_text = f"Evento distinto {source} da sessão rotineira de autenticação."
        with ZipFile(tmp_path / archive_name, "w") as archive:
            archive.writestr(MEMBER, input_text + "\n")
        candidate = {
            "id": source,
            "group": source,
            "archive": archive_name,
            "member": MEMBER,
            "lines": [1],
            "approval": "human_verdict" if split == "train" else "proposed",
            "input": input_text,
            "target": {
                "log_source": "linux_auth",
                "normalized_event": {"iocs": []},
                "triage": {
                    "verdict": "benign",
                    "severity": "info",
                    "rationale": "A sessão corresponde a atividade rotineira.",
                },
            },
            "review_notes": "Anotação separada para o revisor.",
        }
        records = f"source-{split}.jsonl"
        (tmp_path / records).write_text(json.dumps(candidate) + "\n", encoding="utf-8")
        manifest[split] = {"group": source, "records": records, "archive": archive_name}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path, tmp_path / "out"


def test_export_keeps_review_notes_out_of_chat(split_fixture):
    manifest, output = split_fixture
    stats = EXPORT(manifest, output)
    test_record = json.loads((output / "test.jsonl").read_text(encoding="utf-8"))
    assert set(test_record) == {"messages"}
    assert [item["role"] for item in test_record["messages"]] == ["system", "user", "assistant"]
    assert "revisor" not in json.dumps(test_record, ensure_ascii=False)
    assert stats["splits"]["test"]["approval_counts"] == {"proposed": 1}


def test_export_rejects_exact_source_line_overlap_even_if_inputs_differ(split_fixture):
    manifest, output = split_fixture
    with ZipFile(manifest.parent / "train.zip") as original:
        duplicated_line = original.read(MEMBER)
    with ZipFile(manifest.parent / "test.zip", "w") as archive:
        archive.writestr(MEMBER, duplicated_line)
    with pytest.raises(ValueError, match="linha de origem idêntica"):
        EXPORT(manifest, output)
    assert not output.exists()


def test_export_rejects_unprovided_ioc_before_creating_outputs(split_fixture):
    manifest, output = split_fixture
    path = manifest.parent / "source-valid.jsonl"
    row = json.loads(path.read_text(encoding="utf-8"))
    row["target"]["normalized_event"]["iocs"] = ["192.0.2.25"]
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="IoC do alvo ausente"):
        EXPORT(manifest, output)
    assert not output.exists()


def test_export_checks_normalized_ioc_against_original_lines(split_fixture):
    manifest, output = split_fixture
    path = manifest.parent / "source-valid.jsonl"
    row = json.loads(path.read_text(encoding="utf-8"))
    row["target"]["normalized_event"]["iocs"] = ["192.0.2.25"]
    row["input"] += " IP=192.0.2.25"
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="IoC do alvo ausente nas linhas de origem"):
        EXPORT(manifest, output)
    assert not output.exists()


def test_export_joins_approved_sources_from_separate_groups(split_fixture):
    manifest, output = split_fixture
    config = json.loads(manifest.read_text(encoding="utf-8"))
    path = manifest.parent / "source-train.jsonl"
    row = json.loads(path.read_text(encoding="utf-8"))
    row.update(
        id="second-train",
        group="second-train",
        member="linux/auth",
        dataset="second-dataset",
        incident="second-dataset/episode-1",
        anchor_line=1,
        input="Segunda captura, sessão de rotina.",
    )
    with ZipFile(manifest.parent / row["archive"], "a") as archive:
        archive.writestr(row["member"], row["input"] + "\n")
    (manifest.parent / "second-train.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    config["train"] = [
        config["train"],
        {"group": row["group"], "records": "second-train.jsonl", "archive": row["archive"]},
    ]
    manifest.write_text(json.dumps(config), encoding="utf-8")
    stats = EXPORT(manifest, output)
    assert stats["splits"]["train"]["groups"] == ["fixture-train", "second-train"]
    assert stats["splits"]["train"]["count"] == 2
    assert "second-dataset/episode-1" in (output / "revisao.csv").read_text(encoding="utf-8")
    assert "second-dataset" not in (output / "train.jsonl").read_text(encoding="utf-8")


def test_export_rejects_shared_incident_across_distinct_groups(split_fixture):
    manifest, output = split_fixture
    for split in ("train", "test"):
        path = manifest.parent / f"source-{split}.jsonl"
        row = json.loads(path.read_text(encoding="utf-8"))
        row["incident"] = "fixture/episode-replicated"
        path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="incidente atribuído a mais de um split"):
        EXPORT(manifest, output)
    assert not output.exists()


def test_approved_export_rejects_unreviewed_holdout(split_fixture):
    manifest, output = split_fixture
    with pytest.raises(ValueError, match="valid exige veredito humano aprovado"):
        EXPORT(manifest, output, require_approved=True)
    assert not output.exists()


@pytest.mark.parametrize("evidence_format", ["tar", "sqlite_events", "text", "csv_records"])
def test_export_reads_original_coordinates_in_approved_sources(split_fixture, evidence_format):
    manifest, output = split_fixture
    config = json.loads(manifest.read_text(encoding="utf-8"))
    path = manifest.parent / "source-train.jsonl"
    row = json.loads(path.read_text(encoding="utf-8"))
    original = "Registro de origem com IOC 192.0.2.7."
    row["input"] += " 192.0.2.7"
    row["target"]["normalized_event"]["iocs"] = ["192.0.2.7"]
    source = config["train"]
    source["evidence_format"] = evidence_format

    if evidence_format == "tar":
        source["archive"] = "auth.tar.gz"
        row.update(member="auth.log", lines=[2], anchor_line=2)
        data = ("Início\n" + original + "\n").encode()
        with tarfile.open(manifest.parent / source["archive"], "w:gz") as archive:
            member = tarfile.TarInfo("auth.log")
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
    elif evidence_format == "sqlite_events":
        source["archive"] = "campaigns.db"
        row.update(member="events", lines=[501], anchor_line=501)
        with closing(sqlite3.connect(manifest.parent / source["archive"])) as db:
            db.execute("CREATE TABLE events (id INTEGER PRIMARY KEY, raw_line TEXT)")
            db.execute("INSERT INTO events VALUES (?, ?)", (501, original))
            db.commit()
    elif evidence_format == "csv_records":
        source["archive"] = "host.csv"
        row.update(member=source["archive"], lines=[2], anchor_line=2)
        with (manifest.parent / source["archive"]).open("w", newline="", encoding="utf-8") as file:
            csv.writer(file).writerows(
                [("id", "event"), ("1", "Evento anterior\ncom duas linhas"), ("2", original)]
            )
    else:
        source.update(archive="sysmon.log", reverse_lines=True)
        row.update(member="sysmon.log", lines=[2, 1], anchor_line=1)
        (manifest.parent / source["archive"]).write_text(original + "\nContexto anterior\n")

    row["archive"] = source["archive"]
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    manifest.write_text(json.dumps(config), encoding="utf-8")
    stats = EXPORT(manifest, output)
    assert stats["splits"]["train"]["literal_values_checked"] == 1
