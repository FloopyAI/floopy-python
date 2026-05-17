"""Read + full-replace org constraints."""

import os

from floopy import Floopy, OrgConstraints

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    current = floopy.constraints.get()
    print("current:", current)

    # PUT replaces all fields — leave a field as None to clear it.
    updated = floopy.constraints.put(
        OrgConstraints(cost_limit_monthly_usd=250, max_requests_per_minute=120)
    )
    print("updated:", updated)
