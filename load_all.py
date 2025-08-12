import logging
import os
import re
import sys

from dotenv import load_dotenv
from aiogram import Bot, Router
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from wit import Wit

env_file = os.getenv("ENV_FILE", ".env")
print(f"[debug] env_file={env_file}")

load_dotenv(dotenv_path=env_file)

BOT_TOKEN = os.getenv('BOT_TOKEN')

print(f"[debug] BOT_TOKEN repr={repr(BOT_TOKEN)} len={0 if BOT_TOKEN is None else len(BOT_TOKEN)}", file=sys.stderr)
if not BOT_TOKEN or not re.fullmatch(r"\d+:[A-Za-z0-9_-]{20,}", BOT_TOKEN.strip()):
    raise RuntimeError("BOT_TOKEN missing/malformed")

WIT_AI_TOKEN = os.getenv('WIT_AI_TOKEN')

GIGA_AUTH_DATA = os.getenv("GIGA_AUTH_DATA")

from langchain_community.chat_models import GigaChat
# Авторизация в сервисе GigaChat
giga_chat = GigaChat(credentials=GIGA_AUTH_DATA, verify_ssl_certs=False)


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)

storage = MemoryStorage()

bot = Bot(token=str(BOT_TOKEN), parse_mode="HTML")
dp = Dispatcher(bot=bot, storage=storage)
wit_client = Wit(WIT_AI_TOKEN)

# async def setup_aiogram_dialogs():
#     dp.include_router(dialog_folder_control_main_menu)
#     setup_dialogs(dp)


async def setup_bot():
    pass
    # session = await bot.get_session()
    #
    # # Получение текущего коннектора
    # connector = session.connector
    #
    # # Установка таймаута в 30 секунд
    # connector._session_timeout = aiohttp.ClientTimeout(total=30)
