from pyrogram import types

from config import FORCE_SUB_CHANNELS
from database import get_settings


async def check(client, message):
    settings = get_settings(message.chat.id)
    if not settings["force_sub"]:
        return

    # Check all channels
    not_joined = []
    for ch in FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch, message.from_user.id)
            if getattr(member, "status", None) in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)

    if not_joined:
        buttons = []
        for ch in not_joined:
            # ch may be an id like -100123 or a username like @channel
            if str(ch).startswith("-100") or str(ch).lstrip("-").isdigit():
                # no username available, just show the id as text link to t.me/c/ if possible
                url = None
                try:
                    url = f"https://t.me/{str(ch)}"
                except:
                    url = None
            else:
                u = ch.lstrip("@")
                url = f"https://t.me/{u}"
            if url:
                buttons.append([types.InlineKeyboardButton("Join Channel", url=url)])
            else:
                buttons.append(
                    [types.InlineKeyboardButton("Channel", callback_data="noop")]
                )
        await message.reply(
            "❌ You must join these channels to use the bot:",
            reply_markup=types.InlineKeyboardMarkup(buttons),
        )
        await message.delete()
        return  # Force subscribe plugin
