from typing import Any, Dict, List, Optional

from config import MONGO_DB_URI

# -------------------------------
# MongoDB / in-memory setup
# -------------------------------
try:
    if MONGO_DB_URI:
        from pymongo import MongoClient

        _client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=3000)
        _client.server_info()  # force connection
        _db = _client["autofilter_bot"]
        files_col = _db["files"]
        users_col = _db["users"]
        filters_col = _db["filters"]
        settings_col = _db["settings"]
        broadcast_col = _db["broadcast"]
        logger_source = "MongoDB"
    else:
        raise Exception("MONGO_DB_URI not configured")
except Exception:
    # Fallback in-memory
    files_col = {}
    users_col = set()
    filters_col = {}
    settings_col = {}
    broadcast_col = {}
    logger_source = "In-memory storage"

print(f"[INFO] Database initialized using {logger_source}")


# -------------------------------
# Helper functions
# -------------------------------
def _ensure_id(val: Any) -> Optional[int]:
    try:
        return int(val)
    except Exception:
        return None


# -------------------------------
# User functions
# -------------------------------
def add_user(user_id: Any):
    uid = _ensure_id(user_id)
    if uid is None:
        return
    try:
        if hasattr(users_col, "insert_one"):
            if not users_col.find_one({"_id": uid}):
                users_col.insert_one({"_id": uid})
        else:
            users_col.add(uid)
    except Exception:
        pass


# -------------------------------
# File functions
# -------------------------------
def add_file(file_id: Any, file_name: str, message_id: Any, chat_id: Any):
    if file_id is None:
        return
    try:
        if hasattr(files_col, "insert_one"):
            if not files_col.find_one({"file_id": file_id}):
                files_col.insert_one({
                    "file_id": file_id,
                    "file_name": file_name,
                    "message_id": message_id,
                    "chat_id": chat_id,
                })
        else:
            files_col[str(file_id)] = {
                "file_id": file_id,
                "file_name": file_name,
                "message_id": message_id,
                "chat_id": chat_id,
            }
    except Exception:
        pass


def delete_file(file_id: Any):
    try:
        if hasattr(files_col, "delete_one"):
            files_col.delete_one({"file_id": file_id})
        else:
            files_col.pop(str(file_id), None)
    except Exception:
        pass


def delete_all_files():
    try:
        if hasattr(files_col, "delete_many"):
            files_col.delete_many({})
        else:
            files_col.clear()
    except Exception:
        pass


# -------------------------------
# Filter functions
# -------------------------------
def add_filter(keyword: str, reply: str):
    if not keyword:
        return
    k = keyword.lower()
    try:
        if hasattr(filters_col, "insert_one"):
            filters_col.insert_one({"keyword": k, "reply": reply})
        else:
            filters_col[k] = {"keyword": k, "reply": reply}
    except Exception:
        pass


def delete_filter(keyword: str):
    if not keyword:
        return
    k = keyword.lower()
    try:
        if hasattr(filters_col, "delete_one"):
            filters_col.delete_one({"keyword": k})
        else:
            filters_col.pop(k, None)
    except Exception:
        pass


def get_filters() -> List[Dict[str, Any]]:
    try:
        if hasattr(filters_col, "find"):
            return list(filters_col.find({}))
        else:
            return list(filters_col.values())
    except Exception:
        return []


def delete_all_filters():
    try:
        if hasattr(filters_col, "delete_many"):
            filters_col.delete_many({})
        else:
            filters_col.clear()
    except Exception:
        pass


# -------------------------------
# Settings functions
# -------------------------------
def get_settings(chat_id: Any) -> Dict[str, Any]:
    cid = _ensure_id(chat_id) or str(chat_id)
    default = {
        "_id": cid,
        "force_sub": True,
        "auto_delete": True,
        "shortlink": True,
        "manual_filter": True,
        "auto_delete_time": None,
    }
    try:
        if hasattr(settings_col, "find_one"):
            s = settings_col.find_one({"_id": cid})
            if not s:
                settings_col.insert_one(default)
                return default
            return s
        else:
            return settings_col.get(str(cid), default)
    except Exception:
        return default


def update_setting(chat_id: Any, key: str, value: Any):
    cid = _ensure_id(chat_id) or str(chat_id)
    try:
        if hasattr(settings_col, "update_one"):
            settings_col.update_one({"_id": cid}, {"$set": {key: value}}, upsert=True)
        else:
            s = settings_col.get(str(cid), {"_id": cid})
            s[key] = value
            settings_col[str(cid)] = s
    except Exception:
        pass
