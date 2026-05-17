from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ExportFormat = Literal["jsonl", "csv"]


@dataclass(slots=True)
class ExportedDecisionRow:
    request_id: str
    session_id: str | None
    organization_id: str
    provider: str | None
    model: str | None
    status: str
    latency_ms: int | None
    cost_micro_usd: int | None
    cache_enabled: bool | None
    threat: str | None
    created_at: str

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> ExportedDecisionRow:
        return cls(
            request_id=w["request_id"],
            session_id=w["session_id"],
            organization_id=w["organization_id"],
            provider=w["provider"],
            model=w["model"],
            status=w["status"],
            latency_ms=w["latency_ms"],
            cost_micro_usd=w["cost_micro_usd"],
            cache_enabled=w["cache_enabled"],
            threat=w["threat"],
            created_at=w["created_at"],
        )


@dataclass(slots=True)
class ExportTrailer:
    rows_emitted: int
    truncated: bool
    reason: str | None
    trailer: Literal[True] = True

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> ExportTrailer:
        return cls(
            rows_emitted=w["rows_emitted"],
            truncated=w["truncated"],
            reason=w["reason"],
        )
