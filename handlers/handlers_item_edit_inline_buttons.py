import asyncio
import copy
from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, User, InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, Chat

from firebase.firebase_item_reader import get_item
from handlers import states
from handlers.handlers_edit_item_title import on_edit_item
from handlers.handlers_item import show_item
from handlers.handlers_item_inline_buttons import close_item_handler
from load_all import dp, bot
from models.item_model import Item
from utils.utils_button_manager import item_edit_buttons
from utils.utils_items_db import util_edit_item

edit_question = f"\n\n<b><i>Что будете редактировать?</i></b>"

add_none_title_item_button = InlineKeyboardButton("🪧 Пустой заголовок", callback_data=f"add_none_title_item")
cancel_edit_item_button = InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_edit_item")

@dp.callback_query_handler(text="edit_item")
async def edit_item_handler(call: CallbackQuery):
    item_inlines = copy.deepcopy(item_edit_buttons)
    inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=item_inlines)

    await call.answer()
    await call.message.edit_text(text=f"{call.message.text}{edit_question}", reply_markup=inline_markup)


# async def on_edit_item_state_handler(edit_text, state: FSMContext):
#     tg_user = User.get_current()
#     chat = Chat.get_current(())
#     data = await dp.storage.get_data(chat=chat, user=tg_user)
#     item_id = data.get('item_id')
#
#     await on_edit_item(edit_text, state)
#     await show_item(item_id)

@dp.callback_query_handler(text="edit_item_title")
async def edit_item_title_handler(call: CallbackQuery):
    tg_user = User.get_current()
    data = await dp.storage.get_data(chat=call.message.chat, user=tg_user)
    item_id = data.get('item_id')

    item: Item = await get_item(item_id)
    if item.title and item.title != "":
        item_title = f"<b>{item.title}</b>"
    else:
        item_title = "[пусто]"

    edit_item_message_1 = await bot.send_message(call.message.chat.id, f"Текущий заголовок:",
                                                 reply_markup=ReplyKeyboardRemove())
    edit_item_message_2 = await bot.send_message(call.message.chat.id, f"{item_title}")

    await asyncio.sleep(0.4)

    buttons = [[add_none_title_item_button, cancel_edit_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)

    edit_item_message_3 = await bot.send_message(call.message.chat.id,
                                                 f"Придумайте новый заголовок:",
                                                 reply_markup=inline_markup)

    data = await dp.storage.get_data(user=tg_user, chat=call.message.chat)
    data['edit_item_messages'] = (edit_item_message_1, edit_item_message_2, edit_item_message_3)
    await dp.storage.update_data(user=tg_user, chat=call.message.chat, data=data)

    await states.Item.EditTitle.set()


