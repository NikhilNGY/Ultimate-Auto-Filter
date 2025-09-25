import asyncio

from database import get_settings


async def schedule_delete(client, message):
    settings = get_settings(message.chat.id)
    if not settings["auto_delete"]:
        return
    delete_time = settings.get("auto_delete_time", 3000)  # default 5 min
    await asyncio.sleep(delete_time)
    try:
        await message.delete()
    except:
        pass# Auto delete plugin
