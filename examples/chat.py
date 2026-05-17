"""Basic chat completion — a drop-in for the `openai` SDK."""

import os

from floopy import CacheOptions, Floopy, FloopyOptions

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
    options=FloopyOptions(
        cache=CacheOptions(enabled=True, bucket_max_size=3),
        llm_security_enabled=True,
    ),
) as floopy:
    response = floopy.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": "Say hi from Floopy in one sentence."},
        ],
    )
    print(response.choices[0].message.content)
