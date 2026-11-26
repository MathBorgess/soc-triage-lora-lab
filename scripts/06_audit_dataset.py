"""Meça a cobertura e as lacunas dos splits a partir do CSV de revisão."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import get_args

from soc_triage.schema import LogSource, Severity, Verdict

SPLITS = ("train", "valid", "test")
APPROVAL_STATES = {"human_verdict": "approved", "proposed": "proposed"}
REQUIRED_COLUMNS = {"split", "id", "grupo", "origem", "revisao", "veredito", "severidade"}
ALLOWED_VALUES = {
    "split": SPLITS,
    "origem": get_args(LogSource),
    "revisao": APPROVAL_STATES,
    "veredito": get_args(Verdict),
    "severidade": get_args(Severity),
}


@dataclass(frozen=True)
class ReviewRow:
    split: str
    id: str
    group: str
    log_source: str
    approval: str
    verdict: str
    dataset: str
    incident: str


def read_review(path: Path) -> list[ReviewRow]:
    rows = []
    ids: set[str] = set()
    group_splits: dict[str, str] = {}
    incident_splits: dict[str, str] = {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        fields = reader.fieldnames or []
        missing = REQUIRED_COLUMNS - set(fields)
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes no CSV: {', '.join(sorted(missing))}")
        if len(fields) != len(set(fields)):
            raise ValueError("O CSV contém colunas repetidas")

        for record in reader:
            if None in record or any(value is None for value in record.values()):
                raise ValueError(f"Linha {reader.line_num}: quantidade de colunas incorreta")
            values = {name: value.strip() for name, value in record.items()}
            for name, allowed in ALLOWED_VALUES.items():
                if values[name] not in allowed:
                    raise ValueError(f"Linha {reader.line_num}: valor inválido em {name}")
            row = ReviewRow(
                split=values["split"],
                id=values["id"],
                group=values["grupo"],
                log_source=values["origem"],
                approval=APPROVAL_STATES[values["revisao"]],
                verdict=values["veredito"],
                dataset=values.get("dataset", ""),
                incident=values.get("incidente", ""),
            )
            if not row.id or not row.group:
                raise ValueError(f"Linha {reader.line_num}: ID ou grupo ausente")
            if row.id in ids:
                raise ValueError(f"Linha {reader.line_num}: ID duplicado")
            if group_splits.setdefault(row.group, row.split) != row.split:
                raise ValueError(f"Linha {reader.line_num}: grupo compartilhado entre splits")
            if row.incident and incident_splits.setdefault(row.incident, row.split) != row.split:
                raise ValueError(f"Linha {reader.line_num}: incidente compartilhado entre splits")
            ids.add(row.id)
            rows.append(row)
    return rows


def sample_counts(rows: list[ReviewRow]) -> dict:
    annotated = [row for row in rows if row.incident]
    return {
        "rows": len(rows),
        "groups": len({row.group for row in rows}),
        "named_incidents": len({row.incident for row in annotated}),
        "rows_with_incident": len(annotated),
    }


def approval_counts(rows: list[ReviewRow]) -> dict:
    return {
        approval: sample_counts([row for row in rows if row.approval == approval])
        for approval in APPROVAL_STATES.values()
    }


def concentration(values: Counter[str]) -> list[dict]:
    total = values.total()
    return [
        {"source": name or None, "rows": count, "share": round(count / total, 4)}
        for name, count in sorted(values.items(), key=lambda item: (-item[1], item[0]))
    ]


def summarize_split(rows: list[ReviewRow]) -> dict:
    coverage = defaultdict(lambda: defaultdict(list))
    incidents = defaultdict(list)
    for row in rows:
        coverage[row.log_source][row.verdict].append(row)
        if row.incident:
            incidents[row.incident].append(row)

    approved = [row for row in rows if row.approval == "approved"]
    priority = approval_counts(coverage["linux_auth"]["malicious"])
    return {
        **sample_counts(rows),
        "by_approval": approval_counts(rows),
        "coverage": {
            source: {
                verdict: approval_counts(examples) for verdict, examples in sorted(verdicts.items())
            }
            for source, verdicts in sorted(coverage.items())
        },
        "incidents": [
            {
                "datasets": sorted({row.dataset for row in examples if row.dataset}),
                "incident": incident,
                **approval_counts(examples),
            }
            for incident, examples in sorted(incidents.items())
        ],
        "approved_concentration": {
            "dataset": concentration(Counter(row.dataset for row in approved)),
            "group": concentration(Counter(row.group for row in approved)),
            "log_source": concentration(Counter(row.log_source for row in approved)),
        },
        "gaps": ["approved_malicious_linux_auth"] if priority["approved"]["rows"] == 0 else [],
    }


def audit(path: Path, target_train: int = 2_000) -> dict:
    if target_train <= 0:
        raise ValueError("A meta deve ser maior que zero")

    rows = read_review(path)
    splits = {
        split: summarize_split([row for row in rows if row.split == split]) for split in SPLITS
    }
    approved_train = splits["train"]["by_approval"]["approved"]["rows"]
    return {
        "by_approval": approval_counts(rows),
        "progress": {
            "target_approved_train": target_train,
            "approved_train": approved_train,
            "remaining": max(0, target_train - approved_train),
            "percent": round(100 * approved_train / target_train, 2),
        },
        "splits": splits,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="CSV exportado para revisão.")
    parser.add_argument("--target-train", type=int, default=2_000, help="Meta de treino aprovado.")
    parser.add_argument("--output", type=Path, help="Novo relatório JSON. O padrão é stdout.")
    args = parser.parse_args()
    try:
        report = json.dumps(audit(args.input, args.target_train), indent=2, ensure_ascii=False)
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(report + "\n")
        else:
            print(report)
    except (OSError, ValueError, csv.Error) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
