from pyrogram import types, filters
from database import files_col, get_settings
from plugins import shortlink

async def handle(client, message):
    settings = get_settings(message.chat.id)
    if message.text and settings["manual_filter"]:
        query = message.text.lower()
        # Fetch files from DB with fuzzy search
        all_files = list(files_col.find({"file_name": {"$regex": query}}))
        if not all_files:
            await message.reply("No files found.")
            return
        # Pagination logic (10 buttons per page)
        keyboard = []
        for f in all_files[:10]:
            link = f"t.me/c/{f['chat_id']}/{f['message_id']}"
            if settings["shortlink"]:
                link = await shortlink.shorten(link)
            keyboard.append([types.InlineKeyboardButton(f['file_name'], url=link)])
        reply_markup = types.InlineKeyboardMarkup(keyboard)
        await message.reply("Search Results:", reply_markup=reply_markup)
