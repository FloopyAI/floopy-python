from __future__ import annotations

from floopy._constants import FLOOPY_HEADERS
from floopy._headers import build_floopy_headers, merge_headers
from floopy.types.shared import CacheOptions, FloopyOptions


def test_returns_empty_when_no_options() -> None:
    assert build_floopy_headers(None) == {}
    assert build_floopy_headers(FloopyOptions()) == {}


def test_maps_cache_options() -> None:
    headers = build_floopy_headers(
        FloopyOptions(cache=CacheOptions(enabled=True, bucket_max_size=5))
    )
    assert headers[FLOOPY_HEADERS.CACHE_ENABLED] == "true"
    assert headers[FLOOPY_HEADERS.CACHE_BUCKET_MAX_SIZE] == "5"


def test_maps_prompt_id_and_version() -> None:
    headers = build_floopy_headers(FloopyOptions(prompt_id="abc-123", prompt_version="2"))
    assert headers[FLOOPY_HEADERS.PROMPT_ID] == "abc-123"
    assert headers[FLOOPY_HEADERS.PROMPT_VERSION] == "2"


def test_maps_llm_security_enabled() -> None:
    assert (
        build_floopy_headers(FloopyOptions(llm_security_enabled=True))[
            FLOOPY_HEADERS.LLM_SECURITY_ENABLED
        ]
        == "true"
    )
    assert (
        build_floopy_headers(FloopyOptions(llm_security_enabled=False))[
            FLOOPY_HEADERS.LLM_SECURITY_ENABLED
        ]
        == "false"
    )


def test_does_not_emit_unset_cache_fields() -> None:
    assert build_floopy_headers(FloopyOptions(cache=CacheOptions())) == {}


def test_merge_later_layers_win() -> None:
    assert merge_headers({"a": "1", "b": "1"}, {"b": "2", "c": "3"}) == {
        "a": "1",
        "b": "2",
        "c": "3",
    }


def test_merge_ignores_none_layers() -> None:
    assert merge_headers({"a": "1"}, None, {"b": "2"}) == {"a": "1", "b": "2"}
