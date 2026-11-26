"""Valide fontes curadas e exporte splits MLX com uma trilha de revisão separada."""

import argparse
import csv
import hashlib
import json
import sqlite3
import tarfile
from collections import Counter, defaultdict
from contextlib import closing, nullcontext
from gzip import GzipFile
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Annotated, BinaryIO, Literal
from zipfile import BadZipFile, ZipFile

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from soc_triage.metrics import check_ioc_hallucinations
from soc_triage.prompts import PROMPT_VERSION, build_chat_record
from soc_triage.schema import SocTriageEvent

SPLITS = ("train", "valid", "test")
EvidenceFormat = Literal["zip", "tar", "sqlite_events", "text", "csv_records"]


class SplitSource(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    group: str = Field(min_length=1)
    records: str = Field(min_length=1)
    archive: str = Field(min_length=1)
    evidence_format: EvidenceFormat = "zip"
    reverse_lines: bool = False


SplitEntries = SplitSource | Annotated[list[SplitSource], Field(min_length=1)]


class Manifest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    train: SplitEntries
    valid: SplitEntries
    test: SplitEntries


class Candidate(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: str = Field(min_length=1)
    group: str
    archive: str
    member: str
    lines: list[PositiveInt] = Field(min_length=1)
    approval: Literal["human_verdict", "proposed"]
    input: str = Field(min_length=1)
    target: SocTriageEvent
    review_notes: str = ""
    source_labels: list[str] = Field(default_factory=list)
    dataset: str | None = Field(default=None, min_length=1)
    incident: str | None = Field(default=None, min_length=1)
    anchor_line: PositiveInt | None = None


def load_candidates(
    path: Path, source: SplitSource, split: str, *, require_approved: bool
) -> list[Candidate]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = Candidate.model_validate_json(line)
            except ValueError as error:
                raise ValueError(f"{path.name}, linha {line_number}: envelope inválido") from error
            if row.group != source.group or row.archive != Path(source.archive).name:
                raise ValueError(f"{row.id}: grupo ou arquivo de origem divergente do manifesto")
            if (split == "train" or require_approved) and row.approval != "human_verdict":
                raise ValueError(f"{row.id}: {split} exige veredito humano aprovado")
            if not row.input.strip() or not row.target.triage.rationale.strip():
                raise ValueError(f"{row.id}: entrada e justificativa devem conter texto")
            if len(set(row.lines)) != len(row.lines):
                raise ValueError(f"{row.id}: localizadores de origem repetidos")
            if row.anchor_line is not None:
                latest = min(row.lines) if source.reverse_lines else max(row.lines)
                if row.anchor_line != latest:
                    raise ValueError(f"{row.id}: âncora deve ser o último registro usado")
            if check_ioc_hallucinations(row.target, row.input)["hallucinated"]:
                raise ValueError(f"{row.id}: IP ou IoC do alvo ausente na entrada")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path.name}: split sem exemplos")
    return rows


def literal_values(row: Candidate) -> set[str]:
    event = row.target.normalized_event
    return {
        value.casefold() for value in (event.src_ip, event.dst_ip, *event.iocs) if value is not None
    }


def read_lines(stream: BinaryIO, positions: set[int]) -> dict[int, bytes]:
    found = {}
    for index, line in enumerate(stream, 1):
        if index in positions:
            found[index] = line
            if len(found) == len(positions):
                break
    return found


def read_csv_records(stream: BinaryIO, positions: set[int]) -> dict[int, bytes]:
    """Locate logical data records, preserving the raw bytes of multiline fields."""
    physical_lines = []

    def decode_lines():
        for line in stream:
            physical_lines.append(line)
            yield line.decode("utf-8-sig")

    reader = csv.reader(decode_lines(), strict=True)
    next(reader, None)
    physical_lines.clear()
    found = {}
    for index, _ in enumerate(reader, 1):
        if index in positions:
            found[index] = b"".join(physical_lines)
        physical_lines.clear()
        if len(found) == len(positions):
            break
    return found


def read_evidence(
    path: Path, evidence_format: EvidenceFormat, requested: dict[str, set[int]]
) -> dict[str, dict[int, bytes]]:
    evidence = {}
    if evidence_format == "sqlite_events":
        if requested.keys() != {"events"}:
            raise ValueError(f"{path.name}: a origem SQLite exige localizadores de events.id")
        positions = requested["events"]
        uri = f"{path.resolve().as_uri()}?mode=ro&immutable=1"
        with closing(sqlite3.connect(uri, uri=True)) as db:
            rows = db.execute(
                "SELECT id, raw_line FROM events WHERE id BETWEEN ? AND ? ORDER BY id",
                (min(positions), max(positions)),
            )
            evidence["events"] = {
                index: line.encode("utf-8") for index, line in rows if index in positions
            }
    elif evidence_format in ("text", "csv_records"):
        if requested.keys() != {path.name}:
            raise ValueError(f"{path.name}: localizador deve identificar o arquivo de texto")
        with path.open("rb") as stream:
            read_positions = read_csv_records if evidence_format == "csv_records" else read_lines
            evidence[path.name] = read_positions(stream, requested[path.name])
    elif evidence_format == "tar":
        with tarfile.open(path, "r:*") as archive:
            for member, positions in requested.items():
                entry = archive.getmember(member)
                if not entry.isfile():
                    raise ValueError(f"{path.name}: membro de origem não é um arquivo regular")
                with archive.extractfile(entry) as stream:
                    evidence[member] = read_lines(stream, positions)
    else:
        with ZipFile(path) as archive:
            for member, positions in requested.items():
                with (
                    archive.open(member) as raw,
                    GzipFile(fileobj=raw) if member.endswith(".gz") else nullcontext(raw) as stream,
                ):
                    evidence[member] = read_lines(stream, positions)
    return evidence


def source_hashes(path: Path, rows: list[Candidate], evidence_format: EvidenceFormat) -> set[str]:
    """Confira localizadores e calcule hashes das linhas citadas sem publicar o bruto."""
    requested: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        member_path = PurePosixPath(row.member)
        if (
            member_path.is_absolute()
            or ".." in member_path.parts
            or "\\" in row.member
            or row.member != member_path.as_posix()
        ):
            raise ValueError(f"{row.id}: membro de origem inválido")
        if row.group.startswith("ait-lds") and (
            not row.member.startswith("gather/") or "/logs/" not in row.member
        ):
            raise ValueError(f"{row.id}: membro AIT fora da árvore de logs")
        requested[row.member].update(row.lines)

    raw_evidence = read_evidence(path, evidence_format, requested)
    fingerprints = set()
    evidence = {}
    for member, positions in requested.items():
        found = raw_evidence[member]
        if found.keys() != positions:
            raise ValueError(f"{path.name}: localizadores ausentes em {member}")
        evidence[member] = {
            index: line.decode("utf-8", errors="replace").casefold()
            for index, line in found.items()
        }
        fingerprints.update(
            hashlib.sha256(line.strip()).hexdigest() for line in found.values() if line.strip()
        )
    for row in rows:
        lines = [evidence[row.member][index] for index in row.lines]
        if any(not any(value in line for line in lines) for value in literal_values(row)):
            raise ValueError(f"{row.id}: IP ou IoC do alvo ausente nas linhas de origem")
    return fingerprints


def save_jsonl(path: Path, rows) -> None:
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def csv_cell(value: str) -> str:
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value


def export(manifest_path: Path, output: Path, *, require_approved: bool = False) -> dict:
    manifest = Manifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    sources = {}
    for split in SPLITS:
        entries = getattr(manifest, split)
        sources[split] = entries if isinstance(entries, list) else [entries]
    base = manifest_path.parent
    if output.exists():
        raise FileExistsError(f"Use um diretório novo para preservar a revisão anterior: {output}")

    group_splits: dict[str, str] = {}
    archive_usage: dict[Path, tuple[str, EvidenceFormat, bool]] = {}
    for split, entries in sources.items():
        for entry in entries:
            if group_splits.setdefault(entry.group, split) != split:
                raise ValueError("Um grupo foi atribuído a mais de um split")
            archive = (base / entry.archive).resolve()
            usage = (split, entry.evidence_format, entry.reverse_lines)
            existing = archive_usage.setdefault(archive, usage)
            if existing[0] != split:
                raise ValueError("Um arquivo de origem foi atribuído a mais de um split")
            if existing != usage:
                raise ValueError("Um arquivo de origem recebeu interpretações diferentes")

    dataset = {}
    seen_ids: set[str] = set()
    seen_inputs: set[str] = set()
    seen_source_hashes: set[str] = set()
    incident_splits: dict[str, str] = {}
    stats = {"prompt_version": PROMPT_VERSION, "splits": {}}
    for split, entries in sources.items():
        rows = []
        by_archive: dict[Path, list[Candidate]] = defaultdict(list)
        for entry in entries:
            candidates = load_candidates(
                base / entry.records, entry, split, require_approved=require_approved
            )
            rows.extend(candidates)
            by_archive[(base / entry.archive).resolve()].extend(candidates)
        ids = {row.id for row in rows}
        inputs = {" ".join(row.input.casefold().split()) for row in rows}
        raw_hashes: set[str] = set()
        for archive, candidates in by_archive.items():
            raw_hashes.update(source_hashes(archive, candidates, archive_usage[archive][1]))
        if len(ids) != len(rows) or seen_ids & ids:
            raise ValueError(f"{split}: ID duplicado")
        if len(inputs) != len(rows) or seen_inputs & inputs:
            raise ValueError(f"{split}: entrada duplicada após normalizar caixa e espaços")
        if seen_source_hashes & raw_hashes:
            raise ValueError(f"{split}: linha de origem idêntica em outro split")
        seen_ids.update(ids)
        seen_inputs.update(inputs)
        seen_source_hashes.update(raw_hashes)
        dataset[split] = rows
        source_verdicts: dict[str, Counter[str]] = defaultdict(Counter)
        for row in rows:
            if row.incident and incident_splits.setdefault(row.incident, split) != split:
                raise ValueError(f"{row.id}: incidente atribuído a mais de um split")
            source_verdicts[row.target.log_source][row.target.triage.verdict] += 1
        groups = sorted({entry.group for entry in entries})
        stats["splits"][split] = {
            "group": groups[0] if len(groups) == 1 else None,
            "groups": groups,
            "count": len(rows),
            "source_counts": dict(Counter(row.target.log_source for row in rows)),
            "verdict_counts": dict(Counter(row.target.triage.verdict for row in rows)),
            "source_verdict_counts": dict(source_verdicts),
            "approval_counts": dict(Counter(row.approval for row in rows)),
            "literal_values_checked": sum(len(literal_values(row)) for row in rows),
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent, prefix=".curadoria-") as temporary:
        staging = Path(temporary)
        for split, rows in dataset.items():
            save_jsonl(
                staging / f"{split}.jsonl",
                (build_chat_record(row.input, row.target.model_dump_json()) for row in rows),
            )
        with (staging / "revisao.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(
                (
                    "split",
                    "id",
                    "grupo",
                    "origem",
                    "revisao",
                    "veredito",
                    "severidade",
                    "entrada",
                    "justificativa",
                    "alvo_json",
                    "localizador",
                    "notas",
                    "dataset",
                    "incidente",
                    "linha_ancora",
                )
            )
            for split, rows in dataset.items():
                for row in rows:
                    writer.writerow(
                        map(
                            csv_cell,
                            (
                                split,
                                row.id,
                                row.group,
                                row.target.log_source,
                                row.approval,
                                row.target.triage.verdict,
                                row.target.triage.severity,
                                row.input,
                                row.target.triage.rationale,
                                row.target.model_dump_json(),
                                f"{row.member} ({', '.join(map(str, row.lines))})",
                                row.review_notes,
                                row.dataset or "",
                                row.incident or "",
                                str(row.anchor_line or ""),
                            ),
                        )
                    )
        (staging / "validacao.json").write_text(
            json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(output)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", required=True, type=Path, help="Manifesto local dos três splits."
    )
    parser.add_argument("--output-dir", required=True, type=Path, help="Novo diretório de saída.")
    parser.add_argument(
        "--require-approved", action="store_true", help="Exigir decisão humana em todos os splits."
    )
    args = parser.parse_args()
    try:
        stats = export(args.manifest, args.output_dir, require_approved=args.require_approved)
    except (
        ValueError,
        OSError,
        KeyError,
        BadZipFile,
        tarfile.TarError,
        sqlite3.Error,
        csv.Error,
    ) as error:
        parser.error(str(error))
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
