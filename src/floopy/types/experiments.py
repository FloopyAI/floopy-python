from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ExperimentStatus = Literal["active", "rolled_back", "completed"]


@dataclass(slots=True)
class Experiment:
    id: str
    name: str
    description: str | None
    status: ExperimentStatus
    variant_a_routing_rule_id: str
    variant_b_routing_rule_id: str
    split_percentage: int
    created_at: str
    rolled_back_at: str | None

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> Experiment:
        return cls(
            id=w["id"],
            name=w["name"],
            description=w["description"],
            status=w["status"],
            variant_a_routing_rule_id=w["variant_a_routing_rule_id"],
            variant_b_routing_rule_id=w["variant_b_routing_rule_id"],
            split_percentage=w["split_percentage"],
            created_at=w["created_at"],
            rolled_back_at=w["rolled_back_at"],
        )


@dataclass(slots=True)
class ExperimentListPage:
    items: list[Experiment]
    next_cursor: str | None
    has_more: bool

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> ExperimentListPage:
        return cls(
            items=[Experiment.from_wire(i) for i in w["items"]],
            next_cursor=w["next_cursor"],
            has_more=w["has_more"],
        )


@dataclass(slots=True)
class VariantResults:
    routing_rule_id: str
    sample_size: int
    success_rate: float
    average_latency_ms: float
    average_cost_micro_usd: float

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> VariantResults:
        return cls(
            routing_rule_id=w["routing_rule_id"],
            sample_size=w["sample_size"],
            success_rate=w["success_rate"],
            average_latency_ms=w["average_latency_ms"],
            average_cost_micro_usd=w["average_cost_micro_usd"],
        )


@dataclass(slots=True)
class ExperimentResults:
    experiment_id: str
    variant_a: VariantResults
    variant_b: VariantResults
    winner: Literal["A", "B", "tie"] | None
    computed_at: str

    @classmethod
    def from_wire(cls, w: dict[str, Any]) -> ExperimentResults:
        return cls(
            experiment_id=w["experiment_id"],
            variant_a=VariantResults.from_wire(w["variant_a"]),
            variant_b=VariantResults.from_wire(w["variant_b"]),
            winner=w["winner"],
            computed_at=w["computed_at"],
        )
