"""Async client: chat completion + session restore."""

import asyncio
import os

from floopy import AsyncFloopy


async def main() -> None:
    async with AsyncFloopy(
        api_key=os.environ["FLOOPY_API_KEY"],
        base_url=os.environ.get("FLOOPY_BASE_URL"),
    ) as floopy:
        r = await floopy.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hi from async Floopy."}],
        )
        print(r.choices[0].message.content)

        # Decisions stream concurrently with anything else you await.
        async for decision in floopy.decisions.iterate(limit=5):
            print(decision.request_id, decision.status)
            break


if __name__ == "__main__":
    asyncio.run(main())
