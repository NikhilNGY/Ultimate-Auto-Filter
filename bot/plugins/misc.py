import re
from typing import Any, List

import aiohttp
from config import SHORTLINK_API
from pyrogram import types


# -----------------------------
# Pagination helper for inline buttons
# -----------------------------
def paginate_buttons(
    items: List[Any], page: int = 0, items_per_page: int = 10, prefix: str = "file_"
):
    """
    Create inline keyboard buttons with pagination.

    :param items: List of items to paginate (dicts with 'file_name' and 'link')
    :param page: Current page index (0-based)
    :param items_per_page: Number of buttons per page
    :param prefix: Prefix for callback_data
    :return: InlineKeyboardMarkup
    """
    start = page * items_per_page
    end = start + items_per_page
    keyboard = []

    for item in items[start:end]:
        # item must contain 'file_name' and 'link'
        keyboard.append(
            [types.InlineKeyboardButton(item["file_name"], url=item["link"])]
        )

    # Navigation buttons
    nav_buttons = []
    if start > 0:
        nav_buttons.append(
            types.InlineKeyboardButton("⬅️ Back", callback_data=f"{prefix}prev_{page-1}")
        )
    if end < len(items):
        nav_buttons.append(
            types.InlineKeyboardButton("Next ➡️", callback_data=f"{prefix}next_{page+1}")
        )

    if nav_buttons:
        keyboard.append(nav_buttons)

    return types.InlineKeyboardMarkup(keyboard)


# -----------------------------
# Shortlink helper
# -----------------------------
async def shorten_link(url: str) -> str:
    """
    Shorten a URL using SHORTLINK_API (if configured).
    Returns original URL if API not configured or fails.
    """
    if not SHORTLINK_API:
        return url

    api_url = f"https://api.shortlinkservice.com/create?api={SHORTLINK_API}&url={url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                data = await resp.json()
                return data.get("short_url", url)
    except:
        return url


# -----------------------------
# Fuzzy search helper
# -----------------------------
def fuzzy_search(
    query: str, items: List[dict], key: str = "file_name", limit: int = 50
) -> List[dict]:
    """
    Return list of items matching the query using simple case-insensitive substring search.
    Can be replaced by advanced fuzzy matching if needed.
    """
    query = query.lower()
    results = []
    for item in items:
        if query in item.get(key, "").lower():
            results.append(item)
        if len(results) >= limit:
            break
    return results


# -----------------------------
# Clean text helper
# -----------------------------
def clean_text(text: str) -> str:
    """
    Remove extra spaces, special characters, and newlines from text.
    """
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


# -----------------------------
# Convert to int safely
# -----------------------------
def safe_int(val, default=0):
    try:
        return int(val)
    except:
        return default  # Misc utilities
