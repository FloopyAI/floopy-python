from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, SyncHTTP
from ..types.routing import RoutingExplainResult
from ..types.shared import RequestOptions

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam


def _body(
    *,
    model: str,
    messages: list[ChatCompletionMessageParam],
    temperature: float | None,
    max_tokens: int | None,
    top_p: float | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {"model": model, "messages": messages}
    if temperature is not None:
        body["temperature"] = temperature
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if top_p is not None:
        body["top_p"] = top_p
    return body


class RoutingResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def explain(
        self,
        *,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        request_options: RequestOptions | None = None,
    ) -> RoutingExplainResult:
        """Routing dry-run (Pro plan). ``would_select`` is ``None`` when the
        firewall blocks the request."""
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.ROUTING_EXPLAIN,
            body=_body(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            ),
            request_options=request_options,
        )
        return RoutingExplainResult.from_wire(data)


class AsyncRoutingResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def explain(
        self,
        *,
        model: str,
        messages: list[ChatCompletionMessageParam],
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        request_options: RequestOptions | None = None,
    ) -> RoutingExplainResult:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.ROUTING_EXPLAIN,
            body=_body(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            ),
            request_options=request_options,
        )
        return RoutingExplainResult.from_wire(data)
