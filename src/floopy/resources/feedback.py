from __future__ import annotations

from typing import Any

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, SyncHTTP
from ..types.feedback import FeedbackSubmitResponse
from ..types.shared import RequestOptions


def _body(score: int, useful: bool, session_id: str | None) -> dict[str, Any]:
    body: dict[str, Any] = {"score": score, "useful": useful}
    if session_id is not None:
        body["session_id"] = session_id
    return body


class FeedbackResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def submit(
        self,
        *,
        score: int,
        useful: bool,
        session_id: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FeedbackSubmitResponse:
        data, _ = self._http.request(
            "POST",
            ENDPOINTS.FEEDBACK,
            body=_body(score, useful, session_id),
            request_options=request_options,
        )
        return FeedbackSubmitResponse.from_wire(data)


class AsyncFeedbackResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def submit(
        self,
        *,
        score: int,
        useful: bool,
        session_id: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> FeedbackSubmitResponse:
        data, _ = await self._http.request(
            "POST",
            ENDPOINTS.FEEDBACK,
            body=_body(score, useful, session_id),
            request_options=request_options,
        )
        return FeedbackSubmitResponse.from_wire(data)
