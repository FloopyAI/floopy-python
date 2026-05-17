"""Stream the JSONL decision export and read its trailer."""

import os
from datetime import datetime, timedelta, timezone

from floopy import Floopy

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    now = datetime.now(timezone.utc)
    from_ = (now - timedelta(days=7)).isoformat()
    to = now.isoformat()

    stream = floopy.export.decisions_with_trailer(from_=from_, to=to)

    n = 0
    for row in stream:
        n += 1
        if n <= 3:
            print(row.request_id, row.model, row.cost_micro_usd)

    print(f"exported {n} rows")
    if stream.trailer is not None:
        print("trailer:", stream.trailer)
