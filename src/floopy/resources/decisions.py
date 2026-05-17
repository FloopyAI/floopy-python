from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, Query, SyncHTTP
from ..types.decisions import Decision, DecisionListPage
from ..types.shared import RequestOptions


def _list_query(
    *,
    session_id: str | None,
    from_: str | None,
    to: str | None,
    limit: int | None,
    cursor: str | None,
) -> Query:
    query: Query = {}
    if session_id is not None:
        query["session_id"] = session_id
    if from_ is not None:
        query["from"] = from_
    if to is not None:
        query["to"] = to
    if limit is not None:
        query["limit"] = limit
    if cursor is not None:
        query["cursor"] = cursor
    return query


class DecisionsResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, request_id: str, *, request_options: RequestOptions | None = None) -> Decision:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.decision_by_id(request_id),
            request_options=request_options,
        )
        return Decision.from_wire(data)

    def list(
        self,
        *,
        session_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> DecisionListPage:
        return self._fetch_page(
            session_id=session_id,
            from_=from_,
            to=to,
            limit=limit,
            cursor=cursor,
            request_options=request_options,
        )

    def pages(
        self,
        *,
        session_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Iterator[DecisionListPage]:
        """Yield one :class:`DecisionListPage` per network round-trip."""
        next_cursor = cursor
        while True:
            page = self._fetch_page(
                session_id=session_id,
                from_=from_,
                to=to,
                limit=limit,
                cursor=next_cursor,
                request_options=request_options,
            )
            yield page
            if not page.has_more or page.next_cursor is None:
                return
            next_cursor = page.next_cursor

    def iterate(
        self,
        *,
        session_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> Iterator[Decision]:
        """Yield every decision across all pages."""
        for page in self.pages(
            session_id=session_id,
            from_=from_,
            to=to,
            limit=limit,
            cursor=cursor,
            request_options=request_options,
        ):
            yield from page.items

    def _fetch_page(
        self,
        *,
        session_id: str | None,
        from_: str | None,
        to: str | None,
        limit: int | None,
        cursor: str | None,
        request_options: RequestOptions | None,
    ) -> DecisionListPage:
        data, _ = self._http.request(
            "GET",
            ENDPOINTS.DECISIONS,
            query=_list_query(
                session_id=session_id, from_=from_, to=to, limit=limit, cursor=cursor
            ),
            request_options=request_options,
        )
        return DecisionListPage.from_wire(data)


class AsyncDecisionsResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(
        self, request_id: str, *, request_options: RequestOptions | None = None
    ) -> Decision:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.decision_by_id(request_id),
            request_options=request_options,
        )
        return Decision.from_wire(data)

    async def list(
        self,
        *,
        session_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> DecisionListPage:
        return await self._fetch_page(
            session_id=session_id,
            from_=from_,
            to=to,
            limit=limit,
            cursor=cursor,
            request_options=request_options,
        )

    async def pages(
        self,
        *,
        session_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> AsyncIterator[DecisionListPage]:
        next_cursor = cursor
        while True:
            page = await self._fetch_page(
                session_id=session_id,
                from_=from_,
                to=to,
                limit=limit,
                cursor=next_cursor,
                request_options=request_options,
            )
            yield page
            if not page.has_more or page.next_cursor is None:
                return
            next_cursor = page.next_cursor

    async def iterate(
        self,
        *,
        session_id: str | None = None,
        from_: str | None = None,
        to: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        request_options: RequestOptions | None = None,
    ) -> AsyncIterator[Decision]:
        async for page in self.pages(
            session_id=session_id,
            from_=from_,
            to=to,
            limit=limit,
            cursor=cursor,
            request_options=request_options,
        ):
            for item in page.items:
                yield item

    async def _fetch_page(
        self,
        *,
        session_id: str | None,
        from_: str | None,
        to: str | None,
        limit: int | None,
        cursor: str | None,
        request_options: RequestOptions | None,
    ) -> DecisionListPage:
        data, _ = await self._http.request(
            "GET",
            ENDPOINTS.DECISIONS,
            query=_list_query(
                session_id=session_id, from_=from_, to=to, limit=limit, cursor=cursor
            ),
            request_options=request_options,
        )
        return DecisionListPage.from_wire(data)
