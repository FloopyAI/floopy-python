# Changelog

All notable changes to `floopy-sdk` (Python) are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

Releases are produced by `release-please` from Conventional Commits.

## [0.4.0](https://github.com/FloopyAI/floopy-python/compare/floopy-sdk-v0.3.0...floopy-sdk-v0.4.0) (2026-07-06)


### Added

* add max_completion_tokens to routing explain ([991bc13](https://github.com/FloopyAI/floopy-python/commit/991bc138b02a83bec4f61c73ea08f8e4bd13ce83))
* add max_completion_tokens to routing explain ([7e781b0](https://github.com/FloopyAI/floopy-python/commit/7e781b0f48bc5374277cf7ddcc8ee82b10dd200f))

## [0.3.0](https://github.com/FloopyAI/floopy-python/compare/floopy-sdk-v0.2.0...floopy-sdk-v0.3.0) (2026-05-19)


### Added

* add Batch and Files API resources ([8478f19](https://github.com/FloopyAI/floopy-python/commit/8478f196ca20f6ad5259e4b5a00f4ce2b568f7f0))
* Batch and Files API ([77f0bb3](https://github.com/FloopyAI/floopy-python/commit/77f0bb34156613c99be3aa3a97b3d8a1e32b5d19))

## [0.2.0](https://github.com/FloopyAI/floopy-python/compare/floopy-sdk-v0.1.0...floopy-sdk-v0.2.0) (2026-05-17)


### Added

* publish python sdk ([84d451f](https://github.com/FloopyAI/floopy-python/commit/84d451f912d4c4b415f3346dde488967ea28b261))

## [Unreleased]

### Added

- Initial Python SDK: `Floopy` (sync) and `AsyncFloopy` (async) clients
  wrapping the official `openai` SDK via lazy delegation, typed
  `FloopyOptions` mapped to `Floopy-*` headers, an internal httpx
  transport with retries/backoff/timeouts, and the `FloopyError`
  hierarchy. `chat.completions`, `embeddings`, and `models` reach the
  gateway 1:1 with the upstream `openai` SDK.
- Floopy-only resources: `feedback`, `decisions` (+ paginated iterators),
  `experiments` (with auto `X-Floopy-Confirm`), `constraints`, `export`
  (JSONL streaming with optional trailer capture), `evaluations`,
  `routing.explain`, and `sessions.get`. Each resource is fully typed
  end-to-end (sync + async) and raises the appropriate `FloopyError`
  subclass.
