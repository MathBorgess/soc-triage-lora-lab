"""Consolide propostas de curadoria em um lote para adjudicação humana."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from soc_triage.schema import LogSource, Severity, Verdict


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    id: str = Field(min_length=1)
    group: str = Field(min_length=1)
    incident: str = Field(min_length=1)
    log_source: LogSource
    anchor: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
    verdict: Verdict | Literal["precisa_contexto"]
    severity: Severity | None
    rationale: str = Field(min_length=1)
    locator: str = Field(min_length=1)

    @model_validator(mode="after")
    def check_verdict_and_severity(self) -> "Proposal":
        if (self.verdict == "precisa_contexto") != (self.severity is None):
            raise ValueError("Somente precisa_contexto deve ficar sem severidade.")
        return self


class SourceBatch(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    source: str = Field(min_length=1)
    provenance: dict
    proposals: list[Proposal] = Field(min_length=1)


def spreadsheet_cell(value: str) -> str:
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def merge(
    sources: list[Path],
    reference: Path,
    reservations: Path,
    output: Path,
    target_train: int,
) -> dict:
    if target_train <= 0 or output.exists() or output.is_symlink():
        raise ValueError("Informe meta positiva e diretório de saída novo.")

    with reference.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        fields = {"id", "split", "grupo", "revisao", "incidente"}
        if not fields <= set(reader.fieldnames or ()):
            raise ValueError("O CSV de referência precisa ser o relatório do exportador de splits.")
        existing = list(reader)
    policy = yaml.safe_load(reservations.read_text(encoding="utf-8"))
    reserved_groups = {row["grupo"] for row in existing if row["split"] in ("valid", "test")}
    reserved_datasets = set()
    for split in ("valid", "test"):
        for entry in policy[split]:
            reserved_groups.add(entry["group"])
            reserved_datasets.add(entry["dataset"])
    reserved_incidents = {
        row["incidente"]
        for row in existing
        if row["split"] in ("valid", "test") and row["incidente"]
    }

    approved_train = sum(
        row["split"] == "train" and row["revisao"] == "human_verdict" for row in existing
    )
    ids = {row["id"] for row in existing}
    locators = set()
    incident_groups = {row["incidente"]: row["grupo"] for row in existing if row["incidente"]}
    rows = []
    for path in sources:
        batch = SourceBatch.model_validate_json(path.read_text(encoding="utf-8"))
        for row in batch.proposals:
            if (
                row.group in reserved_groups
                or row.group.split("/", 1)[0] in reserved_datasets
                or row.incident in reserved_incidents
            ):
                raise ValueError(f"{row.id}: grupo ou incidente reservado para avaliação.")
            if row.id in ids or (batch.source, row.locator) in locators:
                raise ValueError(f"{row.id}: ID ou localizador repetido.")
            if incident_groups.setdefault(row.incident, row.group) != row.group:
                raise ValueError(f"{row.id}: incidente atribuído a grupos diferentes.")
            ids.add(row.id)
            locators.add((batch.source, row.locator))
            rows.append((batch.source, row))

    context = sum(row.verdict == "precisa_contexto" for _, row in rows)
    report = {
        "meta_treino": target_train,
        "aprovados_treino": approved_train,
        "faltam_aprovados": max(0, target_train - approved_train),
        "propostas": len(rows),
        "propostas_com_rotulo": len(rows) - context,
        "precisa_contexto": context,
        "grupos": len({row.group for _, row in rows}),
        "incidentes": len({row.incident for _, row in rows}),
        "por_fonte": dict(Counter(source for source, _ in rows)),
        "por_origem": dict(Counter(row.log_source for _, row in rows)),
        "por_veredito": dict(Counter(row.verdict for _, row in rows)),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent, prefix=".revisao-") as temporary:
        staging = Path(temporary)
        with (staging / "revisao.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                (
                    "id",
                    "fonte",
                    "grupo",
                    "incidente",
                    "telemetria",
                    "ancora",
                    "evidencia",
                    "veredito_proposto",
                    "severidade_proposta",
                    "justificativa",
                    "localizador",
                    "decisao_humana",
                    "veredito_final",
                    "severidade_final",
                )
            )
            for source, row in rows:
                cells = (
                    row.id,
                    source,
                    row.group,
                    row.incident,
                    row.log_source,
                    row.anchor,
                    row.evidence,
                    row.verdict,
                    row.severity or "",
                    row.rationale,
                    row.locator,
                )
                writer.writerow([*map(spreadsheet_cell, cells), "", "", ""])
        (staging / "auditoria.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        staging.rename(output)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, action="append", required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument(
        "--reservations", type=Path, default=Path("configs/datasets/reservas-avaliacao.yaml")
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--target-train", type=int, default=500)
    args = parser.parse_args()
    try:
        report = merge(
            args.source, args.reference, args.reservations, args.output_dir, args.target_train
        )
    except (ValueError, OSError, KeyError, TypeError, csv.Error, yaml.YAMLError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
