"""Batches API — create/list/retrieve/cancel asynchronous batch jobs.

Traffic is forwarded verbatim to the provider chosen via ``provider``
(the ``floopy-provider`` header); a batch carries no model up front so
the upstream cannot be inferred."""

from __future__ import annotations

from typing import Any

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, SyncHTTP
from ..types.batches import Batch, BatchList
from ..types.shared import RequestOptions
from ._batch_options import with_provider


def _create_body(
    input_file_id: str,
    endpoint: str,
    completion_window: str,
    metadata: dict[str, str] | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "input_file_id": input_file_id,
        "endpoint": endpoint,
        "completion_window": completion_window,
    }
    if metadata is not None:
        body["metadata"] = metadata
    return body


def _list_query(limit: int | None, after: str | None) -> dict[str, Any]:
    q: dict[str, Any] = {}
    if limit is not None:
        q["limit"] = limit
    if after is not None:
        q["after"] = after
    return q


class BatchesResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def create(
        self,
        *,
        input_file_id: str,
        endpoint: str,
        completion_window: str,
        metadata: dict[str, str] | None = None,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Batch:
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.BATCHES,
            body=_create_body(input_file_id, endpoint, completion_window, metadata),
            request_options=with_provider(provider, request_options),
        )
        return Batch.from_wire(data)

    def list(
        self,
        *,
        limit: int | None = None,
        after: str | None = None,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> BatchList:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.BATCHES,
            query=_list_query(limit, after),
            request_options=with_provider(provider, request_options),
        )
        return BatchList.from_wire(data)

    def retrieve(
        self,
        batch_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Batch:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.batch_by_id(batch_id),
            request_options=with_provider(provider, request_options),
        )
        return Batch.from_wire(data)

    def cancel(
        self,
        batch_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Batch:
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.batch_cancel(batch_id),
            request_options=with_provider(provider, request_options),
        )
        return Batch.from_wire(data)


class AsyncBatchesResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def create(
        self,
        *,
        input_file_id: str,
        endpoint: str,
        completion_window: str,
        metadata: dict[str, str] | None = None,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Batch:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.BATCHES,
            body=_create_body(input_file_id, endpoint, completion_window, metadata),
            request_options=with_provider(provider, request_options),
        )
        return Batch.from_wire(data)

    async def list(
        self,
        *,
        limit: int | None = None,
        after: str | None = None,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> BatchList:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.BATCHES,
            query=_list_query(limit, after),
            request_options=with_provider(provider, request_options),
        )
        return BatchList.from_wire(data)

    async def retrieve(
        self,
        batch_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Batch:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.batch_by_id(batch_id),
            request_options=with_provider(provider, request_options),
        )
        return Batch.from_wire(data)

    async def cancel(
        self,
        batch_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Batch:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.batch_cancel(batch_id),
            request_options=with_provider(provider, request_options),
        )
        return Batch.from_wire(data)
