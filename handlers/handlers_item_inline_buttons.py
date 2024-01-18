import asyncio

from aiogram.types import CallbackQuery, User, Chat, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.handlers_folder import show_folders
from load_all import dp, bot
from models.item_model import Item
from utils.utils_button_manager import show_item_files_button, hide_item_files_button
from utils.utils_data import get_current_folder_id
from utils.utils_item_show_files import show_item_files
from utils.utils_items_db import util_delete_item

delete_question = f"\n\n<b><i>Хотите удалить запись?</i></b>"


@dp.callback_query_handler(text="close_item")
async def close_item_handler(call: CallbackQuery):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(user=tg_user, chat=chat)
    item_files_messages = data.get('item_files_messages', [])
    accept_add_item_message = data.get('accept_add_item_message', None)
    tasks = [
        close_files(item_files_messages),
        bot.delete_message(call.message.chat.id, call.message.message_id)
    ]
    if accept_add_item_message:
        tasks.insert(0, bot.delete_message(chat_id=chat.id, message_id=accept_add_item_message.message_id))

    await asyncio.gather(*tasks)

    data['item_files_messages'] = []
    data['accept_add_item_message'] = None
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)
    await call.answer()


async def get_data():
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(user=tg_user, chat=chat)
    return data


async def update_inline_markup_data(inline_markup: InlineKeyboardMarkup):
    data = await get_data()
    data['current_inline_markup'] = inline_markup
    tg_user = User.get_current()
    chat = Chat.get_current()
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)


async def get_current_inline_markup():
    data = await get_data()
    inline_markup = data.get('current_inline_markup', None)
    return inline_markup


@dp.callback_query_handler(text="show_item_files")
async def show_item_files_handler(call: CallbackQuery):
    inline_markup = call.message.reply_markup
    inline_markup.inline_keyboard[-1][-1] = hide_item_files_button

    data = await get_data()
    item = data.get('current_item', None)
    if item:
        await asyncio.gather(
            show_item_files(item),
            call.message.edit_reply_markup(inline_markup)
        )
    await update_inline_markup_data(inline_markup)
    await call.answer()


@dp.callback_query_handler(text="hide_item_files")
async def hide_item_files_handler(call: CallbackQuery):
    inline_markup = call.message.reply_markup
    inline_markup.inline_keyboard[-1][-1] = show_item_files_button

    data = await get_data()
    item_files_messages = data.get('item_files_messages', [])

    await asyncio.gather(
        close_files(item_files_messages),
        call.message.edit_reply_markup(inline_markup)
    )
    await update_inline_markup_data(inline_markup)
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


@dp.callback_query_handler(text="delete_item")
async def delete_item_handler(call: CallbackQuery):
    item_inlines = [
        [
            InlineKeyboardButton("☑️ Да", callback_data="delete_item_yes"),
            InlineKeyboardButton("✖️ Нет", callback_data="delete_item_no"),
        ]
    ]
    inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=item_inlines)

    await call.answer()
    await call.message.edit_text(text=f"{call.message.text}{delete_question}", reply_markup=inline_markup)


@dp.callback_query_handler(text="delete_item_no")
async def cancel_delete_item_handler(call: CallbackQuery):
    data = await get_data()
    item: Item = data.get('current_item', None)
    if item:
        inline_markup = await get_current_inline_markup()
        await call.message.edit_text(text=item.get_body(), reply_markup=inline_markup)
    await call.answer()


@dp.callback_query_handler(text="delete_item_yes")
async def accept_delete_item_handler(call: CallbackQuery):
    data = await get_data()
    item_id = data.get('item_id', None)
    if item_id:
        result = await util_delete_item(item_id)
        if result:
            await asyncio.gather(
                close_item_handler(call),
                refresh_folder()
            )
        await call.answer(text=f"Не получилось удалить запись.'", show_alert=True)
    else:
        await call.answer(text=f"Что то пошло не так при удалении записи.", show_alert=True)


async def refresh_folder():
    folder_id = await get_current_folder_id()
    await show_folders(current_folder_id=folder_id, need_to_resend=False)