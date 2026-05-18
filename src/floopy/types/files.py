"""Files API models. The gateway forwards file traffic verbatim to the
resolved provider; these mirror the OpenAI file shapes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FileObject:
    id: str
    object: str | None
    bytes: int | None
    created_at: int | None
    filename: str | None
    purpose: str | None
    status: str | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> FileObject:
        return cls(
            id=w["id"],
            object=w.get("object"),
            bytes=w.get("bytes"),
            created_at=w.get("created_at"),
            filename=w.get("filename"),
            purpose=w.get("purpose"),
            status=w.get("status"),
        )


@dataclass(slots=True)
class FileList:
    object: str | None
    data: list[FileObject]

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> FileList:
        return cls(
            object=w.get("object"),
            data=[FileObject.from_wire(item) for item in w.get("data", [])],
        )
