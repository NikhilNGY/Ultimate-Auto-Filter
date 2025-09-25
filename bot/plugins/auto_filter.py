from database import files_col, get_settings
from plugins import misc, shortlink
from pyrogram import filters, types

ITEMS_PER_PAGE = 10  # Buttons per page

# -----------------------------
# Handle group message search
# -----------------------------
async def handle(client, message):
    settings = get_settings(message.chat.id)
    if not settings["manual_filter"]:
        return

    if not message.text:
        return

    query = message.text.lower()
    # Fetch files from DB matching the query
    all_files = list(files_col.find({"file_name": {"$regex": query}}))
    if not all_files:
        await message.reply("❌ No files found.")
        return

    # Show first page
    await send_page(client, message, all_files, page=0)


# -----------------------------
# Send a page of results
# -----------------------------
async def send_page(client, message, files_list, page: int):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    buttons = []

    for f in files_list[start:end]:
        link = f"t.me/c/{f['chat_id']}/{f['message_id']}"
        # Shortlink
        settings = get_settings(message.chat.id)
        if settings["shortlink"]:
            link = await shortlink.shorten(link)
        buttons.append([types.InlineKeyboardButton(f['file_name'], url=link)])

    # Navigation buttons
    nav_buttons = []
    if start > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"auto_prev_{page-1}_{message.chat.id}"))
    if end < len(files_list):
        nav_buttons.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"auto_next_{page+1}_{message.chat.id}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = types.InlineKeyboardMarkup(buttons)
    await message.reply("🔎 Search Results:", reply_markup=reply_markup)


# -----------------------------
# Handle pagination callback queries
# -----------------------------
async def callback(client, callback_query):
    data = callback_query.data
    if not data.startswith("auto_"):
        return

    parts = data.split("_")
    action, page, chat_id = parts[1], int(parts[2]), int(parts[3])

    # Fetch the original search results for this chat
    # (You can store last search in memory or DB; here simplified)
    settings = get_settings(chat_id)
    # For simplicity, refetch all files for manual filters
    all_files = list(files_col.find({}))

    if action == "next" or action == "prev":
        await callback_query.message.delete()
        await send_page(client, callback_query.message, all_files, page)
