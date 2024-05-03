import asyncio

from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommand
from aiogram_dialog import setup_dialogs

from dialogs.accesses.windows import dialog_accesses
from dialogs.folder_control.windows import dialog_folder_control
from dialogs.item_control.windows import dialog_item_control
from dialogs.main_menu.windows import dialog_main_menu
from dialogs.settings.windows import dialog_settings_menu
from dialogs.user_support.windows import dialog_user_support
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
    import handlers_pack.handlers
    import handlers_pack.handlers_any_message
    import handlers_pack.handlers_search_end
    import handlers_pack.handlers_item_entities
    import handlers_pack.handlers_item_edit_inline_buttons
    import handlers_pack.handlers_item_add_mode
    import handlers_pack.handlers_inline_query_share
    import handlers_pack.handlers_inline_query_search
    import handlers_pack.handlers_inline_query_access
    import handlers_pack.handlers_item_text_pages
    import handlers_pack.handlers_edit_item_files
    import handlers_pack.handlers_pin_folder_control
    import handlers_pack.handlers_access
    import handlers_pack.handlers_user_support

    dp.include_router(dialog_main_menu)
    dp.include_router(dialog_folder_control)
    dp.include_router(dialog_accesses)
    dp.include_router(dialog_settings_menu)
    dp.include_router(dialog_item_control)
    dp.include_router(dialog_user_support)
    setup_dialogs(dp)



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