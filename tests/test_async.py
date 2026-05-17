from __future__ import annotations

import json

import httpx
import pytest
import respx

from floopy import AsyncFloopy, FloopyRateLimitError
from floopy._constants import FLOOPY_CONFIRM_VALUES, FLOOPY_HEADERS

BASE = "https://gw.test/v1"


@respx.mock
async def test_async_feedback_submit() -> None:
    route = respx.post(f"{BASE}/feedback").mock(
        return_value=httpx.Response(200, json={"duplicate": True, "session_id": None})
    )
    async with AsyncFloopy(api_key="fl_test", base_url=BASE, max_retries=0) as c:
        res = await c.feedback.submit(score=3, useful=False)
    assert res.duplicate is True
    assert res.session_id is None
    assert json.loads(route.calls.last.request.content) == {
        "score": 3,
        "useful": False,
    }


@respx.mock
async def test_async_decisions_iterate_paginates() -> None:
    def page(rid: str, cursor: str | None, more: bool) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "request_id": rid,
                        "session_id": None,
                        "request_created_at": "2026-05-10T00:00:00Z",
                        "provider": None,
                        "model": None,
                        "status": "ok",
                        "latency_ms": None,
                        "cost_micro_usd": None,
                        "cache_enabled": None,
                        "threat": None,
                        "decision_trace": None,
                        "confidence": None,
                        "confidence_reason": None,
                        "explanation": None,
                    }
                ],
                "next_cursor": cursor,
                "has_more": more,
            },
        )

    respx.get(f"{BASE}/decisions").mock(side_effect=[page("a", "c1", True), page("b", None, False)])
    seen = []
    async with AsyncFloopy(api_key="fl_test", base_url=BASE, max_retries=0) as c:
        async for d in c.decisions.iterate(from_="2026-05-01T00:00:00Z"):
            seen.append(d.request_id)
    assert seen == ["a", "b"]


@respx.mock
async def test_async_export_stream_with_trailer() -> None:
    rows = [
        {
            "request_id": "req_1",
            "session_id": None,
            "organization_id": "org_1",
            "provider": None,
            "model": None,
            "status": "ok",
            "latency_ms": None,
            "cost_micro_usd": None,
            "cache_enabled": None,
            "threat": None,
            "created_at": "2026-05-10T00:00:00Z",
        },
        {"trailer": True, "rows_emitted": 1, "truncated": False, "reason": None},
    ]
    respx.get(f"{BASE}/export/decisions").mock(
        return_value=httpx.Response(200, text="\n".join(json.dumps(r) for r in rows))
    )
    async with AsyncFloopy(api_key="fl_test", base_url=BASE, max_retries=0) as c:
        stream = c.export.decisions_with_trailer(
            from_="2026-05-01T00:00:00Z", to="2026-06-01T00:00:00Z"
        )
        collected = [row async for row in stream]
    assert [r.request_id for r in collected] == ["req_1"]
    assert stream.trailer is not None
    assert stream.trailer.rows_emitted == 1


@respx.mock
async def test_async_experiments_confirm_header() -> None:
    route = respx.post(f"{BASE}/experiments").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "exp_1",
                "name": "n",
                "description": None,
                "status": "active",
                "variant_a_routing_rule_id": "a",
                "variant_b_routing_rule_id": "b",
                "split_percentage": 50,
                "created_at": "2026-05-10T00:00:00Z",
                "rolled_back_at": None,
            },
        )
    )
    async with AsyncFloopy(api_key="fl_test", base_url=BASE, max_retries=0) as c:
        await c.experiments.create(
            name="n", variant_a_routing_rule_id="a", variant_b_routing_rule_id="b"
        )
    assert (
        route.calls.last.request.headers[FLOOPY_HEADERS.CONFIRM]
        == FLOOPY_CONFIRM_VALUES.EXPERIMENTS
    )


@respx.mock
async def test_async_error_mapping() -> None:
    respx.get(f"{BASE}/decisions/x").mock(
        return_value=httpx.Response(
            429,
            json={"error": {"message": "slow"}},
            headers={"Retry-After": "7"},
        )
    )
    async with AsyncFloopy(api_key="fl_test", base_url=BASE, max_retries=0) as c:
        with pytest.raises(FloopyRateLimitError) as excinfo:
            await c.decisions.get("x")
    assert excinfo.value.retry_after_seconds == 7
