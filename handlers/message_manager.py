import aiogram
from aiogram import Router
from aiogram.types import InlineKeyboardMarkup

from load_all import bot, dp
from utils.utils_button_manager import ok_info_button

router = Router()
dp.include_router(router)


async def send_ok_info_message(user_id, info_text: str):
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[ok_info_button]])
    await bot.send_message(chat_id=user_id,
                           text=info_text,
                           reply_markup=inline_markup)


@router.callback_query(lambda callback_query: callback_query.data == 'ok_info')
async def ok_info_handler(callback_query: aiogram.types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.answer()