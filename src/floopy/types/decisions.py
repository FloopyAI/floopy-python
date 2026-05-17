from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Decision:
    request_id: str
    session_id: str | None
    request_created_at: str
    provider: str | None
    model: str | None
    status: str
    latency_ms: int | None
    cost_micro_usd: int | None
    cache_enabled: bool | None
    threat: str | None
    decision_trace: Any
    confidence: float | None
    confidence_reason: str | None
    explanation: str | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> Decision:
        return cls(
            request_id=w["request_id"],
            session_id=w["session_id"],
            request_created_at=w["request_created_at"],
            provider=w["provider"],
            model=w["model"],
            status=w["status"],
            latency_ms=w["latency_ms"],
            cost_micro_usd=w["cost_micro_usd"],
            cache_enabled=w["cache_enabled"],
            threat=w["threat"],
            decision_trace=w["decision_trace"],
            confidence=w["confidence"],
            confidence_reason=w["confidence_reason"],
            explanation=w["explanation"],
        )


@dataclass(slots=True)
class DecisionListPage:
    items: list[Decision]
    next_cursor: str | None
    has_more: bool

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> DecisionListPage:
        return cls(
            items=[Decision.from_wire(i) for i in w["items"]],
            next_cursor=w["next_cursor"],
            has_more=w["has_more"],
        )
