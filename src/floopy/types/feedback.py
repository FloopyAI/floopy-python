from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class FeedbackSubmitResponse:
    duplicate: bool
    session_id: str | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> FeedbackSubmitResponse:
        return cls(duplicate=w["duplicate"], session_id=w.get("session_id") or None)
