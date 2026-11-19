"""Contrato canônico da saída de triagem."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

LogSource = Literal["sysmon", "linux_auth", "apache", "suricata", "waf"]
Verdict = Literal["malicious", "suspicious", "benign", "expected_admin"]
Severity = Literal["critical", "high", "medium", "low", "info"]
MitreTechnique = Annotated[str, Field(pattern=r"^T\d{4}(\.\d{3})?$")]


class NormalizedEvent(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    timestamp: str | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    user: str | None = None
    process_or_action: str | None = None
    iocs: list[str]


class Triage(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    verdict: Verdict
    severity: Severity
    mitre_technique: MitreTechnique | None = None
    rationale: str


class SocTriageEvent(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    log_source: LogSource
    normalized_event: NormalizedEvent
    triage: Triage
