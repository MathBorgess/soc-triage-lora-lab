"""Priorize candidatos de triagem para revisão com base em evidência normalizada."""

import argparse
import csv
import json
from collections import Counter, defaultdict, deque
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Literal, NamedTuple, get_args

from pydantic import (
    AwareDatetime,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PositiveInt,
    ValidationError,
    model_validator,
)

from soc_triage.schema import LogSource, Severity, Verdict

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")]
EvidenceKind = Literal[
    "observed_event",
    "correlated_anomaly",
    "verified_malicious_attempt",
    "verified_unauthorized_access",
    "verified_privileged_misuse",
    "verified_routine_activity",
    "verified_authorized_change",
]


def parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("use data e hora ISO 8601 com fuso")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError("use data e hora ISO 8601 com fuso") from None


Timestamp = Annotated[AwareDatetime, BeforeValidator(parse_timestamp)]


class Evidence(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    kind: EvidenceKind
    observed_at: Timestamp
    member: Identifier
    line: PositiveInt


class Case(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    id: Identifier
    dataset: Identifier
    group: Identifier
    incident: Identifier
    log_source: LogSource
    anchor_at: Timestamp
    anchor_member: Identifier
    anchor_line: PositiveInt
    evidence: list[Evidence] = Field(min_length=1)

    @model_validator(mode="after")
    def check_cutoff(self) -> "Case":
        locators = set()
        matched_anchor = False
        for item in self.evidence:
            locator = (item.member, item.line)
            if locator in locators:
                raise ValueError("localizador de evidência repetido")
            locators.add(locator)
            if item.observed_at > self.anchor_at:
                raise ValueError("evidência após a âncora")
            if item.member == self.anchor_member and item.line > self.anchor_line:
                raise ValueError("linha de evidência após a âncora no mesmo arquivo")
            if item.observed_at == self.anchor_at and item.member != self.anchor_member:
                raise ValueError("ordem indeterminada para evidência simultânea de outro arquivo")
            if locator == (self.anchor_member, self.anchor_line):
                if item.observed_at != self.anchor_at:
                    raise ValueError("horário de evidência divergente na linha âncora")
                matched_anchor = True
        if not matched_anchor:
            raise ValueError("linha âncora ausente da evidência")
        return self


class Proposal(NamedTuple):
    verdict: Verdict | None
    severity: Severity | None
    rationale: str
    hard_negative: bool = False


def propose(case: Case) -> Proposal:
    kinds = {item.kind for item in case.evidence}
    positive = kinds & {
        "verified_malicious_attempt",
        "verified_unauthorized_access",
        "verified_privileged_misuse",
    }
    negative = kinds & {"verified_routine_activity", "verified_authorized_change"}
    anomalous = "correlated_anomaly" in kinds
    if positive and negative:
        return Proposal(None, None, "As evidências verificadas sobre a atividade divergem.")
    if "verified_privileged_misuse" in kinds:
        return Proposal("malicious", "high", "A evidência confirma abuso de acesso privilegiado.")
    if "verified_unauthorized_access" in kinds:
        return Proposal("malicious", "high", "A evidência confirma acesso não autorizado.")
    if "verified_malicious_attempt" in kinds:
        return Proposal("malicious", "medium", "A evidência confirma uma tentativa maliciosa.")
    if "verified_authorized_change" in kinds:
        return Proposal(
            "expected_admin",
            "info",
            "A mudança observada corresponde a uma autorização.",
            anomalous,
        )
    if "verified_routine_activity" in kinds:
        return Proposal(
            "benign", "info", "A evidência contextual confirma a atividade rotineira.", anomalous
        )
    if anomalous:
        return Proposal("suspicious", "medium", "A correlação exige investigação adicional.")
    return Proposal(None, None, "A observação isolada é insuficiente para propor um veredito.")


def read_cases(path: Path) -> list[Case]:
    cases = []
    ids = set()
    anchors = set()
    incident_groups = {}
    with path.open(encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            try:
                case = Case.model_validate_json(line)
            except ValidationError as error:
                messages = " / ".join(item["msg"] for item in error.errors(include_input=False))
                raise ValueError(f"Linha {index} — {messages}") from None
            anchor = (case.dataset, case.group, case.anchor_member, case.anchor_line)
            if case.id in ids or anchor in anchors:
                raise ValueError(f"Linha {index}: ID ou âncora repetidos")
            if incident_groups.setdefault(case.incident, case.group) != case.group:
                raise ValueError(f"Linha {index}: incidente atribuído a grupos diferentes")
            ids.add(case.id)
            anchors.add(anchor)
            cases.append(case)
    if not cases:
        raise ValueError("Nenhum candidato no arquivo de entrada")
    return cases


def priority(case: Case, proposal: Proposal) -> int:
    if case.log_source == "linux_auth" and proposal.verdict == "malicious":
        return 0
    if proposal.hard_negative:
        return 1
    if proposal.verdict is not None:
        return 2
    return 3


def order_queue(cases: list[Case]) -> list[tuple[Case, Proposal]]:
    entries = [(case, propose(case)) for case in cases]
    buckets = defaultdict(lambda: defaultdict(deque))
    for case, proposal in sorted(
        entries, key=lambda item: (priority(*item), item[0].group, item[0].anchor_at, item[0].id)
    ):
        buckets[case.group][case.incident].append((case, proposal))

    queue = []
    groups = deque(deque(incidents.values()) for incidents in buckets.values())
    while groups:
        incidents = groups.popleft()
        cases_for_incident = incidents.popleft()
        queue.append(cases_for_incident.popleft())
        if cases_for_incident:
            incidents.append(cases_for_incident)
        if incidents:
            groups.append(incidents)
    return queue


def write_queue(path: Path, entries: list[tuple[Case, Proposal]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            (
                "id",
                "dataset",
                "grupo",
                "incidente",
                "origem",
                "horario_ancora",
                "arquivo_ancora",
                "linha_ancora",
                "status",
                "veredito_proposto",
                "severidade_proposta",
                "negativo_dificil",
                "justificativa",
                "evidencia",
                "decisao_humana",
            )
        )
        for case, proposal in entries:
            evidence = json.dumps(
                [
                    item.model_dump(mode="json")
                    for item in sorted(
                        case.evidence, key=lambda item: (item.observed_at, item.member, item.line)
                    )
                ]
            )
            writer.writerow(
                (
                    case.id,
                    case.dataset,
                    case.group,
                    case.incident,
                    case.log_source,
                    case.anchor_at.isoformat(),
                    case.anchor_member,
                    case.anchor_line,
                    "proposta" if proposal.verdict else "precisa_contexto",
                    proposal.verdict,
                    proposal.severity,
                    "sim" if proposal.hard_negative else "nao",
                    proposal.rationale,
                    evidence,
                    "",
                )
            )


def build_queue(input_path: Path, output: Path, limit: int | None = None) -> dict:
    if limit is not None and limit < 1:
        raise ValueError("O limite precisa ser positivo")
    if output.exists() or output.is_symlink():
        raise FileExistsError(f"Use um novo diretório de revisão: {output}")
    cases = read_cases(input_path)
    entries = order_queue(cases)[:limit]
    stats = {
        "rubrica": "propostas-v1",
        "candidatos": len(cases),
        "selecionados": len(entries),
        "grupos_disponiveis": len({case.group for case in cases}),
        "grupos_selecionados": len({case.group for case, _ in entries}),
        "incidentes_selecionados": len({case.incident for case, _ in entries}),
        "por_dataset": dict(Counter(case.dataset for case, _ in entries)),
        "por_origem": dict(Counter(case.log_source for case, _ in entries)),
        "por_veredito": dict(
            Counter(proposal.verdict or "precisa_contexto" for _, proposal in entries)
        ),
        "negativos_dificeis": sum(proposal.hard_negative for _, proposal in entries),
        "linux_auth_malicioso": sum(
            case.log_source == "linux_auth" and proposal.verdict == "malicious"
            for case, proposal in entries
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent, prefix=".propostas-") as temporary:
        staging = Path(temporary)
        write_queue(staging / "propostas.csv", entries)
        (staging / "auditoria.json").write_text(
            json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        staging.rename(output)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Cada linha JSONL contém id, dataset, group, incident, log_source, anchor_at, "
            "anchor_member, anchor_line e evidence. Cada item de evidence tem kind, "
            "observed_at, member e line. Use data e hora ISO 8601 com fuso e IDs rastreáveis. "
            "Os sinais verificados devem se aplicar ao evento âncora e ser sustentados pelas "
            "referências do incidente. Use observed_event quando a evidência for insuficiente. "
            f"Sinais aceitos em kind: {', '.join(get_args(EvidenceKind))}."
        ),
    )
    parser.add_argument("--input", required=True, type=Path, help="Metadados locais em JSONL.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Pasta nova para a fila.")
    parser.add_argument("--limit", type=int, help="Número máximo de candidatos na fila.")
    args = parser.parse_args()
    try:
        stats = build_queue(args.input, args.output_dir, args.limit)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
