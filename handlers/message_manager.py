import aiogram
from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, Chat
from load_all import dp, bot
from utils.utils_button_manager import ok_info_button

router = Router()


async def send_ok_info_message(info_text: str):
    chat = Chat.get_current()
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=[[ok_info_button]])
    await bot.send_message(chat_id=chat.id,
                           text=info_text,
                           reply_markup=inline_markup)


@router.callback_query(lambda callback_query: callback_query.data == 'ok_info')
async def ok_info_handler(callback_query: aiogram.types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await callback_query.answer()