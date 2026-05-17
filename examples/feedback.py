"""Submit NPS-style feedback for a completion."""

import os

from floopy import Floopy

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    r = floopy.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Reply with: 'hello world'"}],
    )
    result = floopy.feedback.submit(score=9, useful=True, session_id=r.id)
    print("feedback duplicate?", result.duplicate)
