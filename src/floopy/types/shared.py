"""Shared option/response types. Field names are snake_case (Python
convention); the Node SDK's camelCase fields map 1:1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class CacheOptions:
    """Maps to ``Floopy-Cache-*`` headers."""

    #: Toggle exact + semantic cache for the request.
    enabled: bool | None = None
    #: Maximum number of entries per semantic cache bucket.
    bucket_max_size: int | None = None


@dataclass(slots=True)
class FloopyOptions:
    """Gateway behaviour toggles, mapped to ``Floopy-*`` headers and
    forwarded to every request (OpenAI-compat and Floopy-only)."""

    #: Cache controls. Maps to ``Floopy-Cache-*`` headers.
    cache: CacheOptions | None = None
    #: Stored prompt id; the gateway resolves it to the active prompt content.
    prompt_id: str | None = None
    #: Pinned prompt version. Use with ``prompt_id``.
    prompt_version: str | None = None
    #: Toggle the LLM firewall (``floopy-llm-security-enabled``).
    llm_security_enabled: bool | None = None


@dataclass(slots=True)
class RequestOptions:
    """Per-call overrides, merged on top of client defaults."""

    #: Per-call headers merged on top of client defaults.
    headers: dict[str, str] = field(default_factory=dict)
    #: Per-call timeout in seconds (overrides the client default).
    timeout: float | None = None
    #: Override Floopy options for this call.
    options: FloopyOptions | None = None


@dataclass(slots=True)
class PaginatedResponse(Generic[T]):
    items: list[T]
    next_cursor: str | None
    has_more: bool
