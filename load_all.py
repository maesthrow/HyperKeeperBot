import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import TOKEN

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)

storage = MemoryStorage()

bot = Bot(token=str(TOKEN), parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="🚀️ начало работы"),
        BotCommand(command="/storage", description="🗂️ открыть хранилище"),
        BotCommand(command="/settings", description="⚙️ настройки"),
        #BotCommand(command="/profile", description="👤 мой профиль"),
        #BotCommand(command="/help", description="справка"),
    ]
    await bot.set_my_commands(bot_commands)

