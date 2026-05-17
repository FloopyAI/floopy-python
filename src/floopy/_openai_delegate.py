"""Build ``openai`` / ``AsyncOpenAI`` clients pre-pointed at the Floopy
gateway. Mirrors ``src/openai-delegate.ts``.

The ``openai`` SDK manages auth, content-type and user-agent itself, so those
headers are stripped from the forwarded Floopy header set; the remaining
``Floopy-*`` toggles ride along on every OpenAI-compatible call.
"""

from __future__ import annotations

from openai import AsyncOpenAI, OpenAI

from ._constants import DEFAULT_USER_AGENT_PREFIX, FLOOPY_HEADERS
from ._headers import build_floopy_headers, merge_headers
from ._http import AsyncHTTP, SyncHTTP
from ._version import __version__


def _delegate_headers(default_request_headers: dict[str, str]) -> dict[str, str]:
    headers = merge_headers(build_floopy_headers(None), default_request_headers)
    for managed in (
        FLOOPY_HEADERS.AUTHORIZATION,
        FLOOPY_HEADERS.CONTENT_TYPE,
        FLOOPY_HEADERS.USER_AGENT,
    ):
        headers.pop(managed, None)
    headers["X-Floopy-SDK"] = f"{DEFAULT_USER_AGENT_PREFIX}/{__version__}"
    return headers


def create_openai_delegate(http: SyncHTTP) -> OpenAI:
    return OpenAI(
        api_key=http.api_key,
        base_url=http.base_url,
        default_headers=_delegate_headers(http.get_default_request_headers()),
    )


def create_async_openai_delegate(http: AsyncHTTP) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=http.api_key,
        base_url=http.base_url,
        default_headers=_delegate_headers(http.get_default_request_headers()),
    )
