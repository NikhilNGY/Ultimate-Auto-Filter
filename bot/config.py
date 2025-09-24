import os

API_ID = int(os.environ.get("API_ID", "2468192"))
API_HASH = os.environ.get("API_HASH", "4906b3f8f198ec0e24edb2c197677678")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "")
INDEX_CHANNEL_ID = int(os.environ.get("INDEX_CHANNEL_ID", "-1001892397342"))

FORCE_SUB_CHANNELS = os.environ.get("FORCE_SUB_CHANNELS", "-1002055023335").split(",")

SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "vplink.in")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "ab42d0b5656f5c774f800dacb6739342b6f094aa")

ADMIN_IDS = list(map(int, os.environ.get("ADMIN_IDS", "2098589219,2068233407").split(",")))

AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "3000"))
