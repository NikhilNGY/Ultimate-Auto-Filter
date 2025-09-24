from pyrogram import types
from database import get_settings
from config import FORCE_SUB_CHANNELS

async def check(client, message):
    settings = get_settings(message.chat.id)
    if not settings["force_sub"]:
        return

    # Check all channels
    not_joined = []
    for ch in FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch, message.from_user.id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not_joined:
        buttons = [[types.InlineKeyboardButton("Join Channel", url=f"https://t.me/{ch[1:]})")] for ch in not_joined]
        await message.reply(
            "❌ You must join these channels to use the bot:",
            reply_markup=types.InlineKeyboardMarkup(buttons)
        )
        await message.delete()
        return# Force subscribe plugin
