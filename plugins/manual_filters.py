from database import (add_filter, delete_all_filters, delete_filter,
                      get_filters, get_settings)
from pyrogram import filters


async def handle(client, message):
    settings = get_settings(message.chat.id)
    if not settings["manual_filter"]:
        return

    text = message.text
    if text.startswith("/filter "):
        parts = text.split(None, 2)
        if len(parts) < 3:
            await message.reply("Usage: /filter <keyword> <reply>")
            return
        keyword, reply = parts[1], parts[2]
        add_filter(keyword, reply)
        await message.reply(f"✅ Filter added for '{keyword}'")
    elif text.startswith("/del "):
        keyword = text.split(None, 1)[1]
        delete_filter(keyword)
        await message.reply(f"✅ Filter deleted for '{keyword}'")
    elif text.startswith("/delall"):
        delete_all_filters()
        await message.reply("✅ All filters deleted")
    elif text.startswith("/filters"):
        fs = get_filters()
        if not fs:
            await message.reply("No filters added.")
            return
        msg = "Filters:\n" + "\n".join([f["keyword"] for f in fs])
        await message.reply(msg)  # Manual filters plugin
