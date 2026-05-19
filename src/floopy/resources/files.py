"""Files API — upload/list/retrieve/delete files and download content.

v1 targets the ``batch`` purpose (JSONL input + output files). Traffic is
forwarded verbatim to the provider chosen via ``provider`` (the
``floopy-provider`` header)."""

from __future__ import annotations

from typing import Any

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, SyncHTTP
from ..types.files import FileList, FileObject
from ..types.shared import RequestOptions
from ._batch_options import with_provider


def _list_query(purpose: str | None, limit: int | None, after: str | None) -> dict[str, Any]:
    q: dict[str, Any] = {}
    if purpose is not None:
        q["purpose"] = purpose
    if limit is not None:
        q["limit"] = limit
    if after is not None:
        q["after"] = after
    return q


class FilesResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def upload(
        self,
        *,
        file: bytes,
        purpose: str,
        filename: str = "file",
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileObject:
        data, _ = self._http.request_multipart(
            "POST",
            ENDPOINTS.FILES,
            form={"purpose": purpose},
            files={"file": (filename, file)},
            request_options=with_provider(provider, request_options),
        )
        return FileObject.from_wire(data)

    def list(
        self,
        *,
        purpose: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileList:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.FILES,
            query=_list_query(purpose, limit, after),
            request_options=with_provider(provider, request_options),
        )
        return FileList.from_wire(data)

    def retrieve(
        self,
        file_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileObject:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.file_by_id(file_id),
            request_options=with_provider(provider, request_options),
        )
        return FileObject.from_wire(data)

    def content(
        self,
        file_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> bytes:
        body, _ = self._http.request_bytes(
            "GET",
            ENDPOINTS.file_content(file_id),
            request_options=with_provider(provider, request_options),
        )
        return body

    def delete(
        self,
        file_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileObject:
        data, _ = self._http.request(
            "DELETE",
            ENDPOINTS.file_by_id(file_id),
            request_options=with_provider(provider, request_options),
        )
        return FileObject.from_wire(data)


class AsyncFilesResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def upload(
        self,
        *,
        file: bytes,
        purpose: str,
        filename: str = "file",
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileObject:
        data, _ = await self._http.request_multipart(
            "POST",
            ENDPOINTS.FILES,
            form={"purpose": purpose},
            files={"file": (filename, file)},
            request_options=with_provider(provider, request_options),
        )
        return FileObject.from_wire(data)

    async def list(
        self,
        *,
        purpose: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileList:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.FILES,
            query=_list_query(purpose, limit, after),
            request_options=with_provider(provider, request_options),
        )
        return FileList.from_wire(data)

    async def retrieve(
        self,
        file_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileObject:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.file_by_id(file_id),
            request_options=with_provider(provider, request_options),
        )
        return FileObject.from_wire(data)

    async def content(
        self,
        file_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> bytes:
        body, _ = await self._http.request_bytes(
            "GET",
            ENDPOINTS.file_content(file_id),
            request_options=with_provider(provider, request_options),
        )
        return body

    async def delete(
        self,
        file_id: str,
        *,
        provider: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FileObject:
        data, _ = await self._http.request(
            "DELETE",
            ENDPOINTS.file_by_id(file_id),
            request_options=with_provider(provider, request_options),
        )
        return FileObject.from_wire(data)
