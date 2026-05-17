from __future__ import annotations

from dataclasses import replace
from typing import Any

from .._constants import ENDPOINTS, FLOOPY_CONFIRM_VALUES, FLOOPY_HEADERS
from .._http import AsyncHTTP, Query, SyncHTTP
from ..types.experiments import (
    Experiment,
    ExperimentListPage,
    ExperimentResults,
    ExperimentStatus,
)
from ..types.shared import RequestOptions


def _list_query(
    status: ExperimentStatus | None,
    from_: str | None,
    to: str | None,
    limit: int | None,
    cursor: str | None,
) -> Query:
    query: Query = {}
    if status is not None:
        query["status"] = status
    if from_ is not None:
        query["from"] = from_
    if to is not None:
        query["to"] = to
    if limit is not None:
        query["limit"] = limit
    if cursor is not None:
        query["cursor"] = cursor
    return query


def _create_body(
    *,
    name: str,
    variant_a_routing_rule_id: str,
    variant_b_routing_rule_id: str,
    description: str | None,
    split_percentage: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "name": name,
        "variant_a_routing_rule_id": variant_a_routing_rule_id,
        "variant_b_routing_rule_id": variant_b_routing_rule_id,
    }
    if description is not None:
        body["description"] = description
    if split_percentage is not None:
        body["split_percentage"] = split_percentage
    return body


def _with_confirm(request_options: RequestOptions | None) -> RequestOptions:
    """Inject ``X-Floopy-Confirm: experiments`` (gateway SEC-009 requires it
    on create/rollback) without mutating the caller's options."""
    base = request_options or RequestOptions()
    headers = {**base.headers, FLOOPY_HEADERS.CONFIRM: FLOOPY_CONFIRM_VALUES.EXPERIMENTS}
    return replace(base, headers=headers)


class ExperimentsResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def list(
        self,
        *,
        status: ExperimentStatus | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> ExperimentListPage:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.EXPERIMENTS,
            query=_list_query(status, from_, to, limit, cursor),
            request_options=request_options,
        )
        return ExperimentListPage.from_wire(data)

    def create(
        self,
        *,
        name: str,
        variant_a_routing_rule_id: str,
        variant_b_routing_rule_id: str,
        description: str | None = None,
        split_percentage: int | None = None,
        request_options: RequestOptions | None = None,
    ) -> Experiment:
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.EXPERIMENTS,
            body=_create_body(
                name=name,
                variant_a_routing_rule_id=variant_a_routing_rule_id,
                variant_b_routing_rule_id=variant_b_routing_rule_id,
                description=description,
                split_percentage=split_percentage,
            ),
            request_options=_with_confirm(request_options),
        )
        return Experiment.from_wire(data)

    def rollback(
        self, experiment_id: str, *, request_options: RequestOptions | None = None
    ) -> Experiment:
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.experiment_rollback(experiment_id),
            request_options=_with_confirm(request_options),
        )
        return Experiment.from_wire(data)

    def results(
        self, experiment_id: str, *, request_options: RequestOptions | None = None
    ) -> ExperimentResults:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.experiment_results(experiment_id),
            request_options=request_options,
        )
        return ExperimentResults.from_wire(data)


class AsyncExperimentsResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        status: ExperimentStatus | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> ExperimentListPage:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.EXPERIMENTS,
            query=_list_query(status, from_, to, limit, cursor),
            request_options=request_options,
        )
        return ExperimentListPage.from_wire(data)

    async def create(
        self,
        *,
        name: str,
        variant_a_routing_rule_id: str,
        variant_b_routing_rule_id: str,
        description: str | None = None,
        split_percentage: int | None = None,
        request_options: RequestOptions | None = None,
    ) -> Experiment:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.EXPERIMENTS,
            body=_create_body(
                name=name,
                variant_a_routing_rule_id=variant_a_routing_rule_id,
                variant_b_routing_rule_id=variant_b_routing_rule_id,
                description=description,
                split_percentage=split_percentage,
            ),
            request_options=_with_confirm(request_options),
        )
        return Experiment.from_wire(data)

    async def rollback(
        self, experiment_id: str, *, request_options: RequestOptions | None = None
    ) -> Experiment:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.experiment_rollback(experiment_id),
            request_options=_with_confirm(request_options),
        )
        return Experiment.from_wire(data)

    async def results(
        self, experiment_id: str, *, request_options: RequestOptions | None = None
    ) -> ExperimentResults:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.experiment_results(experiment_id),
            request_options=request_options,
        )
        return ExperimentResults.from_wire(data)
