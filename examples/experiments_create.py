"""Create (and optionally roll back) a routing experiment."""

import os
import time

from floopy import Floopy

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    # Replace with real routing rule ids in your org.
    variant_a = os.environ.get("FLOOPY_VARIANT_A_RULE_ID", "rule_a_uuid")
    variant_b = os.environ.get("FLOOPY_VARIANT_B_RULE_ID", "rule_b_uuid")

    exp = floopy.experiments.create(
        name=f"cost-vs-quality-{int(time.time())}",
        description="Compare gpt-4o-mini vs gpt-4o on free-tier traffic",
        variant_a_routing_rule_id=variant_a,
        variant_b_routing_rule_id=variant_b,
        split_percentage=50,
    )
    print("created:", exp.id, exp.status)

    # To roll back:
    # rolled_back = floopy.experiments.rollback(exp.id)
    # print("rolled back:", rolled_back.status)

    # To inspect results once enough samples accumulate:
    # print(floopy.experiments.results(exp.id))
