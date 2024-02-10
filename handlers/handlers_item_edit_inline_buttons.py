import asyncio
import copy

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, Message

from handlers import states
from handlers.handlers_folder import show_folders
from handlers.handlers_item import show_item
from load_all import bot, dp
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_ import invisible_char
from utils.utils_button_manager import item_edit_buttons, create_general_reply_markup, \
    get_edit_item_title_keyboard, cancel_edit_item_button, get_edit_item_text_keyboard
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import to_markdown_text, preformat_text, full_escape_markdown, \
    markdown_without_code

edit_question = f"\n\n\n_*Что будете редактировать?*_"

#add_none_title_item_button = InlineKeyboardButton(text="🪧 Пустой заголовок", callback_data=f"add_none_title_item")
#cancel_edit_item_button = InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_edit_item")

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "edit_item")
async def edit_item_handler(call: CallbackQuery):
    item_inlines = copy.deepcopy(item_edit_buttons)
    inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=item_inlines)

    format_message_text = to_markdown_text(call.message.text, call.message.entities)

    await call.answer()
    await call.message.edit_text(
        text=f"{format_message_text}{edit_question}",
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )


@router.callback_query(F.data == "edit_item_title")
async def edit_item_title_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)

    edit_item_messages = []

    if item.title:
        edit_item_messages.append(
            await bot.send_message(call.message.chat.id,
                                                 f"Нажмите на текст ниже, чтобы скопировать текущий заголовок:"
                                                 f"\n\n`{item.title}`",
                                                 parse_mode=ParseMode.MARKDOWN_V2)
        )

    await asyncio.sleep(0.4)

    buttons = get_edit_item_title_keyboard(item.title)
    markup = create_general_reply_markup(buttons)

    edit_item_messages.append(
        await bot.send_message(call.message.chat.id,
                                                 f"Придумайте новый заголовок:",
                                                 reply_markup=markup)
    )

    data = await get_data(user_id)
    data['edit_item_messages'] = edit_item_messages
    await set_data(user_id, data)

    await state.set_state(states.Item.EditTitle)
    await call.answer()


@router.callback_query(F.data == "edit_item_text")
async def edit_item_text_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)

    edit_item_messages = []
    if item.get_text():
        edit_item_messages.append(
            await bot.send_message(call.message.chat.id,
                                                 f"Нажмите на текущий текст записи, чтобы скопировать:"
                                                 f"\n\n`{item.get_text()}`",
                                                 parse_mode=ParseMode.MARKDOWN_V2)
        )

    await asyncio.sleep(0.4)

    buttons = get_edit_item_text_keyboard(item.text)
    markup = create_general_reply_markup(buttons)

    edit_item_messages.append(
        await bot.send_message(call.message.chat.id,
                                                 f"Придумайте новый текст:",
                                                 reply_markup=markup)
    )

    data = await get_data(user_id)
    data['edit_item_messages'] = edit_item_messages
    await set_data(user_id, data)

    await state.set_state(states.Item.EditText)
    await call.answer()


