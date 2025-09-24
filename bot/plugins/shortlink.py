import aiohttp
from config import SHORTLINK_API
from urllib.parse import quote_plus


async def shorten(url: str) -> str:
    if not SHORTLINK_API or not url:
        return url
    try:
        safe_url = quote_plus(url)
        api_url = f"https://api.shortlinkservice.com/create?api={SHORTLINK_API}&url={safe_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as r:
                if r.status != 200:
                    return url
                data = await r.json()
                return data.get("short_url", url)
    except Exception:
        return url

# Shortlink plugin
