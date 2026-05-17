from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

EvaluationStatus = Literal["pending", "running", "completed", "failed", "cancelled"]


@dataclass(slots=True)
class EvaluationRun:
    id: str
    dataset_id: str
    model: str
    prompt_id: str | None
    status: EvaluationStatus
    config: dict[str, Any] | None
    created_at: str
    started_at: str | None
    finished_at: str | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> EvaluationRun:
        return cls(
            id=w["id"],
            dataset_id=w["dataset_id"],
            model=w["model"],
            prompt_id=w["prompt_id"],
            status=w["status"],
            config=w["config"],
            created_at=w["created_at"],
            started_at=w["started_at"],
            finished_at=w["finished_at"],
        )


@dataclass(slots=True)
class EvaluationResultRow:
    id: str
    run_id: str
    input_id: str
    output: str
    score: float | None
    metadata: dict[str, Any] | None
    created_at: str

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> EvaluationResultRow:
        return cls(
            id=w["id"],
            run_id=w["run_id"],
            input_id=w["input_id"],
            output=w["output"],
            score=w["score"],
            metadata=w["metadata"],
            created_at=w["created_at"],
        )


@dataclass(slots=True)
class EvaluationResultsPage:
    items: list[EvaluationResultRow]
    next_cursor: str | None
    has_more: bool

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> EvaluationResultsPage:
        return cls(
            items=[EvaluationResultRow.from_wire(i) for i in w["items"]],
            next_cursor=w["next_cursor"],
            has_more=w["has_more"],
        )
