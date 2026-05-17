"""Routing dry-run (Pro plan)."""

import os

from floopy import Floopy

with Floopy(
    api_key=os.environ["FLOOPY_API_KEY"],
    base_url=os.environ.get("FLOOPY_BASE_URL"),
) as floopy:
    explanation = floopy.routing.explain(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "What's the cheapest way to summarize a 10k-token doc?",
            }
        ],
    )
    print("would route to:", explanation.would_select)
    print("firewall:", explanation.firewall_decision)
    print("rule id:", explanation.routing_rule_id)
    print("reasoning:", explanation.reasoning)
