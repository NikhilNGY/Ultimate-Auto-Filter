import os

API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "mongodb://localhost:27017")
INDEX_CHANNEL_ID = int(os.environ.get("INDEX_CHANNEL_ID", "-1001234567890"))
FORCE_SUB_CHANNEL = os.environ.get("FORCE_SUB_CHANNEL", "@YourChannel")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "")
ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS","123456789").split()))
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "300"))  # seconds# Config file template
