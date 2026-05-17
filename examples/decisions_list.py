"""List + paginate audit decisions."""

import os
from datetime import datetime, timedelta, timezone

from floopy import Floopy

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    since = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    count = 0
    for decision in floopy.decisions.iterate(from_=since, limit=50):
        count += 1
        if count <= 5:
            print(
                decision.request_id,
                decision.provider,
                decision.model,
                decision.status,
            )
    print(f"total: {count}")
