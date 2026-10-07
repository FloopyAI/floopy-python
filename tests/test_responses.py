from __future__ import annotations

import json
from typing import Any

import httpx2
import pytest
from openai import AsyncOpenAI, OpenAI

from floopy import AsyncFloopy, Floopy, FloopyOptions, _openai_delegate

OUTPUT = {
    "id": "resp_test",
    "object": "response",
    "created_at": 1,
    "model": "gpt-6-luna",
    "status": "completed",
    "output": [
        {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "status": "completed",
            "content": [{"type": "output_text", "text": "Olá", "annotations": []}],
        }
    ],
}


def test_native_responses_and_gateway_options(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        return httpx2.Response(200, json=OUTPUT)

    def factory(**kwargs: Any) -> OpenAI:
        return OpenAI(**kwargs, http_client=httpx2.Client(transport=httpx2.MockTransport(handle)))

    monkeypatch.setattr(_openai_delegate, "OpenAI", factory)
    with Floopy(
        api_key="fl_test",
        base_url="https://gw.local/v1",
        max_retries=0,
        timeout=2.0,
        options=FloopyOptions(llm_security_enabled=True),
    ) as client:
        response = client.responses.create(
            model="gpt-6-luna", input="hi", reasoning={"effort": "medium"}, store=False
        )
        assert response.output_text == "Olá"
        assert client.openai.timeout == 2.0
        assert client.responses is client.openai.responses
    request = seen[0]
    assert str(request.url) == "https://gw.local/v1/responses"
    assert request.headers["authorization"] == "Bearer fl_test"
    assert request.headers["floopy-llm-security-enabled"] == "true"
    assert json.loads(request.content)["reasoning"] == {"effort": "medium"}


@pytest.mark.asyncio
async def test_async_native_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    event = {
        "type": "response.output_text.delta",
        "sequence_number": 0,
        "delta": "Olá",
        "item_id": "msg_1",
        "output_index": 0,
        "content_index": 0,
    }
    frames = f"event: response.output_text.delta\ndata: {json.dumps(event)}\n\nevent: response.completed\ndata: {json.dumps({'type': 'response.completed', 'sequence_number': 1, 'response': OUTPUT})}\n\n"

    def handle(request: httpx2.Request) -> httpx2.Response:
        assert request.url.path == "/v1/responses"
        assert json.loads(request.content)["stream"] is True
        return httpx2.Response(200, text=frames, headers={"content-type": "text/event-stream"})

    def factory(**kwargs: Any) -> AsyncOpenAI:
        return AsyncOpenAI(
            **kwargs, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle))
        )

    monkeypatch.setattr(_openai_delegate, "AsyncOpenAI", factory)
    async with AsyncFloopy(
        api_key="fl_test", base_url="https://gw.local/v1", max_retries=0
    ) as client:
        stream = await client.responses.create(model="gpt-6-luna", input="hi", stream=True)
        events = [item async for item in stream]
    assert events[0].type == "response.output_text.delta"
    assert events[1].type == "response.completed"
