from aiogram.utils import executor

from load_all import bot, setup_bot_commands, dp


async def on_shutdown(dp):
    await bot.close()
    #await bot.send_message(admin_id, "Я упал!")


async def on_startup(dp):
    #await create_db()
    await setup_bot_commands()
    #await bot.send_message(admin_id, "Я запущен!")


if __name__ == '__main__':
    #from admin_panel import dp
    from handlers.handlers_ import dp

    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)