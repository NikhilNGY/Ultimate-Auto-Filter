import aiohttp
from config import SHORTLINK_API

async def shorten(url):
    if not SHORTLINK_API:
        return url
    api_url = f"https://api.shortlinkservice.com/create?api={SHORTLINK_API}&url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as r:
            data = await r.json()
            return data.get("short_url", url)# Shortlink plugin
