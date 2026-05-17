# `floopy-sdk` (Python)

> Official Floopy AI Gateway SDK for Python. **Drop-in replacement for the
> [`openai`](https://pypi.org/project/openai/) SDK** with Floopy's cache,
> audit, experiments, routing, and security on top.

[![PyPI](https://img.shields.io/pypi/v/floopy-sdk?color=22c55e&label=pypi)](https://pypi.org/project/floopy-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/floopy-sdk)](https://pypi.org/project/floopy-sdk/)
[![docs](https://img.shields.io/badge/docs-floopy.ai-blue)](https://floopy.ai/docs/guides/sdks/floopy-sdk-python)

## Why

`floopy-sdk` wraps the official `openai` package and points it at the
Floopy gateway, so:

- **Zero migration cost** for `chat.completions` and `embeddings` — same
  types, same methods.
- **Security updates** to the OpenAI SDK reach you on `pip install -U`
  without forks or parity drift.
- **Floopy-only features** (audit, experiments, constraints, decision
  export, feedback, routing dry-run, sessions) get **first-class typed
  methods** instead of raw `requests`/`httpx` calls.

## Install

```sh
pip install floopy-sdk          # or: uv add floopy-sdk
```

Requires Python `>= 3.10`.

## Quick start

```python
from floopy import Floopy

with Floopy(api_key="fl_...") as floopy:
    response = floopy.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello from Floopy!"}],
    )
    print(response.choices[0].message.content)
```

Async is symmetric:

```python
import asyncio
from floopy import AsyncFloopy

async def main() -> None:
    async with AsyncFloopy(api_key="fl_...") as floopy:
        r = await floopy.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello!"}],
        )
        print(r.choices[0].message.content)

asyncio.run(main())
```

### Migrating from `openai`

```diff
- from openai import OpenAI
- client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
+ from floopy import Floopy
+ client = Floopy(api_key=os.environ["FLOOPY_API_KEY"])

  r = client.chat.completions.create(
      model="gpt-4o",
      messages=[{"role": "user", "content": "..."}],
  )
```

`client.chat`, `client.embeddings`, and `client.models` return the
underlying `openai` resources, so types and runtime behaviour are
identical. Full guide:
<https://floopy.ai/docs/guides/sdks/floopy-sdk-python#migrating-from-openai>.

## Floopy options (cache, prompt versioning, security firewall)

```python
from floopy import Floopy, FloopyOptions, CacheOptions

floopy = Floopy(
    api_key="fl_...",
    options=FloopyOptions(
        cache=CacheOptions(enabled=True, bucket_max_size=3),
        prompt_id="cd4249d5-44d5-46c8-8961-9eb3861e1f7e",
        prompt_version="1",
        llm_security_enabled=True,
    ),
)
```

These map to `Floopy-*` headers forwarded to **every** request (both
OpenAI-compat calls and Floopy-only ones). Per-call overrides are
available via `request_options=RequestOptions(...)` on every resource.

| Option | Header | Purpose |
| --- | --- | --- |
| `cache.enabled` | `Floopy-Cache-Enabled` | Toggle exact + semantic cache |
| `cache.bucket_max_size` | `Floopy-Cache-Bucket-Max-Size` | Max entries per semantic bucket |
| `prompt_id` | `Floopy-Prompt-Id` | Stored prompt to resolve |
| `prompt_version` | `Floopy-Prompt-Version` | Pinned version for `prompt_id` |
| `llm_security_enabled` | `floopy-llm-security-enabled` | LLM firewall pre-check |

## Floopy-only resources

Each resource maps to a public `/v1/*` gateway endpoint and is typed
end-to-end. Errors are `FloopyError` subclasses (see below). Every method
exists on both `Floopy` (sync) and `AsyncFloopy` (`await` it).

### `feedback`

```python
r = floopy.chat.completions.create(...)
floopy.feedback.submit(score=9, useful=True, session_id=r.id)
```

### `decisions`

```python
decision = floopy.decisions.get(request_id)
page = floopy.decisions.list(from_=since, limit=50)

for d in floopy.decisions.iterate(from_=since):   # one at a time
    ...
for p in floopy.decisions.pages(from_=since):     # page at a time
    ...
```

### `experiments`

```python
exp = floopy.experiments.create(
    name="cost-vs-quality",
    variant_a_routing_rule_id=rule_a,
    variant_b_routing_rule_id=rule_b,
)
results = floopy.experiments.results(exp.id)
floopy.experiments.rollback(exp.id)
```

`create` and `rollback` automatically include the
`X-Floopy-Confirm: experiments` header the gateway requires (SEC-009).

### `constraints`

```python
from floopy import OrgConstraints

current = floopy.constraints.get()
floopy.constraints.put(OrgConstraints(cost_limit_monthly_usd=100))
```

`put` is full-replace: fields left as `None` are reset.

### `export`

```python
for row in floopy.export.decisions(from_=start, to=end):
    ...  # streamed JSONL, parsed and typed

# to also read the trailer (truncation reasons, totals):
stream = floopy.export.decisions_with_trailer(from_=start, to=end)
for row in stream:
    ...
print(stream.trailer)   # populated after iteration completes
```

### `evaluations`

```python
run = floopy.evaluations.create(dataset_id=ds_id, model="gpt-4o")
status = floopy.evaluations.get(run.id)
results = floopy.evaluations.results(run.id, limit=100)
floopy.evaluations.cancel(run.id)
```

### `routing.explain`

```python
explain = floopy.routing.explain(model="gpt-4o", messages=messages)
print(explain.would_select, explain.firewall_decision)
```

Pro plan only. `would_select` is `None` if the firewall blocks the request.

### `sessions`

```python
session = floopy.sessions.get(session_id)
# session.messages is a drop-in for a follow-up chat completion
floopy.chat.completions.create(model="gpt-4o", messages=session.messages)
```

## Streaming

`chat.completions` streaming is delegated to `openai` and yields chunks
exactly as the upstream SDK does. `export.decisions` yields typed
`ExportedDecisionRow` objects over the gateway's JSONL stream.

## Error handling

Every Floopy-only call raises a `FloopyError` subclass:

```python
from floopy import FloopyRateLimitError, FloopyPlanError

try:
    for row in floopy.export.decisions(from_=start, to=end):
        ...
except FloopyRateLimitError as err:
    time.sleep(err.retry_after_seconds or 1)
except FloopyPlanError as err:
    print(f"Upgrade plan: feature {err.feature} not in current plan")
```

Errors from `chat.completions` / `embeddings` are emitted by the OpenAI
SDK (`openai.APIError` and friends).

## Security

- The API key is only ever sent in the `Authorization` header and is
  masked in `repr()` of internal objects; the SDK never logs request or
  response bodies.
- TLS certificate verification is on by default (httpx).
- Releases are published to PyPI via **Trusted Publishing (OIDC)** with
  **PEP 740 attestations** — no long-lived tokens, and consumers can
  verify the artifact was built by this repo's release workflow.

## Self-hosting / custom base URL

```python
floopy = Floopy(api_key="fl_...", base_url="https://gateway.internal.acme.com/v1")
```

## Links

- Full SDK guide: <https://floopy.ai/docs/guides/sdks/floopy-sdk-python>
  ([Português](https://floopy.ai/pt/docs/guides/sdks/floopy-sdk-python))
- API reference: <https://floopy.ai/docs/guides/api-reference>
- Changelog: [`CHANGELOG.md`](./CHANGELOG.md)

## License

Apache-2.0 © Floopy
