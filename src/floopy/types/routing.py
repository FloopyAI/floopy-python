from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

FirewallDecision = Literal["allow", "block_input"]


@dataclass(slots=True)
class RoutingExplainResult:
    #: ``None`` when the firewall blocks the request.
    would_select: dict[str, str] | None
    firewall_decision: FirewallDecision
    reasoning: str | None
    routing_rule_id: str | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> RoutingExplainResult:
        return cls(
            would_select=w["would_select"],
            firewall_decision=w["firewall_decision"],
            reasoning=w["reasoning"],
            routing_rule_id=w["routing_rule_id"],
        )
