import asyncio


async def wait_timeout(seconds):
    await asyncio.sleep(seconds)