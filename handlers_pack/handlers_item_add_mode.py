import asyncio
from typing import List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import ChooseTypeAddText
from handlers_pack import states
from handlers_pack.filters import ItemAddModeFilter, OnlyAddTextToItemFilter, ItemAllAddModesFilter
from handlers_pack.handlers_folder import show_folders
from handlers_pack.handlers_item import show_item
from load_all import dp, bot
from models.item_model import Item
from utils.data_manager import get_data
from utils.utils_button_manager import create_general_reply_markup, general_buttons_add_mode, cancel_add_mode_button
from utils.utils_files import get_file_info_by_content_type
from utils.utils_items_db import util_edit_item
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import preformat_text

router = Router()
dp.include_router(router)


def get_choose_type_add_text_keyboard(item: Item, page=-1):
    print(f'page ={page}')
    new_page_text = "🆕 Новая"
    display_page = page + 1
    while display_page < 1:
        display_page += 1
    builder = InlineKeyboardBuilder()
    builder.button(text=f"⤵️ Текущая ({display_page})", callback_data=ChooseTypeAddText(type='join', page=page).pack())
    if 0 <= page < item.pages_count() - 1:
        builder.button(text="➡️ Последняя", callback_data=ChooseTypeAddText(type='join', page=-1).pack())
        new_page_text = f"{new_page_text} страница"
    builder.button(text=new_page_text, callback_data=ChooseTypeAddText(type='new_page', page=-1).pack())
    builder.adjust(2, 1)
    return builder.as_markup()


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
        text="<i>Отправьте в сообщении то, чем хотите дополнить запись:</i>",
        reply_markup=markup
    )
    await state.set_state(states.ItemState.AddTo)
    await state.update_data(bot_message=call.message)
    await call.answer()


# @router.message(F.content_type == 'text')
async def add_text_to_item_handler(messages: List[Message], state: FSMContext, is_new_item: bool, item: Item,
                                   page: int, user_id=None):
    if not user_id:
        user_id = messages[0].from_user.id

    inline_markup = get_choose_type_add_text_keyboard(item, page)
    await bot.send_message(user_id, 'На какую страницу добавить новый текст?', reply_markup=inline_markup)
    # await asyncio.sleep(0.5)

    await state.update_data(text_messages=messages)
    if is_new_item:
        await state.set_state(states.ItemState.ChooseTypeAddTextToNewItem)
    else:
        await state.set_state(states.ItemState.ChooseTypeAddText)


@router.message(states.ItemState.ChooseTypeAddTextToNewItem)
@router.message(states.ItemState.ChooseTypeAddText)
async def message_on_choose_type_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await bot.delete_message(user_id, message.message_id)

    info_message = await bot.send_message(
        chat_id=user_id,
        text='❗ <i>Выберите один из вариантов ⬆️\n\nИли отмените дополнение записи ⬇️</i>',
    )
    await asyncio.sleep(2.7)
    await bot.delete_message(user_id, info_message.message_id)


@router.callback_query(OnlyAddTextToItemFilter(), ChooseTypeAddText.filter())
async def on_add_text_to_item_handler(call: CallbackQuery, state: FSMContext):
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
    await call.answer()
    await asyncio.sleep(0.4)
    await show_folders(user_id, need_to_resend=True)
    await asyncio.sleep(0.1)
    await show_item(user_id, item_id, page=item.last_page_number())


async def add_files_to_message_handler(messages: List[Message], state: FSMContext):
    # add_item_messages = messages
    if not messages:
        return

    user_id = messages[0].from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    item: Item = await get_item(user_id, item_id)

    for message in messages:
        file_info = get_file_info_by_content_type(message)
        if file_info:
            item.media[message.content_type].append(file_info)
        await bot.delete_message(message.from_user.id, message.message_id)
    # if new_item.text == "":
    #     new_item.text = new_item.date_created.strftime("%Y-%m-%d %H:%M")

    if len(messages) == 1:
        message_success_text = "Добавил новый файл в запись ✅"
    else:
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
