"""Batches API models. The gateway forwards batch traffic verbatim to the
resolved provider; these mirror the OpenAI batch shapes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class BatchRequestCounts:
    total: int | None
    completed: int | None
    failed: int | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> BatchRequestCounts:
        return cls(
            total=w.get("total"),
            completed=w.get("completed"),
            failed=w.get("failed"),
        )


@dataclass(slots=True)
class Batch:
    id: str
    object: str | None
    endpoint: str | None
    status: str | None
    input_file_id: str | None
    output_file_id: str | None
    error_file_id: str | None
    created_at: int | None
    completed_at: int | None
    request_counts: BatchRequestCounts | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> Batch:
        rc = w.get("request_counts")
        return cls(
            id=w["id"],
            object=w.get("object"),
            endpoint=w.get("endpoint"),
            status=w.get("status"),
            input_file_id=w.get("input_file_id"),
            output_file_id=w.get("output_file_id"),
            error_file_id=w.get("error_file_id"),
            created_at=w.get("created_at"),
            completed_at=w.get("completed_at"),
            request_counts=BatchRequestCounts.from_wire(rc) if rc is not None else None,
        )


@dataclass(slots=True)
class BatchList:
    object: str | None
    data: list[Batch]
    has_more: bool | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> BatchList:
        return cls(
            object=w.get("object"),
            data=[Batch.from_wire(item) for item in w.get("data", [])],
            has_more=w.get("has_more"),
        )
