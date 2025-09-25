from database import users_col


async def broadcast(client, message, text):
    if message.from_user.id not in client.ADMIN_IDS:
        await message.reply("❌ You are not authorized!")
        return
    users = list(users_col.find({}))
    success = 0
    failed = 0
    for u in users:
        try:
            await client.send_message(u["_id"], text)
            success += 1
        except:
            failed += 1
    await message.reply(
        f"Broadcast completed!\n✅ Success: {success}\n❌ Failed: {failed}"
    )  # Broadcast plugin
