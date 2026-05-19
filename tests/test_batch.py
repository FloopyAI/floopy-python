from __future__ import annotations

import httpx
import respx

from floopy import AsyncFloopy, Floopy, RequestOptions
from floopy.resources._batch_options import with_provider

BASE = "https://gw.test/v1"


def make_client() -> Floopy:
    return Floopy(api_key="fl_test", base_url=BASE, max_retries=0)


# --- with_provider --------------------------------------------------------


def test_with_provider_none_returns_request_options_unchanged() -> None:
    assert with_provider(None, None) is None
    ro = RequestOptions(timeout=5.0)
    assert with_provider(None, ro) is ro


def test_with_provider_creates_options_when_absent() -> None:
    out = with_provider("openai", None)
    assert out is not None
    assert out.headers == {"floopy-provider": "openai"}
    assert out.timeout is None


def test_with_provider_merges_into_existing_options() -> None:
    ro = RequestOptions(headers={"x-trace": "t1"}, timeout=9.0)
    out = with_provider("groq", ro)
    assert out is not None
    assert out.headers == {"x-trace": "t1", "floopy-provider": "groq"}
    assert out.timeout == 9.0


# --- files (sync) ---------------------------------------------------------


@respx.mock
def test_files_upload_multipart() -> None:
    route = respx.post(f"{BASE}/files").mock(
        return_value=httpx.Response(
            200, json={"id": "file-1", "object": "file", "purpose": "batch", "status": "ok"}
        )
    )
    c = make_client()
    res = c.files.upload(file=b'{"x":1}\n', purpose="batch", filename="in.jsonl", provider="openai")
    assert res.id == "file-1"
    req = route.calls.last.request
    assert req.headers["content-type"].startswith("multipart/form-data")
    assert req.headers["floopy-provider"] == "openai"
    body = req.content.decode("utf-8", "replace")
    assert "in.jsonl" in body and "batch" in body
    c.close()


@respx.mock
def test_files_list_with_and_without_params() -> None:
    route = respx.get(f"{BASE}/files").mock(
        return_value=httpx.Response(200, json={"object": "list", "data": [{"id": "f1"}]})
    )
    c = make_client()
    page = c.files.list(purpose="batch", limit=10, after="f0")
    assert [f.id for f in page.data] == ["f1"]
    assert str(route.calls.last.request.url).endswith("/files?purpose=batch&limit=10&after=f0")
    c.files.list()
    assert str(route.calls.last.request.url).endswith("/files")
    c.close()


@respx.mock
def test_files_retrieve_content_delete() -> None:
    respx.get(f"{BASE}/files/file-1").mock(return_value=httpx.Response(200, json={"id": "file-1"}))
    respx.get(f"{BASE}/files/file-1/content").mock(
        return_value=httpx.Response(200, content=b'{"a":1}\n')
    )
    del_route = respx.delete(f"{BASE}/files/file-1").mock(
        return_value=httpx.Response(200, json={"id": "file-1", "object": "file"})
    )
    c = make_client()
    assert c.files.retrieve("file-1").id == "file-1"
    assert c.files.content("file-1", provider="openai") == b'{"a":1}\n'
    assert c.files.delete("file-1").id == "file-1"
    assert del_route.calls.last.request.method == "DELETE"
    c.close()


# --- batches (sync) -------------------------------------------------------


@respx.mock
def test_batches_create_with_and_without_metadata() -> None:
    route = respx.post(f"{BASE}/batches").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "batch_1",
                "object": "batch",
                "status": "validating",
                "request_counts": {"total": 2, "completed": 0, "failed": 0},
            },
        )
    )
    c = make_client()
    b = c.batches.create(
        input_file_id="file-1",
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"k": "v"},
        provider="openai",
    )
    assert b.id == "batch_1"
    assert b.request_counts is not None and b.request_counts.total == 2
    import json as _json

    assert _json.loads(route.calls.last.request.content)["metadata"] == {"k": "v"}
    b2 = c.batches.create(
        input_file_id="file-1", endpoint="/v1/chat/completions", completion_window="24h"
    )
    assert "metadata" not in _json.loads(route.calls.last.request.content)
    assert b2.request_counts is None or b2.id == "batch_1"
    c.close()


@respx.mock
def test_batches_list_retrieve_cancel() -> None:
    respx.get(f"{BASE}/batches").mock(
        return_value=httpx.Response(
            200, json={"object": "list", "data": [{"id": "batch_1"}], "has_more": False}
        )
    )
    respx.get(f"{BASE}/batches/batch_1").mock(
        return_value=httpx.Response(200, json={"id": "batch_1", "status": "completed"})
    )
    cancel_route = respx.post(f"{BASE}/batches/batch_1/cancel").mock(
        return_value=httpx.Response(200, json={"id": "batch_1", "status": "cancelling"})
    )
    c = make_client()
    page = c.batches.list(limit=5, after="batch_0")
    assert page.has_more is False and page.data[0].id == "batch_1"
    c.batches.list()
    assert c.batches.retrieve("batch_1").status == "completed"
    assert c.batches.cancel("batch_1", provider="openai").status == "cancelling"
    assert cancel_route.calls.last.request.method == "POST"
    c.close()


# --- async ---------------------------------------------------------------


@respx.mock
async def test_async_files_and_batches() -> None:
    respx.post(f"{BASE}/files").mock(return_value=httpx.Response(200, json={"id": "file-1"}))
    respx.get(f"{BASE}/files").mock(
        return_value=httpx.Response(200, json={"object": "list", "data": []})
    )
    respx.get(f"{BASE}/files/file-1").mock(return_value=httpx.Response(200, json={"id": "file-1"}))
    respx.get(f"{BASE}/files/file-1/content").mock(
        return_value=httpx.Response(200, content=b"data")
    )
    respx.delete(f"{BASE}/files/file-1").mock(
        return_value=httpx.Response(200, json={"id": "file-1"})
    )
    respx.post(f"{BASE}/batches").mock(return_value=httpx.Response(200, json={"id": "batch_1"}))
    respx.get(f"{BASE}/batches").mock(
        return_value=httpx.Response(200, json={"object": "list", "data": []})
    )
    respx.get(f"{BASE}/batches/batch_1").mock(
        return_value=httpx.Response(200, json={"id": "batch_1"})
    )
    respx.post(f"{BASE}/batches/batch_1/cancel").mock(
        return_value=httpx.Response(200, json={"id": "batch_1"})
    )
    async with AsyncFloopy(api_key="fl_test", base_url=BASE, max_retries=0) as c:
        assert (await c.files.upload(file=b"x", purpose="batch", provider="openai")).id == "file-1"
        assert (await c.files.list(purpose="batch")).data == []
        assert (await c.files.retrieve("file-1")).id == "file-1"
        assert await c.files.content("file-1") == b"data"
        assert (await c.files.delete("file-1")).id == "file-1"
        assert (
            await c.batches.create(
                input_file_id="file-1",
                endpoint="/v1/chat/completions",
                completion_window="24h",
                provider="openai",
            )
        ).id == "batch_1"
        assert (await c.batches.list(limit=1)).data == []
        assert (await c.batches.retrieve("batch_1")).id == "batch_1"
        assert (await c.batches.cancel("batch_1")).id == "batch_1"
