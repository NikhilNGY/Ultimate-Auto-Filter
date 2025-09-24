from pyrogram import Client, filters
from pyrogram.raw import functions
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_IDS
from database import add_user
import asyncio

# Import plugins lazily and defensively
from plugins import auto_filter, auto_delete, files_delete, manual_filters, force_subscribe, broadcast, settings

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("API_ID, API_HASH and BOT_TOKEN must be set in environment")

app = Client("autofilter_bot", api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN)

# -----------------------------
# Private messages
# -----------------------------
@app.on_message(filters.private)
async def pm_block(client, message):
    await message.reply("❌ You can only search files in groups.")


# -----------------------------
# Callback queries
# -----------------------------
@app.on_callback_query()
async def cb_handler(client, callback_query):
    await settings.callback(client, callback_query)
    await auto_filter.callback(client, callback_query)


# -----------------------------
# Group messages
# -----------------------------
@app.on_message(filters.group)
async def group_handler(client, message):
    add_user(message.from_user.id)
    await force_subscribe.check(client, message)
    await auto_filter.handle(client, message)
    await manual_filters.handle(client, message)


# -----------------------------
# Admin broadcast
# -----------------------------
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast_handler(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /broadcast <message>")
        return
    text = message.text.split(None, 1)[1]
    await broadcast.broadcast(client, message, text)


# -----------------------------
# Sync time before starting
# -----------------------------
async def start_bot():
    await app.start()
    try:
        # Sync Telegram server time
        # Use raw GetConfig to warm up connection (no response needed here)
        await app.invoke(functions.help.GetConfig())
    except Exception as e:
        print("Time sync failed:", e)
    print("Bot started successfully")
    await app.idle()  # Keep bot running


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    asyncio.run(start_bot())
