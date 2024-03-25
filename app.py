import asyncio

from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommand

from load_all import bot, dp
from mongo_db.mongo import close_client


async def on_shutdown():
    await close_client()
    await bot.close()


async def on_startup():
    #await setup_bot()
    await setup_bot_commands()


async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, on_shutdown=on_shutdown, on_startup=on_startup)


if __name__ == '__main__':
    import handlers.handlers_
    import handlers.handlers_search_end
    import handlers.handlers_item_entities
    import handlers.handlers_item_edit_inline_buttons
    import handlers.handlers_item_add_mode
    import handlers.handlers_inline_query_share
    import handlers.handlers_inline_query_search
    import handlers.handlers_inline_query_access
    import handlers.handlers_item_text_pages
    import handlers.handlers_edit_item_files
    import handlers.handlers_folder_control
    import handlers.handlers_access
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот был остановлен вручную')


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="🚀️ начало работы"),
        BotCommand(command="/storage", description="🗂️ открыть хранилище"),
        BotCommand(command="/access", description="🔐 доступы от других пользователей"),
        BotCommand(command="/search", description="🔍️ live-поиск"),
        BotCommand(command="/profile", description="👤 мой профиль"),
        BotCommand(command="/settings", description="⚙️ настройки"),
        BotCommand(command="/help", description="❔ помощь"),
    ]
    await bot.set_my_commands(bot_commands)

# start - 🚀️ начало работы
# storage - 🗂️ открыть хранилище
# access - 🔐 доступы от других пользователей
# search - 🔍️ live-поиск
# profile - 👤 мой профиль
# settings - ⚙️ настройки
# help - ❔ помощь