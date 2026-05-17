from __future__ import annotations

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, SyncHTTP
from ..types.sessions import Session
from ..types.shared import RequestOptions


class SessionsResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, session_id: str, *, request_options: RequestOptions | None = None) -> Session:
        """Restore a stored conversation by its ``session_id`` (the value
        sent on the ``floopy-session-id`` header at request time). Scoped to
        the API key's organization; the returned ``messages`` are a drop-in
        for a follow-up chat completion."""
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.session_by_id(session_id),
            request_options=request_options,
        )
        return Session.from_wire(data)


class AsyncSessionsResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(
        self, session_id: str, *, request_options: RequestOptions | None = None
    ) -> Session:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.session_by_id(session_id),
            request_options=request_options,
        )
        return Session.from_wire(data)
