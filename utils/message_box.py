from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import MessageBoxCallback
from load_all import bot


class MessageBox:
    ok_button = InlineKeyboardButton(text='OK', callback_data=MessageBoxCallback(result='ok').pack())
    ok_builder = InlineKeyboardBuilder()
    ok_builder.add(ok_button)

    @staticmethod
    async def show(user_id, message_text: str, parse_mode: ParseMode = ParseMode.HTML):
        await bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode=parse_mode,
            reply_markup=MessageBox.ok_builder.as_markup()
        )
