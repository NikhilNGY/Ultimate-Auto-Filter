from urllib.parse import quote_plus

import requests  # synchronous HTTP requests

from config import SHORTLINK_API


def shorten(url: str) -> str:
    if not SHORTLINK_API or not url:
        return url
    try:
        safe_url = quote_plus(url)
        api_url = f"https://api.shortlinkservice.com/create?api={SHORTLINK_API}&url={safe_url}"
        r = requests.get(api_url, timeout=10)
        if r.status_code != 200:
            return url
        data = r.json()
        return data.get("short_url", url)
    except Exception:
        return url
