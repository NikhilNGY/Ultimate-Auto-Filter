import os
from typing import List, Optional


# -----------------------------
# Helpers
# -----------------------------
def _csv_to_int_list(s: str) -> List[int]:
    """Convert comma-separated string to list of ints, safely."""
    if not s:
        return []
    return [int(x) for x in s.split(",") if x.strip()]


# -----------------------------
# Required credentials
# -----------------------------
API_ID: Optional[int] = (
    int(os.environ.get("API_ID")) if os.environ.get("API_ID") else None
)
API_HASH: Optional[str] = os.environ.get("API_HASH") or None
BOT_TOKEN: Optional[str] = os.environ.get("BOT_TOKEN") or None
MONGO_DB_URI: Optional[str] = os.environ.get("MONGO_DB_URI") or None

# -----------------------------
# Channels / groups
# -----------------------------
INDEX_CHANNEL_ID: Optional[int] = (
    int(os.environ.get("INDEX_CHANNEL_ID"))
    if os.environ.get("INDEX_CHANNEL_ID")
    else None
)

FORCE_SUB_CHANNELS: list[str] = [
    s for s in os.environ.get("FORCE_SUB_CHANNELS", "sandalwood_kannada_moviesz").split(",") if s
]

# -----------------------------
# Shortlink config
# -----------------------------
SHORTLINK_URL: Optional[str] = os.environ.get("SHORTLINK_URL") or None
SHORTLINK_API: Optional[str] = os.environ.get("SHORTLINK_API") or None

# -----------------------------
# Admins
# -----------------------------
ADMIN_IDS: list[int] = _csv_to_int_list(
    os.environ.get("ADMIN_IDS", "2098589219,2068233407")
)

# -----------------------------
# Default auto delete time
# -----------------------------
AUTO_DELETE_TIME: int = int(os.environ.get("AUTO_DELETE_TIME", "3000"))
