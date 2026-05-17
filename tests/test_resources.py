from __future__ import annotations

import json

import httpx
import respx

from floopy import Floopy, OrgConstraints, RequestOptions
from floopy._constants import FLOOPY_CONFIRM_VALUES, FLOOPY_HEADERS

BASE = "https://gw.test/v1"


def make_client() -> Floopy:
    return Floopy(api_key="fl_test", base_url=BASE, max_retries=0)


def _decision_wire(rid: str) -> dict[str, object]:
    return {
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


def _experiment_wire(eid: str) -> dict[str, object]:
    return {
        "id": eid,
        "name": "test",
        "description": None,
        "status": "active",
        "variant_a_routing_rule_id": "rule_a",
        "variant_b_routing_rule_id": "rule_b",
        "split_percentage": 50,
        "created_at": "2026-05-10T00:00:00Z",
        "rolled_back_at": None,
    }


@respx.mock
def test_feedback_posts_snake_case_body() -> None:
    route = respx.post(f"{BASE}/feedback").mock(
        return_value=httpx.Response(200, json={"duplicate": False, "session_id": "s1"})
    )
    c = make_client()
    res = c.feedback.submit(score=9, useful=True, session_id="s1")
    assert res.duplicate is False
    assert res.session_id == "s1"
    assert json.loads(route.calls.last.request.content) == {
        "score": 9,
        "useful": True,
        "session_id": "s1",
    }
    c.close()


@respx.mock
def test_decisions_maps_wire_to_snake_case() -> None:
    respx.get(f"{BASE}/decisions/req_1").mock(
        return_value=httpx.Response(
            200,
            json={
                **_decision_wire("req_1"),
                "latency_ms": 123,
                "cache_enabled": True,
                "decision_trace": {"nodes": []},
                "confidence": 0.9,
            },
        )
    )
    c = make_client()
    d = c.decisions.get("req_1")
    assert d.request_id == "req_1"
    assert d.latency_ms == 123
    assert d.cache_enabled is True
    c.close()


@respx.mock
def test_decisions_paginate_via_pages() -> None:
    respx.get(f"{BASE}/decisions").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "items": [_decision_wire("req_1")],
                    "next_cursor": "cur_1",
                    "has_more": True,
                },
            ),
            httpx.Response(
                200,
                json={
                    "items": [_decision_wire("req_2")],
                    "next_cursor": None,
                    "has_more": False,
                },
            ),
        ]
    )
    c = make_client()
    ids = [
        d.request_id for page in c.decisions.pages(from_="2026-05-01T00:00:00Z") for d in page.items
    ]
    assert ids == ["req_1", "req_2"]
    c.close()


@respx.mock
def test_experiments_inject_confirm_header() -> None:
    create = respx.post(f"{BASE}/experiments").mock(
        return_value=httpx.Response(200, json=_experiment_wire("exp_1"))
    )
    rollback = respx.post(f"{BASE}/experiments/exp_1/rollback").mock(
        return_value=httpx.Response(200, json=_experiment_wire("exp_1"))
    )
    c = make_client()
    c.experiments.create(
        name="test",
        variant_a_routing_rule_id="rule_a",
        variant_b_routing_rule_id="rule_b",
    )
    c.experiments.rollback("exp_1")
    for route in (create, rollback):
        assert (
            route.calls.last.request.headers[FLOOPY_HEADERS.CONFIRM]
            == FLOOPY_CONFIRM_VALUES.EXPERIMENTS
        )
    c.close()


@respx.mock
def test_constraints_uses_put_and_maps_nulls() -> None:
    route = respx.put(f"{BASE}/constraints").mock(
        return_value=httpx.Response(
            200,
            json={
                "cost_limit_monthly_usd": 100,
                "token_window_seconds": None,
                "max_tokens_per_window": None,
                "max_requests_per_minute": 60,
            },
        )
    )
    c = make_client()
    res = c.constraints.put(OrgConstraints(cost_limit_monthly_usd=100, max_requests_per_minute=60))
    assert route.calls.last.request.method == "PUT"
    assert res.cost_limit_monthly_usd == 100
    assert res.token_window_seconds is None
    c.close()


@respx.mock
def test_export_yields_rows_and_skips_trailer() -> None:
    rows = [
        {
            "request_id": "req_1",
            "session_id": None,
            "organization_id": "org_1",
            "provider": "openai",
            "model": "gpt-4o",
            "status": "ok",
            "latency_ms": 100,
            "cost_micro_usd": 1000,
            "cache_enabled": False,
            "threat": None,
            "created_at": "2026-05-10T00:00:00Z",
        },
        {
            "request_id": "req_2",
            "session_id": None,
            "organization_id": "org_1",
            "provider": "openai",
            "model": "gpt-4o",
            "status": "ok",
            "latency_ms": 200,
            "cost_micro_usd": 2000,
            "cache_enabled": False,
            "threat": None,
            "created_at": "2026-05-10T00:01:00Z",
        },
        {"trailer": True, "rows_emitted": 2, "truncated": False, "reason": None},
    ]
    body = "\n".join(json.dumps(r) for r in rows)
    respx.get(f"{BASE}/export/decisions").mock(
        return_value=httpx.Response(
            200, text=body, headers={"Content-Type": "application/x-ndjson"}
        )
    )
    c = make_client()
    collected = list(c.export.decisions(from_="2026-05-01T00:00:00Z", to="2026-06-01T00:00:00Z"))
    assert [r.request_id for r in collected] == ["req_1", "req_2"]
    c.close()


@respx.mock
def test_export_with_trailer_capture() -> None:
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
        {"trailer": True, "rows_emitted": 1, "truncated": True, "reason": "deadline"},
    ]
    body = "\n".join(json.dumps(r) for r in rows)
    respx.get(f"{BASE}/export/decisions").mock(return_value=httpx.Response(200, text=body))
    c = make_client()
    stream = c.export.decisions_with_trailer(
        from_="2026-05-01T00:00:00Z", to="2026-06-01T00:00:00Z"
    )
    collected = list(stream)
    assert len(collected) == 1
    assert stream.trailer is not None
    assert stream.trailer.truncated is True
    assert stream.trailer.reason == "deadline"
    c.close()


@respx.mock
def test_routing_explain_maps_wire() -> None:
    respx.post(f"{BASE}/routing/explain").mock(
        return_value=httpx.Response(
            200,
            json={
                "would_select": {"provider": "openai", "model": "gpt-4o-mini"},
                "firewall_decision": "allow",
                "reasoning": None,
                "routing_rule_id": "rule_1",
            },
        )
    )
    c = make_client()
    res = c.routing.explain(model="gpt-4o", messages=[{"role": "user", "content": "hi"}])
    assert res.would_select == {"provider": "openai", "model": "gpt-4o-mini"}
    assert res.firewall_decision == "allow"
    c.close()


@respx.mock
def test_evaluations_create() -> None:
    route = respx.post(f"{BASE}/evaluations").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "eval_1",
                "dataset_id": "ds_1",
                "model": "gpt-4o",
                "prompt_id": None,
                "status": "pending",
                "config": None,
                "created_at": "2026-05-10T00:00:00Z",
                "started_at": None,
                "finished_at": None,
            },
        )
    )
    c = make_client()
    run = c.evaluations.create(dataset_id="ds_1", model="gpt-4o")
    assert run.id == "eval_1"
    assert json.loads(route.calls.last.request.content) == {
        "dataset_id": "ds_1",
        "model": "gpt-4o",
    }
    c.close()


@respx.mock
def test_sessions_get_maps_and_encodes_path() -> None:
    route = respx.get(f"{BASE}/session/sess%2F1").mock(
        return_value=httpx.Response(
            200,
            json={
                "session_id": "sess/1",
                "messages": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hello"},
                ],
                "turn_count": 1,
                "turns": [
                    {
                        "request_id": "r1",
                        "created_at": "2026-05-17T10:00:00Z",
                        "model": "gpt-4o",
                        "provider": "openai",
                    }
                ],
            },
        )
    )
    c = make_client()
    s = c.sessions.get("sess/1", request_options=_opts({"x-trace": "abc"}))
    assert route.calls.last.request.headers["x-trace"] == "abc"
    assert s.session_id == "sess/1"
    assert s.turn_count == 1
    assert s.turns[0].request_id == "r1"
    c.close()


def _opts(headers: dict[str, str]) -> RequestOptions:
    return RequestOptions(headers=headers)
