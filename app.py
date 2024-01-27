import asyncio

from aiogram.methods import DeleteWebhook

from load_all import bot, setup_bot_commands


async def on_shutdown(dp):
    await bot.close()


async def on_startup(dp):
    #await setup_bot()
    await setup_bot_commands()

async def main():
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, on_shutdown=on_shutdown, on_startup=on_startup, polling_timeout=5)


if __name__ == '__main__':
    from handlers.handlers_ import dp
    asyncio.run(main())



