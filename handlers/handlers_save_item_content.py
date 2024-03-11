import asyncio
from typing import List

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from callbacks.callbackdata import TextPagesCallback
from handlers import states
from handlers.handlers_item import movement_item_message_handler
from handlers.handlers_item_add_mode import add_text_to_item_handler
from load_all import bot
from models.item_model import Item
from utils.data_manager import get_data
from utils.utils_button_manager import create_general_reply_markup, general_new_item_buttons
from utils.utils_data import get_current_folder_id
from utils.utils_files import get_file_info_by_content_type
from utils.utils_parse_mode_converter import preformat_text


async def text_to_message_handler(message: Message, state: FSMContext):
    if not await is_message_allowed_new_item(message):
        return

    data = await state.get_data()
    text_messages = data.get('text_messages', [])
    print(f'text_messages {text_messages}')
    text_messages.append(message)
    await state.update_data(text_messages=text_messages)
    if len(text_messages) == 1:
        await text_to_new_item_handler(text_messages, state)


async def text_to_new_item_handler(messages: List[Message], state: FSMContext):
    data = await state.get_data()
    item: Item = data.get('item', None)

    _state = await state.get_state()

    if not item and _state != states.ItemState.AddTo:
        response_text = "Сейчас сохраним новую запись 👌"
        item = Item(id="", text=[])
        await save_text_to_new_item_and_set_title(state=state, item=item, messages=messages,
                                                  response_text=response_text)
    else:
        is_new_item = _state == states.ItemState.NewStepAdd
        page = -1
        if not item:
            item = data.get('current_item')
        if item and not is_new_item and item.pages_count() > 1:
            bot_message: Message = data.get('bot_message')
            mid_btn = bot_message.reply_markup.inline_keyboard[0][1]
            call_data: TextPagesCallback = TextPagesCallback.unpack(mid_btn.callback_data)
            page = call_data.page
        elif item and is_new_item:
            page = item.pages_count() - 1

        await add_text_to_item_handler(messages, state, is_new_item=is_new_item, item=item, page=page)


async def save_text_to_new_item_and_set_title(
        state: FSMContext,
        item: Item,
        messages: List[Message],
        response_text: str = None,
        is_new_page=False
):
    if not response_text:
        response_text = "Дополнил новую запись ✅"

    add_item_messages = []
    markup = create_general_reply_markup(general_new_item_buttons)
    add_item_messages.append(await bot.send_message(messages[0].chat.id, response_text, reply_markup=markup))
    await asyncio.sleep(0.5)

    texts = []
    for message in messages:
        add_item_messages.append(message)
        format_message_text = preformat_text(message.text, message.entities)
        texts.append(format_message_text)
    item.add_text(texts, on_new_page=is_new_page)

    add_item_messages.append(
        await bot.send_message(messages[0].chat.id, "Напишите заголовок или выберите действие на клавиатуре:")
    )

    await state.update_data(item=item, add_item_messages=add_item_messages)
    await state.set_state(states.ItemState.NewStepTitle)


async def files_to_message_handler(messages: List[Message], state: FSMContext):
    if (not messages or
            not await is_message_allowed_new_item(messages[0])):
        return

    data = await state.get_data()
    item: Item = data.get('item', None)
    if len(messages) == 1:
        response_text = "Дополнил новую запись файлом ✅" if item else "Сейчас сохраним файл в новую запись 👌"
    else:
        response_text = "Дополнил новую запись файлами ✅" if item else "Сейчас сохраним файлы в новую запись 👌"

    markup = create_general_reply_markup(general_new_item_buttons)
    add_item_messages = messages
    add_item_messages.append(
        await bot.send_message(messages[0].chat.id, response_text, reply_markup=markup)
    )
    await asyncio.sleep(0.5)
    add_item_messages.append(
        await bot.send_message(messages[0].chat.id, "Добавьте заголовок или выберите действие на клавиатуре:")
    )

    for message in messages:
        if message.content_type == 'text':
            continue
        item = await get_new_item_from_state_data(message, state)
        file_info = get_file_info_by_content_type(message)
        print(f'message.content_type {message.content_type}')
        if file_info:
            item.media[message.content_type].append(file_info)
    # if new_item.text == "":
    #     new_item.text = new_item.date_created.strftime("%Y-%m-%d %H:%M")

    await state.update_data(item=item, add_item_messages=add_item_messages)
    await state.set_state(states.ItemState.NewStepTitle)
    print('await state.set_state(states.Item.NewStepTitle)')


async def get_new_item_from_state_data(message: Message, state: FSMContext):
    data = await state.get_data()
    new_item: Item = data.get('item', None)
    if new_item:
        if not new_item.get_text():
            new_item.text = [""]
    else:
        new_item = Item(id="", text=[""])
    await state.update_data(item=new_item)
    return new_item


async def is_message_allowed_new_item(message: Message):
    if message.text == "🔄 Новый поиск 🔍️":
        return False

    user_id = message.from_user.id
    data = await get_data(user_id)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        current_folder_id = await get_current_folder_id(user_id)
        await movement_item_message_handler(message, current_folder_id)
        return False

    dict_search_data = data.get('dict_search_data', None)
    if dict_search_data:
        await message.reply('Завершите режим поиска 🔍 для добавления новой записи.')
        return False

    return True