import os
from typing import List


# Environment / runtime configuration
# It's safer to keep defaults empty so deployments must explicitly set credentials.
def _csv_to_int_list(s: str) -> List[int]:
	if not s:
		return []
	return [int(x) for x in s.split(",") if x.strip()]

API_ID = int(os.environ.get("API_ID")) if os.environ.get("API_ID") else None
API_HASH = os.environ.get("API_HASH") or None
BOT_TOKEN = os.environ.get("BOT_TOKEN") or None
MONGO_DB_URI = os.environ.get("MONGO_DB_URI") or None

# Channel / group defaults (allow comma separated list of ids or usernames)
INDEX_CHANNEL_ID = int(os.environ.get("INDEX_CHANNEL_ID")) if os.environ.get("INDEX_CHANNEL_ID") else None
FORCE_SUB_CHANNELS = [s for s in os.environ.get("FORCE_SUB_CHANNELS", "-1002055023335").split(",") if s]

SHORTLINK_URL = os.environ.get("SHORTLINK_URL") or None
SHORTLINK_API = os.environ.get("SHORTLINK_API") or None

ADMIN_IDS = _csv_to_int_list(os.environ.get("ADMIN_IDS", "2098589219,2068233407"))

# default auto delete time in seconds
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", "3000"))
