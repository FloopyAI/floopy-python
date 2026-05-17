"""Single + batch embeddings."""

import os

from floopy import Floopy

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    single = floopy.embeddings.create(
        model="text-embedding-3-small",
        input="Floopy routes any OpenAI-compatible call.",
    )
    batch = floopy.embeddings.create(
        model="text-embedding-3-small",
        input=["batch item 1", "batch item 2", "batch item 3"],
    )
    print("single dims:", len(single.data[0].embedding))
    print("batch count:", len(batch.data))
