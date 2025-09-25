from database import get_settings, update_setting
from pyrogram import types


async def show_settings(client, message):
    settings = get_settings(message.chat.id)
    keyboard = [
        [
            types.InlineKeyboardButton(
                f"Force Sub: {'ON' if settings['force_sub'] else 'OFF'}",
                callback_data="toggle_force_sub",
            )
        ],
        [
            types.InlineKeyboardButton(
                f"Auto Delete: {'ON' if settings['auto_delete'] else 'OFF'}",
                callback_data="toggle_auto_delete",
            )
        ],
        [
            types.InlineKeyboardButton(
                f"Shortlink: {'ON' if settings['shortlink'] else 'OFF'}",
                callback_data="toggle_shortlink",
            )
        ],
        [
            types.InlineKeyboardButton(
                f"Manual Filter: {'ON' if settings['manual_filter'] else 'OFF'}",
                callback_data="toggle_manual_filter",
            )
        ],
    ]
    await message.reply(
        "⚙️ Settings:", reply_markup=types.InlineKeyboardMarkup(keyboard)
    )


async def callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    key_map = {
        "toggle_force_sub": "force_sub",
        "toggle_auto_delete": "auto_delete",
        "toggle_shortlink": "shortlink",
        "toggle_manual_filter": "manual_filter",
    }
    key = key_map.get(data)
    if key:
        s = get_settings(chat_id)
        current = s.get(key, False)
        update_setting(chat_id, key, not current)
        await callback_query.answer(
            f"{key.replace('_',' ').title()} set to {'ON' if not current else 'OFF'}",
            show_alert=False,
        )
        try:
            await callback_query.message.delete()
        except:
            pass
        await show_settings(client, callback_query.message)
