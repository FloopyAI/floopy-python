from __future__ import annotations

import httpx
import pytest
import respx

from floopy import (
    CacheOptions,
    Floopy,
    FloopyError,
    FloopyOptions,
    FloopyRateLimitError,
)
from floopy._constants import FLOOPY_HEADERS


def test_requires_api_key() -> None:
    with pytest.raises(FloopyError):
        Floopy(api_key="")


def test_lazy_openai_delegate_reused() -> None:
    c = Floopy(api_key="fl_test")
    assert c.openai is c.openai
    assert c.chat is not None
    assert c.embeddings is not None
    assert c.models is not None
    c.close()


@respx.mock
def test_includes_floopy_headers_when_options_set() -> None:
    route = respx.get("https://gw.local/v1/decisions/abc").mock(
        return_value=httpx.Response(200, json={})
    )
    c = Floopy(
        api_key="fl_test",
        base_url="https://gw.local/v1",
        options=FloopyOptions(
            cache=CacheOptions(enabled=True, bucket_max_size=4),
            prompt_id="p1",
            llm_security_enabled=True,
        ),
    )
    c._http.request("GET", "/decisions/abc")
    req = route.calls.last.request
    assert req.headers[FLOOPY_HEADERS.AUTHORIZATION] == "Bearer fl_test"
    assert req.headers[FLOOPY_HEADERS.CACHE_ENABLED] == "true"
    assert req.headers[FLOOPY_HEADERS.CACHE_BUCKET_MAX_SIZE] == "4"
    assert req.headers[FLOOPY_HEADERS.PROMPT_ID] == "p1"
    assert req.headers[FLOOPY_HEADERS.LLM_SECURITY_ENABLED] == "true"
    assert "floopy-sdk/" in req.headers[FLOOPY_HEADERS.USER_AGENT]
    c.close()


@respx.mock
def test_maps_non_2xx_into_floopy_error_subclass() -> None:
    respx.get("https://api.floopy.ai/v1/decisions").mock(
        return_value=httpx.Response(
            429,
            json={"error": {"code": "rate_limited", "message": "slow down"}},
            headers={"Retry-After": "5", FLOOPY_HEADERS.REQUEST_ID: "req_x"},
        )
    )
    c = Floopy(api_key="fl_test", max_retries=0)
    with pytest.raises(FloopyRateLimitError) as excinfo:
        c._http.request("GET", "/decisions")
    err = excinfo.value
    assert err.status == 429
    assert err.request_id == "req_x"
    assert err.retry_after_seconds == 5
    c.close()


@respx.mock
def test_retries_5xx_up_to_max_retries() -> None:
    route = respx.get("https://api.floopy.ai/v1/decisions").mock(
        side_effect=[
            httpx.Response(503, json={}),
            httpx.Response(503, json={}),
            httpx.Response(200, json={"ok": True}),
        ]
    )
    c = Floopy(api_key="fl_test", max_retries=2)
    data, _ = c._http.request("GET", "/decisions")
    assert data == {"ok": True}
    assert route.call_count == 3
    c.close()


@respx.mock
def test_connection_error_wrapped() -> None:
    respx.get("https://api.floopy.ai/v1/decisions").mock(side_effect=httpx.ConnectError("boom"))
    from floopy import FloopyConnectionError

    c = Floopy(api_key="fl_test", max_retries=0)
    with pytest.raises(FloopyConnectionError):
        c._http.request("GET", "/decisions")
    c.close()
