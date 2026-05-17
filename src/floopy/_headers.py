"""Translate :class:`FloopyOptions` into wire headers and merge header
layers with a deterministic precedence. Mirrors ``src/headers.ts``."""

from __future__ import annotations

from ._constants import FLOOPY_HEADERS
from .types.shared import FloopyOptions


def build_floopy_headers(options: FloopyOptions | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if options is None:
        return headers

    if options.cache is not None:
        if options.cache.enabled is not None:
            headers[FLOOPY_HEADERS.CACHE_ENABLED] = _bool(options.cache.enabled)
        if options.cache.bucket_max_size is not None:
            headers[FLOOPY_HEADERS.CACHE_BUCKET_MAX_SIZE] = str(options.cache.bucket_max_size)
    if options.prompt_id is not None:
        headers[FLOOPY_HEADERS.PROMPT_ID] = options.prompt_id
    if options.prompt_version is not None:
        headers[FLOOPY_HEADERS.PROMPT_VERSION] = options.prompt_version
    if options.llm_security_enabled is not None:
        headers[FLOOPY_HEADERS.LLM_SECURITY_ENABLED] = _bool(options.llm_security_enabled)
    return headers


def merge_headers(*layers: dict[str, str] | None) -> dict[str, str]:
    """Later layers win. ``None`` layers are skipped."""
    merged: dict[str, str] = {}
    for layer in layers:
        if layer is None:
            continue
        merged.update(layer)
    return merged


def _bool(value: bool) -> str:
    # Match JS String(boolean): lowercase "true"/"false".
    return "true" if value else "false"
