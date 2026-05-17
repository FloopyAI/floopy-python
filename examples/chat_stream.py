"""Streaming chat completion (delegated to the openai SDK)."""

import os
import sys

from floopy import Floopy

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    stream = floopy.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Stream a haiku about gateways."}],
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            sys.stdout.write(delta)
    sys.stdout.write("\n")
