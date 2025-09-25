import requests
from config import REVIEWBOT_URL
from pyrogram import Client, filters

# Warn if REVIEWBOT_URL is still the placeholder
if REVIEWBOT_URL == "https://example.com":
    print("⚠️ REVIEWBOT_URL is set to placeholder. Replace it with the real Reviewbot URL for /fixcode to work.")


@Client.on_message(filters.command("fixcode") & filters.private)
async def fix_code(client, message):
    """
    Fix user-submitted Python code using Reviewbot.
    Usage: /fixcode <your_code>
    """
    code_text = message.text.replace("/fixcode", "").strip()
    if not code_text:
        await message.reply_text(
            "Please provide the code to fix.\nExample:\n`/fixcode print('Hello World`"
        )
        return

    # If using placeholder URL, notify and skip sending
    if REVIEWBOT_URL == "https://example.com":
        await message.reply_text(
            "⚠️ Reviewbot URL is not set. Please configure REVIEWBOT_URL in config.py"
        )
        return

    payload = {"code": code_text, "language": "python"}

    try:
        response = requests.post(f"{REVIEWBOT_URL}/analyze", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        fixed_code = result.get("fixed_code")

        if fixed_code:
            await message.reply_text(
                f"✅ Corrected code:\n```python\n{fixed_code}\n```",
                parse_mode="markdown",
            )
        else:
            await message.reply_text("⚠️ Reviewbot could not provide a fix.")

    except requests.exceptions.RequestException as e:
        await message.reply_text(f"❌ Error contacting Reviewbot:\n{e}")
    except Exception as e:
        await message.reply_text(f"❌ Unexpected error:\n{e}")
