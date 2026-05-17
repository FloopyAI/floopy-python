from __future__ import annotations

from typing import Any

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, Query, SyncHTTP
from ..types.evaluations import EvaluationResultsPage, EvaluationRun
from ..types.shared import RequestOptions


def _create_body(
    *,
    dataset_id: str,
    model: str,
    prompt_id: str | None,
    config: dict[str, Any] | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"dataset_id": dataset_id, "model": model}
    if prompt_id is not None:
        body["prompt_id"] = prompt_id
    if config is not None:
        body["config"] = config
    return body


def _results_query(limit: int | None, cursor: str | None) -> Query:
    query: Query = {}
    if limit is not None:
        query["limit"] = limit
    if cursor is not None:
        query["cursor"] = cursor
    return query


class EvaluationsResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def create(
        self,
        *,
        dataset_id: str,
        model: str,
        prompt_id: str | None = None,
        config: dict[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> EvaluationRun:
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.EVALUATIONS,
            body=_create_body(
                dataset_id=dataset_id, model=model, prompt_id=prompt_id, config=config
            ),
            request_options=request_options,
        )
        return EvaluationRun.from_wire(data)

    def get(
        self, evaluation_id: str, *, request_options: RequestOptions | None = None
    ) -> EvaluationRun:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.evaluation_by_id(evaluation_id),
            request_options=request_options,
        )
        return EvaluationRun.from_wire(data)

    def cancel(
        self, evaluation_id: str, *, request_options: RequestOptions | None = None
    ) -> EvaluationRun:
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.evaluation_cancel(evaluation_id),
            request_options=request_options,
        )
        return EvaluationRun.from_wire(data)

    def results(
        self,
        evaluation_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> EvaluationResultsPage:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.evaluation_results(evaluation_id),
            query=_results_query(limit, cursor),
            request_options=request_options,
        )
        return EvaluationResultsPage.from_wire(data)


class AsyncEvaluationsResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def create(
        self,
        *,
        dataset_id: str,
        model: str,
        prompt_id: str | None = None,
        config: dict[str, Any] | None = None,
        request_options: RequestOptions | None = None,
    ) -> EvaluationRun:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.EVALUATIONS,
            body=_create_body(
                dataset_id=dataset_id, model=model, prompt_id=prompt_id, config=config
            ),
            request_options=request_options,
        )
        return EvaluationRun.from_wire(data)

    async def get(
        self, evaluation_id: str, *, request_options: RequestOptions | None = None
    ) -> EvaluationRun:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.evaluation_by_id(evaluation_id),
            request_options=request_options,
        )
        return EvaluationRun.from_wire(data)

    async def cancel(
        self, evaluation_id: str, *, request_options: RequestOptions | None = None
    ) -> EvaluationRun:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.evaluation_cancel(evaluation_id),
            request_options=request_options,
        )
        return EvaluationRun.from_wire(data)

    async def results(
        self,
        evaluation_id: str,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> EvaluationResultsPage:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.evaluation_results(evaluation_id),
            query=_results_query(limit, cursor),
            request_options=request_options,
        )
        return EvaluationResultsPage.from_wire(data)
