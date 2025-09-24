from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS
from database import add_user
from plugins import auto_filter, auto_delete, files_delete, manual_filters, force_subscribe, broadcast, settings

app = Client("autofilter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.private)
async def pm_block(client, message):
    await message.reply("❌ You can only search files in groups.")

@app.on_message(filters.group)
async def group_handler(client, message):
    add_user(message.from_user.id)
    # Here we can add plugins hooks (auto filter, manual filters, etc.)
    await auto_filter.handle(client, message)
    await manual_filters.handle(client, message)
    await force_subscribe.check(client, message)

app.run()# Main bot starter
