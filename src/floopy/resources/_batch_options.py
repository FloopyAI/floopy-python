"""Shared helper for the Batch / Files surface: fold the ``provider``
convenience argument into the ``floopy-provider`` request header."""

from __future__ import annotations

from .._constants import FLOOPY_HEADERS
from ..types.shared import RequestOptions


def with_provider(
    provider: str | None,
    request_options: RequestOptions | None,
) -> RequestOptions | None:
    """Return ``request_options`` with ``floopy-provider`` set when
    ``provider`` is given. A batch carries no model up front, so the
    upstream cannot be inferred — it must be selected explicitly."""
    if provider is None:
        return request_options
    base = request_options or RequestOptions()
    headers = {**base.headers, FLOOPY_HEADERS.PROVIDER: provider}
    return RequestOptions(headers=headers, timeout=base.timeout, options=base.options)
