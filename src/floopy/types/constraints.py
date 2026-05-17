from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class OrgConstraints:
    #: Hard cap (USD) on total monthly spend. ``None`` clears it.
    cost_limit_monthly_usd: float | None = None
    #: Sliding window for the token rate limit, in seconds.
    token_window_seconds: int | None = None
    #: Max tokens allowed per ``token_window_seconds``.
    max_tokens_per_window: int | None = None
    #: Max requests per minute per API key.
    max_requests_per_minute: int | None = None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> OrgConstraints:
        return cls(
            cost_limit_monthly_usd=w["cost_limit_monthly_usd"],
            token_window_seconds=w["token_window_seconds"],
            max_tokens_per_window=w["max_tokens_per_window"],
            max_requests_per_minute=w["max_requests_per_minute"],
        )

    def to_wire(self) -> dict[str, Any]:
        """Full-replace payload: every field is sent (``None`` clears it
        server-side), matching the gateway's PUT semantics."""
        return {
            "cost_limit_monthly_usd": self.cost_limit_monthly_usd,
            "token_window_seconds": self.token_window_seconds,
            "max_tokens_per_window": self.max_tokens_per_window,
            "max_requests_per_minute": self.max_requests_per_minute,
        }
