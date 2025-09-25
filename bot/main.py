import sys
import time
from datetime import datetime, timezone

from config import ADMIN_IDS, API_HASH, API_ID, BOT_TOKEN
from database import add_user
from plugins import (auto_delete, auto_filter, broadcast, files_delete,
                     force_subscribe, manual_filters, settings)
from pyrogram import Client, filters
from pyrogram.raw import functions

# -----------------------------
# System time check
# -----------------------------
MAX_OFFSET = 5  # seconds

def check_system_time():
    """
    Exits if system time is off by more than MAX_OFFSET seconds.
    """
    now_utc = datetime.now(timezone.utc).timestamp()
    system_time = time.time()
    offset = abs(system_time - now_utc)
    if offset > MAX_OFFSET:
        print(
            f"[ERROR] System time is off by {offset:.2f}s. Telegram requires correct time."
        )
        print("Please sync your server time (NTP/chrony) before starting the bot.")
        sys.exit(1)
    else:
        print(f"[INFO] System time synchronized ({offset:.2f}s offset).")

check_system_time()

# -----------------------------
# Verify environment
# -----------------------------
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise RuntimeError("API_ID, API_HASH and BOT_TOKEN must be set in environment")

# -----------------------------
# Initialize bot
# -----------------------------
app = Client(
    "autofilter_bot", api_id=int(API_ID), api_hash=API_HASH, bot_token=BOT_TOKEN
)

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
# Run bot
# -----------------------------
if __name__ == "__main__":
    print("Instance created. Starting bot...")
    # Pyrogram v2: run() blocks and keeps bot alive
    app.run()
