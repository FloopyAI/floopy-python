from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


@dataclass(slots=True)
class SessionTurn:
    """Provenance for one reconstructed exchange."""

    request_id: str
    #: RFC3339 timestamp of the originating request.
    created_at: str
    model: str
    provider: str

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> SessionTurn:
        return cls(
            request_id=w["request_id"],
            created_at=w["created_at"],
            model=w["model"],
            provider=w["provider"],
        )


@dataclass(slots=True)
class Session:
    """A conversation restored from Floopy's stored logs.

    ``messages`` is chronological (oldest -> newest) and is a drop-in for the
    ``messages`` argument of a follow-up ``chat.completions.create`` call.
    """

    session_id: str
    messages: list[ChatCompletionMessageParam]
    #: Stored turns that contributed to ``messages``.
    turn_count: int
    turns: list[SessionTurn]

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> Session:
        return cls(
            session_id=w["session_id"],
            messages=w["messages"],
            turn_count=w["turn_count"],
            turns=[SessionTurn.from_wire(t) for t in w["turns"]],
        )
