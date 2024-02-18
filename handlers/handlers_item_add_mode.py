import asyncio
from typing import List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup

from callbacks.callbackdata import ChooseTypeAddText
from handlers import states
from handlers.filters import ItemAddModeFilter
from handlers.handlers_folder import show_folders
from handlers.handlers_item import show_item
from load_all import dp, bot
from models.item_model import Item
from utils.data_manager import get_data
from utils.utils_button_manager import create_general_reply_markup, general_buttons_add_mode, cancel_add_mode_button
from utils.utils_files import get_file_id_by_content_type
from utils.utils_items_db import util_edit_item
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import preformat_text

router = Router()
dp.include_router(router)

choose_type_add_buttons = [
    InlineKeyboardButton(text="Дополнение страницы", callback_data=ChooseTypeAddText(type='join').pack()),
    InlineKeyboardButton(text="Новая страница", callback_data=ChooseTypeAddText(type='new_page').pack()),
]


@router.message(ItemAddModeFilter(), F.text == cancel_add_mode_button.text)
async def cancel_edit_item(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    await state.clear()
    await show_folders(user_id, need_to_resend=True)
    await asyncio.sleep(0.1)
    await show_item(user_id, item_id)


@router.callback_query(F.data == "add_to_item")
async def add_to_item_handler(call: CallbackQuery, state: FSMContext):
    markup = create_general_reply_markup(general_buttons_add_mode)
    await bot.send_message(
        chat_id=call.from_user.id,
        text="Отправьте в сообщении то, чем хотите дополнить новую запись:",
        reply_markup=markup
    )
    await state.set_state(states.Item.AddTo)
    await call.answer()


# @router.message(states.Item.AddTo, F.content_type == 'text')
async def add_text_to_message_handler(messages: List[Message], state: FSMContext):
    user_id = messages[0].from_user.id

    inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=[choose_type_add_buttons], resize_keyboard=True)
    await bot.send_message(user_id, 'Как вы хотите сохранить новый текст?', reply_markup=inline_markup)
    #await asyncio.sleep(0.5)

    await state.update_data(text_messages=messages)
    await state.set_state(states.Item.ChooseTypeAddText)


@router.message(states.Item.ChooseTypeAddText)
async def message_on_choose_type_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id

    inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=[choose_type_add_buttons], resize_keyboard=True)
    await bot.send_message(
        chat_id=user_id,
        text='Выберите один из вариантов.\nКак вы хотите сохранить новый текст?',
        reply_markup=inline_markup
    )


@router.callback_query(ChooseTypeAddText.filter())
async def choose_type_add_text_handler(call: CallbackQuery, state: FSMContext):
    callback_data: ChooseTypeAddText = ChooseTypeAddText.unpack(call.data)

    user_id = call.from_user.id
    data = await state.get_data()
    item_id = data.get('item_id')
    item: Item = await get_item(user_id, item_id)
    messages = data.get('text_messages', [])

    texts = []
    for message in messages:
        # add_item_messages.append(message)
        format_message_text = preformat_text(message.text, message.entities)
        texts.append(format_message_text)
    item.add_text(texts, on_new_page=(callback_data.type == 'new_page'))

    message_success_text = "Добавил новый текст в запись ✅"
    message_failure_text = "Что то пошло не так при добавлении текста ❌"

    result = await util_edit_item(user_id, item_id, item)
    if result:
        sent_message = await bot.send_message(user_id, message_success_text)
    else:
        sent_message = await bot.send_message(user_id, message_failure_text)
    await state.clear()
    await asyncio.sleep(0.4)
    await show_folders(user_id, need_to_resend=True)
    await asyncio.sleep(0.1)
    await show_item(user_id, item_id, page=item.last_page_number())


async def add_files_to_message_handler(messages: List[Message], state: FSMContext):
    # add_item_messages = messages

    user_id = messages[0].from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    item: Item = await get_item(user_id, item_id)

    for message in messages:
        file_id = get_file_id_by_content_type(message)
        if file_id:
            item.media[message.content_type].append(file_id)
        await bot.delete_message(message.from_user.id, message.message_id)
    # if new_item.text == "":
    #     new_item.text = new_item.date_created.strftime("%Y-%m-%d %H:%M")

    message_success_text = "Добавил новые файлы в запись ✅"
    message_failure_text = "Что то пошло не так при добавлении файлов ❌"

    result = await util_edit_item(user_id, item_id, item)
    if result:
        sent_message = await bot.send_message(user_id, message_success_text)
    else:
        sent_message = await bot.send_message(user_id, message_failure_text)
    await asyncio.sleep(0.7)
    await state.clear()
    await show_folders(user_id, need_to_resend=True)
    await asyncio.sleep(0.2)
    await show_item(user_id, item_id)
