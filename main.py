import asyncio
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from aiohttp import web
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

from database import (add_file, add_user, delete_file, get_settings,
                      update_setting)
from plugins import (auto_delete, auto_filter, broadcast, files_delete,
                     force_subscribe, manual_filters, settings)

# -----------------------------
# Logging Setup
# -----------------------------
os.makedirs("logs", exist_ok=True)
log_file = "logs/bot.log"

logger = logging.getLogger("UltimateAutoFilter")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# -----------------------------
# System Time Check
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
# Environment Variables
# -----------------------------
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = os.environ.get("ADMIN_IDS", "")

if not API_ID or not API_HASH or not BOT_TOKEN:
    logger.error("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables!")
    sys.exit(1)

try:
    ADMIN_IDS = [int(x) for x in ADMIN_IDS.split(",") if x.strip()]
except Exception:
    ADMIN_IDS = []

# -----------------------------
# Ensure session folder exists
# -----------------------------
SESSION_DIR = "session"
os.makedirs(SESSION_DIR, exist_ok=True)
try:
    os.chmod(SESSION_DIR, 0o777)
except Exception as e:
    logger.warning(f"Could not change permissions for {SESSION_DIR}: {e}")

SESSION_FILE = f"{SESSION_DIR}/Ultimate-Auto-Filter"

# -----------------------------
# Initialize Bot (Persistent Session)
# -----------------------------
app = Client(
    SESSION_FILE,
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# -----------------------------
# Private Message Handler
# -----------------------------
@app.on_message(filters.private)
async def pm_block(client, message):
    await message.reply("❌ You can only search files in groups.")

# -----------------------------
# Callback Query Handler
# -----------------------------
@app.on_callback_query()
async def cb_handler(client, callback_query):
    await settings.callback(client, callback_query)
    await auto_filter.callback(client, callback_query)

# -----------------------------
# Group Message Handler
# -----------------------------
@app.on_message(filters.group)
async def group_handler(client, message):
    add_user(message.from_user.id)
    await force_subscribe.check(client, message)
    await auto_filter.handle(client, message)
    await manual_filters.handle(client, message)
    if get_settings(message.chat.id).get("auto_delete"):
        await auto_delete.handle(client, message)

# -----------------------------
# Admin Broadcast Handler
# -----------------------------
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_IDS))
async def broadcast_handler(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /broadcast <message>")
        return
    text = message.text.split(None, 1)[1]
    await broadcast.broadcast(client, message, text)

# -----------------------------
# Health Check Handler
# -----------------------------
@app.on_message(filters.command("health") & filters.user(ADMIN_IDS))
async def health_check(client, message):
    await message.reply("✅ Bot is running fine.")

# -----------------------------
# HTTP Health Server
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
# Run Bot with Auto-Restart
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
