# Changelog

All notable changes to `floopy-sdk` (Python) are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and the project adheres to [Semantic Versioning](https://semver.org/).

Releases are produced by `release-please` from Conventional Commits.

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
