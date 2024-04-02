from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import MessageBoxCallback
from load_all import bot


class MessageBox:
    ok_button = InlineKeyboardButton(text='Ok', callback_data=MessageBoxCallback(result='ok').pack())
    ok_builder = InlineKeyboardBuilder()
    ok_builder.add(ok_button)

    @staticmethod
    async def show(
            user_id: int,
            message_text: str,
            parse_mode: ParseMode = ParseMode.HTML,
            edit_message_id: str | int = None,
    ):
        if not edit_message_id:
            await bot.send_message(
                chat_id=user_id,
                text=message_text,
                parse_mode=parse_mode,
                reply_markup=MessageBox.ok_builder.as_markup()
            )
        else:
            try:
                await bot.edit_message_text(
                    chat_id=user_id,
                    text=message_text,
                    message_id=edit_message_id,
                    parse_mode=parse_mode,
                    reply_markup=MessageBox.ok_builder.as_markup()
                )
            except:
                try:
                    await bot.delete_message(user_id, message_id=edit_message_id)
                except:
                    pass
                await bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    parse_mode=parse_mode,
                    reply_markup=MessageBox.ok_builder.as_markup()
                )
