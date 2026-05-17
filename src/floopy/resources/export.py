from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, Query, SyncHTTP
from ..types.export import ExportedDecisionRow, ExportFormat, ExportTrailer
from ..types.shared import RequestOptions


def _query(from_: str, to: str, fmt: ExportFormat | None) -> Query:
    query: Query = {"from": from_, "to": to}
    if fmt is not None:
        query["format"] = fmt
    return query


def _is_trailer(line: dict[str, Any]) -> bool:
    return line.get("trailer") is True


class DecisionExportStream:
    """Iterable over the JSONL export. The terminal trailer record is *not*
    yielded as a row; after iteration completes, :attr:`trailer` holds the
    summary (truncation reason / totals), or ``None`` if none was sent."""

    def __init__(self, lines: Iterator[dict[str, Any]]) -> None:
        self._lines = lines
        self.trailer: ExportTrailer | None = None

    def __iter__(self) -> Iterator[ExportedDecisionRow]:
        for line in self._lines:
            if _is_trailer(line):
                self.trailer = ExportTrailer.from_wire(line)
                continue
            yield ExportedDecisionRow.from_wire(line)


class AsyncDecisionExportStream:
    def __init__(self, lines: AsyncIterator[dict[str, Any]]) -> None:
        self._lines = lines
        self.trailer: ExportTrailer | None = None

    async def __aiter__(self) -> AsyncIterator[ExportedDecisionRow]:
        async for line in self._lines:
            if _is_trailer(line):
                self.trailer = ExportTrailer.from_wire(line)
                continue
            yield ExportedDecisionRow.from_wire(line)


class ExportResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def decisions(
        self,
        *,
        from_: str,
        to: str,
        format: ExportFormat | None = None,
        request_options: RequestOptions | None = None,
    ) -> Iterator[ExportedDecisionRow]:
        """Iterate decision rows from the JSONL export. The trailer record is
        skipped — use :meth:`decisions_with_trailer` to capture it."""
        for line in self._http.stream_lines(
            "GET",
            ENDPOINTS.EXPORT_DECISIONS,
            query=_query(from_, to, format),
            request_options=request_options,
        ):
            if _is_trailer(line):
                continue
            yield ExportedDecisionRow.from_wire(line)

    def decisions_with_trailer(
        self,
        *,
        from_: str,
        to: str,
        format: ExportFormat | None = None,
        request_options: RequestOptions | None = None,
    ) -> DecisionExportStream:
        lines = self._http.stream_lines(
            "GET",
            ENDPOINTS.EXPORT_DECISIONS,
            query=_query(from_, to, format),
            request_options=request_options,
        )
        return DecisionExportStream(lines)


class AsyncExportResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def decisions(
        self,
        *,
        from_: str,
        to: str,
        format: ExportFormat | None = None,
        request_options: RequestOptions | None = None,
    ) -> AsyncIterator[ExportedDecisionRow]:
        async for line in self._http.stream_lines(
            "GET",
            ENDPOINTS.EXPORT_DECISIONS,
            query=_query(from_, to, format),
            request_options=request_options,
        ):
            if _is_trailer(line):
                continue
            yield ExportedDecisionRow.from_wire(line)

    def decisions_with_trailer(
        self,
        *,
        from_: str,
        to: str,
        format: ExportFormat | None = None,
        request_options: RequestOptions | None = None,
    ) -> AsyncDecisionExportStream:
        lines = self._http.stream_lines(
            "GET",
            ENDPOINTS.EXPORT_DECISIONS,
            query=_query(from_, to, format),
            request_options=request_options,
        )
        return AsyncDecisionExportStream(lines)
