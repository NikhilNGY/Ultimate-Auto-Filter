from database import files_col, delete_file

async def delete_seeded_file(client, file_id):
    f = files_col.find_one({"file_id": file_id})
    if f:
        try:
            await client.delete_messages(f["chat_id"], f["message_id"])
        except:
            pass
        delete_file(file_id)

async def delete_all_files(client):
    all_files = list(files_col.find({}))
    for f in all_files:
        try:
            await client.delete_messages(f["chat_id"], f["message_id"])
        except:
            pass
    files_col.delete_many({})# Files delete plugin
