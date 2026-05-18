"""Internal HTTP transport for Floopy-only endpoints.

Mirrors ``src/http.ts``: bearer auth, ``Floopy-*`` header injection, bounded
retries with exponential backoff + jitter (``Retry-After`` honoured),
per-call timeouts, request-id capture, and mapping of non-2xx responses to
:class:`FloopyError` subclasses.

The OpenAI-compatible surface (``chat``/``embeddings``/``models``) does *not*
go through here — it is delegated to the ``openai`` SDK.

Security: the API key only ever appears in the ``Authorization`` header and
is masked in ``repr``. Request/response bodies are never logged by the SDK.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import random
import time
from collections.abc import AsyncIterator, Iterator
from typing import Any, cast
from urllib.parse import urlencode

import httpx

from ._constants import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_USER_AGENT_PREFIX,
    FLOOPY_HEADERS,
)
from ._errors import (
    FloopyConnectionError,
    FloopyError,
    FloopyTimeoutError,
    error_from_status,
)
from ._headers import build_floopy_headers, merge_headers
from ._version import __version__
from .types.shared import FloopyOptions, RequestOptions

RETRYABLE_STATUS: frozenset[int] = frozenset({408, 409, 425, 429, 500, 502, 503, 504})

QueryValue = str | int | float | bool | None
Query = dict[str, QueryValue]


def _python_version() -> str:
    import platform

    return platform.python_version()


class _BaseHTTP:
    """I/O-free helpers shared by the sync and async transports."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None,
        timeout: float | None,
        max_retries: int | None,
        default_headers: dict[str, str] | None,
        default_options: FloopyOptions | None,
    ) -> None:
        if not api_key:
            raise FloopyError("api_key is required to construct a Floopy client")
        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = DEFAULT_TIMEOUT_SECONDS if timeout is None else timeout
        self._max_retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries
        self._default_headers = dict(default_headers or {})
        self._default_options = default_options

    # --- pure helpers ----------------------------------------------------

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_key(self) -> str:
        return self._api_key

    def get_default_request_headers(self) -> dict[str, str]:
        return merge_headers(
            self._default_headers,
            build_floopy_headers(self._default_options),
            self._auth_and_ua_headers(),
        )

    def _auth_and_ua_headers(self) -> dict[str, str]:
        return {
            FLOOPY_HEADERS.AUTHORIZATION: f"Bearer {self._api_key}",
            FLOOPY_HEADERS.USER_AGENT: (
                f"{DEFAULT_USER_AGENT_PREFIX}/{__version__} python/{_python_version()}"
            ),
        }

    def _build_request_headers(self, req_opts: RequestOptions | None) -> dict[str, str]:
        return merge_headers(
            self._default_headers,
            build_floopy_headers(self._default_options),
            build_floopy_headers(req_opts.options if req_opts else None),
            self._auth_and_ua_headers(),
            req_opts.headers if req_opts else None,
        )

    def _build_url(self, path: str, query: Query | None) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        url = f"{self._base_url}{normalized}"
        if query:
            pairs = [(k, str(v)) for k, v in query.items() if v is not None]
            if pairs:
                url = f"{url}?{urlencode(pairs)}"
        return url

    def _timeout_for(self, req_opts: RequestOptions | None) -> float:
        if req_opts is not None and req_opts.timeout is not None:
            return req_opts.timeout
        return self._timeout

    def _error_from_parts(self, *, status: int, headers: httpx.Headers, text: str) -> FloopyError:
        request_id = headers.get(FLOOPY_HEADERS.REQUEST_ID) or None
        body: dict[str, Any] | str | None
        if text:
            try:
                body = cast("dict[str, Any]", json.loads(text))
            except ValueError:
                body = text
        else:
            body = None
        err = error_from_status(status=status, body=body, request_id=request_id)
        if err.__class__.__name__ == "FloopyRateLimitError":
            retry_after = headers.get("Retry-After")
            if retry_after is not None:
                with contextlib.suppress(ValueError):
                    err.retry_after_seconds = int(retry_after)  # type: ignore[attr-defined]
        return err

    def _backoff_seconds(self, attempt: int, retry_after_header: str | None) -> float:
        if retry_after_header is not None:
            try:
                seconds = int(retry_after_header)
            except ValueError:
                seconds = -1
            if seconds > 0:
                return float(seconds)
        base: float = 0.25 * float(2**attempt)
        jitter: float = random.random() * base * 0.25
        return base + jitter

    def __repr__(self) -> str:  # pragma: no cover - cosmetic, key never shown
        return f"<{type(self).__name__} base_url={self._base_url!r} api_key=***>"


def _normalize_query(query: Query | None) -> Query | None:
    return query


class SyncHTTP(_BaseHTTP):
    """Blocking transport backed by :class:`httpx.Client`."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict[str, str] | None = None,
        default_options: FloopyOptions | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_options=default_options,
        )
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(timeout=self._timeout)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any | None = None,
        query: Query | None = None,
        request_options: RequestOptions | None = None,
    ) -> tuple[Any, str | None]:
        response = self._request_raw(
            method, path, body=body, query=query, request_options=request_options
        )
        request_id = response.headers.get(FLOOPY_HEADERS.REQUEST_ID) or None
        if response.status_code == 204:
            return None, request_id
        text = response.text
        data = json.loads(text) if text else None
        return data, request_id

    def request_bytes(
        self,
        method: str,
        path: str,
        *,
        query: Query | None = None,
        request_options: RequestOptions | None = None,
    ) -> tuple[bytes, str | None]:
        """Like :meth:`request` but returns the raw body bytes (no JSON
        parsing) — used to download file content."""
        response = self._request_raw(method, path, query=query, request_options=request_options)
        request_id = response.headers.get(FLOOPY_HEADERS.REQUEST_ID) or None
        return response.content, request_id

    def request_multipart(
        self,
        method: str,
        path: str,
        *,
        form: dict[str, Any],
        files: dict[str, Any],
        request_options: RequestOptions | None = None,
    ) -> tuple[Any, str | None]:
        """Send a ``multipart/form-data`` request (file upload)."""
        response = self._request_raw(
            method, path, files=files, form=form, request_options=request_options
        )
        request_id = response.headers.get(FLOOPY_HEADERS.REQUEST_ID) or None
        if response.status_code == 204:
            return None, request_id
        text = response.text
        data = json.loads(text) if text else None
        return data, request_id

    def _request_raw(
        self,
        method: str,
        path: str,
        *,
        body: Any | None = None,
        query: Query | None = None,
        files: Any | None = None,
        form: Any | None = None,
        request_options: RequestOptions | None = None,
    ) -> httpx.Response:
        url = self._build_url(path, _normalize_query(query))
        headers = self._build_request_headers(request_options)
        multipart = files is not None or form is not None
        content: bytes | None = None
        # Multipart uploads are handed to httpx via ``files``/``data`` so it
        # sets the ``multipart/form-data`` boundary itself — never JSON
        # encoded and never given an explicit Content-Type.
        if body is not None and not multipart:
            content = json.dumps(body).encode("utf-8")
            headers.setdefault(FLOOPY_HEADERS.CONTENT_TYPE, "application/json")
        timeout = self._timeout_for(request_options)

        attempt = 0
        while True:
            try:
                if multipart:
                    response = self._client.request(
                        method, url, headers=headers, data=form, files=files, timeout=timeout
                    )
                else:
                    response = self._client.request(
                        method, url, headers=headers, content=content, timeout=timeout
                    )
            except httpx.TimeoutException as err:
                raise FloopyTimeoutError(f"Request timed out after {timeout}s", err) from err
            except httpx.RequestError as err:
                if attempt < self._max_retries:
                    time.sleep(self._backoff_seconds(attempt, None))
                    attempt += 1
                    continue
                raise FloopyConnectionError("Network error talking to Floopy gateway", err) from err

            if response.is_success:
                return response
            if attempt < self._max_retries and response.status_code in RETRYABLE_STATUS:
                time.sleep(self._backoff_seconds(attempt, response.headers.get("Retry-After")))
                attempt += 1
                response.close()
                continue
            mapped_error = self._error_from_parts(
                status=response.status_code,
                headers=response.headers,
                text=response.text,
            )
            response.close()
            raise mapped_error

    def stream_lines(
        self,
        method: str,
        path: str,
        *,
        query: Query | None = None,
        request_options: RequestOptions | None = None,
    ) -> Iterator[dict[str, Any]]:
        url = self._build_url(path, _normalize_query(query))
        headers = self._build_request_headers(request_options)
        timeout = self._timeout_for(request_options)
        try:
            with self._client.stream(method, url, headers=headers, timeout=timeout) as response:
                if not response.is_success:
                    body_text = response.read().decode("utf-8", "replace")
                    raise self._error_from_parts(
                        status=response.status_code,
                        headers=response.headers,
                        text=body_text,
                    )
                for line in response.iter_lines():
                    stripped = line.strip()
                    if stripped:
                        yield json.loads(stripped)
        except httpx.TimeoutException as err:
            raise FloopyTimeoutError(f"Request timed out after {timeout}s", err) from err
        except httpx.RequestError as err:
            raise FloopyConnectionError("Network error talking to Floopy gateway", err) from err

    def __enter__(self) -> SyncHTTP:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class AsyncHTTP(_BaseHTTP):
    """Awaitable transport backed by :class:`httpx.AsyncClient`."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict[str, str] | None = None,
        default_options: FloopyOptions | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_options=default_options,
        )
        self._owns_client = http_client is None
        self._client = http_client or httpx.AsyncClient(timeout=self._timeout)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: Any | None = None,
        query: Query | None = None,
        request_options: RequestOptions | None = None,
    ) -> tuple[Any, str | None]:
        response = await self._request_raw(
            method, path, body=body, query=query, request_options=request_options
        )
        request_id = response.headers.get(FLOOPY_HEADERS.REQUEST_ID) or None
        if response.status_code == 204:
            return None, request_id
        text = response.text
        data = json.loads(text) if text else None
        return data, request_id

    async def request_bytes(
        self,
        method: str,
        path: str,
        *,
        query: Query | None = None,
        request_options: RequestOptions | None = None,
    ) -> tuple[bytes, str | None]:
        """Like :meth:`request` but returns the raw body bytes (no JSON
        parsing) — used to download file content."""
        response = await self._request_raw(
            method, path, query=query, request_options=request_options
        )
        request_id = response.headers.get(FLOOPY_HEADERS.REQUEST_ID) or None
        return response.content, request_id

    async def request_multipart(
        self,
        method: str,
        path: str,
        *,
        form: dict[str, Any],
        files: dict[str, Any],
        request_options: RequestOptions | None = None,
    ) -> tuple[Any, str | None]:
        """Send a ``multipart/form-data`` request (file upload)."""
        response = await self._request_raw(
            method, path, files=files, form=form, request_options=request_options
        )
        request_id = response.headers.get(FLOOPY_HEADERS.REQUEST_ID) or None
        if response.status_code == 204:
            return None, request_id
        text = response.text
        data = json.loads(text) if text else None
        return data, request_id

    async def _request_raw(
        self,
        method: str,
        path: str,
        *,
        body: Any | None = None,
        query: Query | None = None,
        files: Any | None = None,
        form: Any | None = None,
        request_options: RequestOptions | None = None,
    ) -> httpx.Response:
        url = self._build_url(path, _normalize_query(query))
        headers = self._build_request_headers(request_options)
        multipart = files is not None or form is not None
        content: bytes | None = None
        if body is not None and not multipart:
            content = json.dumps(body).encode("utf-8")
            headers.setdefault(FLOOPY_HEADERS.CONTENT_TYPE, "application/json")
        timeout = self._timeout_for(request_options)

        attempt = 0
        while True:
            try:
                if multipart:
                    response = await self._client.request(
                        method, url, headers=headers, data=form, files=files, timeout=timeout
                    )
                else:
                    response = await self._client.request(
                        method, url, headers=headers, content=content, timeout=timeout
                    )
            except httpx.TimeoutException as err:
                raise FloopyTimeoutError(f"Request timed out after {timeout}s", err) from err
            except httpx.RequestError as err:
                if attempt < self._max_retries:
                    await asyncio.sleep(self._backoff_seconds(attempt, None))
                    attempt += 1
                    continue
                raise FloopyConnectionError("Network error talking to Floopy gateway", err) from err

            if response.is_success:
                return response
            if attempt < self._max_retries and response.status_code in RETRYABLE_STATUS:
                await asyncio.sleep(
                    self._backoff_seconds(attempt, response.headers.get("Retry-After"))
                )
                attempt += 1
                await response.aclose()
                continue
            mapped_error = self._error_from_parts(
                status=response.status_code,
                headers=response.headers,
                text=response.text,
            )
            await response.aclose()
            raise mapped_error

    async def stream_lines(
        self,
        method: str,
        path: str,
        *,
        query: Query | None = None,
        request_options: RequestOptions | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        url = self._build_url(path, _normalize_query(query))
        headers = self._build_request_headers(request_options)
        timeout = self._timeout_for(request_options)
        try:
            async with self._client.stream(
                method, url, headers=headers, timeout=timeout
            ) as response:
                if not response.is_success:
                    body_bytes = await response.aread()
                    raise self._error_from_parts(
                        status=response.status_code,
                        headers=response.headers,
                        text=body_bytes.decode("utf-8", "replace"),
                    )
                async for line in response.aiter_lines():
                    stripped = line.strip()
                    if stripped:
                        yield json.loads(stripped)
        except httpx.TimeoutException as err:
            raise FloopyTimeoutError(f"Request timed out after {timeout}s", err) from err
        except httpx.RequestError as err:
            raise FloopyConnectionError("Network error talking to Floopy gateway", err) from err

    async def __aenter__(self) -> AsyncHTTP:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()
