from load_all import bot


async def get_bot_link():
    bot_info = await bot.get_me()
    username = bot_info.username
    bot_link = f"https://t.me/{username}"
    return bot_link


async def get_bot_name():
    bot_info = await bot.get_me()
    name = bot_info.first_name
    return name