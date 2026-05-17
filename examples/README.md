# `floopy-sdk` examples

Runnable snippets for every public surface of the SDK. **Not** part of the
published PyPI distribution.

## Setup

```sh
# from floopy-python/
uv pip install -e .          # installs the local floopy-sdk
cp examples/.env.example examples/.env
set -a; source examples/.env; set +a
python examples/chat.py
```

By default examples talk to `https://api.floopy.ai/v1`. To point at a local
gateway, set `FLOOPY_BASE_URL=http://localhost:8000/v1`.

## Files

| File | What it shows |
| --- | --- |
| `chat.py` | Basic chat completion (drop-in for `openai`) |
| `chat_stream.py` | Streaming response |
| `embeddings.py` | Single + batch embeddings |
| `feedback.py` | Submit NPS-style feedback |
| `decisions_list.py` | List + paginate decisions |
| `export_decisions.py` | Stream the JSONL export + trailer |
| `experiments_create.py` | Create + roll back an experiment |
| `constraints.py` | Read + upsert org constraints |
| `routing_explain.py` | Routing dry-run |
| `async_chat.py` | `AsyncFloopy`: async chat + decision iteration |
