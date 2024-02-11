import asyncio

from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommand

from load_all import bot


async def on_shutdown(dp):
    await bot.close()


async def on_startup(dp):
    #await setup_bot()
    await setup_bot_commands()
    pass

async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, on_shutdown=on_shutdown, on_startup=on_startup)


if __name__ == '__main__':
    from handlers.handlers_ import dp
    import handlers.handlers_file
    import handlers.handlers_item_edit_inline_buttons
    import handlers.handlers_item_add_mode
    import handlers.handlers_inline_query
    asyncio.run(main())


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="🚀️ начало работы"),
        BotCommand(command="/storage", description="🗂️ открыть хранилище"),
        BotCommand(command="/settings", description="⚙️ настройки"),
        #BotCommand(command="/profile", description="👤 мой профиль"),
        #BotCommand(command="/help", description="справка"),
    ]
    await bot.set_my_commands(bot_commands)