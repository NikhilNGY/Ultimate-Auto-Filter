import asyncio
import urllib.parse
from datetime import datetime, timedelta

from database import files_col, get_settings
from plugins import shortlink
from pyrogram import types

ITEMS_PER_PAGE = 10  # Buttons per page
CACHE_EXPIRATION = 300  # seconds (5 minutes)
BUTTONS_TIMEOUT = 60  # seconds after which inline buttons are removed

# In-memory cache: chat_id -> last search results
search_cache = {}

# Cleanup expired cache periodically
async def cache_cleaner():
    while True:
        now = datetime.utcnow()
        expired = [cid for cid, val in search_cache.items() if val["expires_at"] < now]
        for cid in expired:
            del search_cache[cid]
        await asyncio.sleep(60)

# -----------------------------
# Handle group message search
# -----------------------------
async def handle(client, message):
    settings = await get_settings(message.chat.id)
    if not settings.get("manual_filter", False) or not message.text:
        return

    query = message.text.strip().lower()
    files_list = list(files_col.find({"file_name": {"$regex": query}}))
    if not files_list:
        return  # Silent if nothing found

    search_cache[message.chat.id] = {
        "query": query,
        "files": files_list,
        "expires_at": datetime.utcnow() + timedelta(seconds=CACHE_EXPIRATION)
    }

    await send_page(client, message, message.chat.id, page=0)

# -----------------------------
# Send a page of results from cache
# -----------------------------
async def send_page(client, message, chat_id, page: int):
    cached = search_cache.get(chat_id)
    if not cached or cached["expires_at"] < datetime.utcnow():
        search_cache.pop(chat_id, None)
        return

    files_list = cached["files"]
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_files = files_list[start:end]
    if not page_files:
        return

    settings = await get_settings(chat_id)
    buttons = []
    for f in page_files:
        link = f"t.me/c/{f['chat_id']}/{f['message_id']}"
        if settings.get("shortlink", False):
            link = await shortlink.shorten(link)
        buttons.append([types.InlineKeyboardButton(f["file_name"], url=link)])

    total_pages = (len(files_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    encoded_query = urllib.parse.quote(cached["query"])

    # Navigation buttons with current page highlighted
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⏮️ First", callback_data=f"auto_first_0_{chat_id}_{encoded_query}"))
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"auto_prev_{page-1}_{chat_id}_{encoded_query}"))
    # Current page disabled
    nav_buttons.append(types.InlineKeyboardButton(f"Page {page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"auto_next_{page+1}_{chat_id}_{encoded_query}"))
        nav_buttons.append(types.InlineKeyboardButton("⏭️ Last", callback_data=f"auto_last_{total_pages-1}_{chat_id}_{encoded_query}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = types.InlineKeyboardMarkup(buttons)
    sent_msg = await message.reply(f"🔎 Search Results (Page {page+1} of {total_pages}):", reply_markup=reply_markup)
    asyncio.create_task(remove_buttons_only(sent_msg, BUTTONS_TIMEOUT))

# Remove buttons only (keep message)
async def remove_buttons_only(message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.edit_reply_markup(None)
    except:
        pass

# Handle pagination callback queries
async def callback(client, callback_query):
    data = callback_query.data
    if data == "noop":
        await callback_query.answer()
        return

    if not data.startswith("auto_"):
        return

    parts = data.split("_", 4)
    action, page, chat_id, encoded_query = parts[1], int(parts[2]), int(parts[3]), parts[4]
    query = urllib.parse.unquote(encoded_query)

    settings = await get_settings(chat_id)
    if not settings.get("manual_filter", False):
        await callback_query.answer("Manual filters disabled.", show_alert=True)
        return

    cached = search_cache.get(chat_id)
    if not cached or cached["query"] != query or cached["expires_at"] < datetime.utcnow():
        search_cache.pop(chat_id, None)
        try:
            await callback_query.message.edit_reply_markup(None)
        except:
            pass
        await callback_query.answer("Search expired. Please search again.", show_alert=True)
        return

    await callback_query.message.edit_reply_markup(None)
    await send_page(client, callback_query.message, chat_id, page)
