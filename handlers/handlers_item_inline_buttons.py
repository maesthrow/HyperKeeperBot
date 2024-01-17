import asyncio

from aiogram.types import CallbackQuery, User, Chat

from load_all import dp, bot
from utils.utils_button_manager import show_item_files_button


@dp.callback_query_handler(text="close_item")
async def close_item_handler(call: CallbackQuery):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(user=tg_user, chat=chat)
    item_files_messages = data.get('item_files_messages', [])

    await asyncio.gather(
        close_files(item_files_messages),
        bot.delete_message(call.message.chat.id, call.message.message_id)
    )

    data['item_files_messages'] = []
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)
    await call.answer()


@dp.callback_query_handler(text="hide_item_files")
async def hide_item_files_handler(call: CallbackQuery):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(user=tg_user, chat=chat)
    item_files_messages = data.get('item_files_messages', [])

    inline_markup = call.message.reply_markup
    #inline_markup.inline_keyboard[-1][-1] = show_item_files_button
    inline_markup.inline_keyboard[-1][-1].text = "Показать файлы »"
    inline_markup.inline_keyboard[-1][-1].callback_data = "show_item_files"

    await asyncio.gather(
        close_files(item_files_messages),
        call.message.edit_reply_markup(inline_markup)
    )

    await call.answer()


async def close_files(item_files_messages: list):
    if len(item_files_messages) > 0:
        delete_tasks = [delete_files_message(message) for message in item_files_messages]
        await asyncio.gather(*delete_tasks)


async def delete_files_message(message):
    if isinstance(message, list):
        delete_tasks = [delete_message(msg.chat.id, msg.message_id) for msg in message]
        await asyncio.gather(*delete_tasks)
    else:
        await bot.delete_message(message.chat.id, message.message_id)


async def delete_message(chat_id, message_id):
    await bot.delete_message(chat_id, message_id)