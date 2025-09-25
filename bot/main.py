import asyncio
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timezone

from aiohttp import web
from database import add_user
from plugins import (
    auto_delete,
    auto_filter,
    broadcast,
    files_delete,
    force_subscribe,
    manual_filters,
    settings,
)
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# -----------------------------
# Logging Setup
# -----------------------------
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("Ultimate-Auto-Filter")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# -----------------------------
# System time check
# -----------------------------
MAX_OFFSET = 5  # seconds

def check_system_time():
    now_utc = datetime.now(timezone.utc).timestamp()
    system_time = time.time()
    offset = abs(system_time - now_utc)
    if offset > MAX_OFFSET:
        logger.error(f"System time is off by {offset:.2f}s. Telegram requires correct time.")
        sys.exit(1)
    logger.info(f"System time synchronized ({offset:.2f}s offset).")

check_system_time()

# -----------------------------
# Environment variables
# -----------------------------
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()]

if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables!")
    sys.exit(1)

# -----------------------------
# Initialize Pyrogram bot (in-memory session)
# -----------------------------
app = Client(
    ":memory:",  # in-memory session, no .session file
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# -----------------------------
# Handlers
# -----------------------------
@app.on_message(filters.private)
async def pm_block(client, message):
    await message.reply("❌ You can only search files in groups. @KR_Picture")


@app.on_callback_query()
async def cb_handler(client, callback_query):
    await settings.callback(client, callback_query)
    await auto_filter.callback(client, callback_query)


@app.on_message(filters.group)
async def group_handler(client, message):
    add_user(message.from_user.id)
    await force_subscribe.check(client, message)
    await auto_filter.handle(client, message)
    await manual_filters.handle(client, message)


@app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast_handler(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /broadcast <message>")
        return
    text = message.text.split(None, 1)[1]
    await broadcast.broadcast(client, message, text)


@app.on_message(filters.command("health") & filters.user(ADMIN_IDS))
async def health_check(client, message):
    await message.reply("✅ Bot is running fine.")


# -----------------------------
# HTTP health check
# -----------------------------
async def health(request):
    return web.Response(text="✅ Bot is running")


async def run_health_server():
    web_app = web.Application()
    web_app.router.add_get("/", health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logger.info("Health server running on port 8080")
    while True:
        await asyncio.sleep(3600)


# -----------------------------
# Run bot
# -----------------------------
if __name__ == "__main__":
    while True:
        try:
            logger.info("Starting bot...")
            loop = asyncio.get_event_loop()
            loop.create_task(run_health_server())
            app.run()
        except FloodWait as e:
            wait_time = int(getattr(e, "value", 15))
            logger.warning(f"FloodWait: Sleeping for {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            traceback.print_exc()
            logger.info("Restarting in 15 seconds...")
            time.sleep(15)
