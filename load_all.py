import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from wit import Wit

from config import BOT_TOKEN, WIT_AI_TOKEN

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)

storage = MemoryStorage()

bot = Bot(token=str(BOT_TOKEN), parse_mode="HTML")
dp = Dispatcher(bot=bot, storage=storage)

wit_client = Wit(WIT_AI_TOKEN)

# current_item = {}

async def setup_bot():
    pass
    # session = await bot.get_session()
    #
    # # Получение текущего коннектора
    # connector = session.connector
    #
    # # Установка таймаута в 30 секунд
    # connector._session_timeout = aiohttp.ClientTimeout(total=30)







