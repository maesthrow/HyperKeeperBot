import asyncio

import aiogram
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from button_manager import check_button_exists
from load_all import dp, bot
from enums import Environment


async def get_environment():
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    keyboard: ReplyKeyboardMarkup = data.get('current_keyboard', None)
    environment: Environment = Environment.FOLDERS
    for tmp_environment in Environment:
        if check_button_exists(keyboard, tmp_environment.value):
            environment = tmp_environment
    return environment


def get_inline_markup_for_accept_cancel(text_accept, text_cancel, callback_data):
    inline_markup = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text=text_accept, callback_data=f"{callback_data}_accept"),
            ],
            [
                InlineKeyboardButton(text=text_cancel, callback_data=f"{callback_data}_cancel")
            ],
        ]
    )
    return inline_markup
