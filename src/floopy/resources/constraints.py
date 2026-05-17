from __future__ import annotations

from .._constants import ENDPOINTS
from .._http import AsyncHTTP, SyncHTTP
from ..types.constraints import OrgConstraints
from ..types.shared import RequestOptions


class ConstraintsResource:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, *, request_options: RequestOptions | None = None) -> OrgConstraints:
        data, _ = self._http.request("GET", ENDPOINTS.CONSTRAINTS, request_options=request_options)
        return OrgConstraints.from_wire(data)

    def put(
        self,
        constraints: OrgConstraints,
        *,
        request_options: RequestOptions | None = None,
    ) -> OrgConstraints:
        """Full-replace upsert. Any field left at ``None`` is reset to null
        server-side (matches the gateway's PUT semantics)."""
        data, _ = self._http.request(
            "PUT",
            ENDPOINTS.CONSTRAINTS,
            body=constraints.to_wire(),
            request_options=request_options,
        )
        return OrgConstraints.from_wire(data)


class AsyncConstraintsResource:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, *, request_options: RequestOptions | None = None) -> OrgConstraints:
        data, _ = await self._http.request(
            "GET", ENDPOINTS.CONSTRAINTS, request_options=request_options
        )
        return OrgConstraints.from_wire(data)

    async def put(
        self,
        constraints: OrgConstraints,
        *,
        request_options: RequestOptions | None = None,
    ) -> OrgConstraints:
        data, _ = await self._http.request(
            "PUT",
            ENDPOINTS.CONSTRAINTS,
            body=constraints.to_wire(),
            request_options=request_options,
        )
        return OrgConstraints.from_wire(data)
