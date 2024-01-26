import asyncio
import copy

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton

from handlers import states
from load_all import bot, dp
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import item_edit_buttons
from utils.utils_items_reader import get_item

edit_question = f"\n\n\n<b><i>Что будете редактировать?</i></b>"

add_none_title_item_button = InlineKeyboardButton(text="🪧 Пустой заголовок", callback_data=f"add_none_title_item")
cancel_edit_item_button = InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_edit_item")

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "edit_item")
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

@router.callback_query(F.data == "edit_item_title")
async def edit_item_title_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)
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

    data = await get_data(user_id)
    data['edit_item_messages'] = (edit_item_message_1, edit_item_message_2, edit_item_message_3)
    await set_data(user_id, data)

    await state.set_state(states.Item.EditTitle)
    await call.answer()


