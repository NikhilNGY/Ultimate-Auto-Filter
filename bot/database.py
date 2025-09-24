from pymongo import MongoClient
from config import MONGO_DB_URI

client = MongoClient(MONGO_DB_URI)
db = client["autofilter_bot"]

# Collections
files_col = db["files"]
users_col = db["users"]
filters_col = db["filters"]
settings_col = db["settings"]
broadcast_col = db["broadcast"]

# Helper functions
def add_user(user_id):
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id})

def add_file(file_id, file_name, message_id, chat_id):
    if not files_col.find_one({"file_id": file_id}):
        files_col.insert_one({"file_id": file_id, "file_name": file_name, "message_id": message_id, "chat_id": chat_id})

def delete_file(file_id):
    files_col.delete_one({"file_id": file_id})

def delete_all_files():
    files_col.delete_many({})

def add_filter(keyword, reply):
    filters_col.insert_one({"keyword": keyword.lower(), "reply": reply})

def delete_filter(keyword):
    filters_col.delete_one({"keyword": keyword.lower()})

def get_filters():
    return list(filters_col.find({}))

def delete_all_filters():
    filters_col.delete_many({})

def get_settings(chat_id):
    s = settings_col.find_one({"_id": chat_id})
    if not s:
        settings_col.insert_one({"_id": chat_id, "force_sub": True, "auto_delete": True, "shortlink": True, "manual_filter": True})
        return get_settings(chat_id)
    return s

def update_setting(chat_id, key, value):
    settings_col.update_one({"_id": chat_id}, {"$set": {key: value}})# MongoDB handler
