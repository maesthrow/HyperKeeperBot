import concurrent.futures
import asyncio
import functools
import re
from typing import List

import aiogram
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, any_state
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, KeyboardButton, Message, ReplyKeyboardRemove

from handlers import states
from handlers.handlers_folder import show_all_folders, show_folders
from handlers.handlers_item import movement_item_handler, show_item
from handlers.handlers_item_add_mode import add_files_to_message_handler, add_text_to_message_handler
from load_all import dp, bot
from models.item_model import Item
from mongo_db.mongo_collection_folders import add_user_folders, ROOT_FOLDER_ID
from mongo_db.mongo_collection_users import add_user
from utils.data_manager import get_data, set_data
from utils.utils_ import get_inline_markup_items_in_folder, get_inline_markup_folders, get_folder_path_names, \
    invisible_char
from utils.utils_bot import from_url_data_item
from utils.utils_button_manager import create_general_reply_markup, general_buttons_folder, \
    skip_enter_item_title_button, cancel_add_new_item_button, general_buttons_movement_item, \
    get_folders_with_items_inline_markup, save_file_buttons, general_new_item_buttons
from utils.utils_data import set_current_folder_id, get_current_folder_id
from utils.utils_file_finder import FileFinder
from utils.utils_files import get_file_id_by_content_type
from utils.utils_items import show_all_items
from utils.utils_items_reader import get_folder_id, get_item
from utils.utils_parse_mode_converter import to_markdown_text, preformat_text
from utils.utils_sender_message_loop import send_storage, send_storage_folders, send_storage_with_items

# from aiogram_media_group import media_group_handler, MediaGroupFilter

router = Router()
dp.include_router(router)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    tg_user = message.from_user
    url_data = from_url_data_item(message.text).split()
    if len(url_data) > 1:
        if len(url_data[1].split('_')) <= 2:
            await start_url_data_item_handler(message, state, tg_user)
        else:
            await start_url_data_file_handler(message, state, tg_user)
    else:
        await start_handler(message, state, tg_user)


async def start_handler(message: Message, state: FSMContext, tg_user):
    await state.clear()

    await add_user(tg_user)
    await add_user_folders(tg_user)

    me = await bot.me()
    bot_username = me.username
    #await asyncio.sleep(1)
    text = (f"Привет👋, {tg_user.first_name}, давайте начнем! 🚀️\n\nДля вас создано персональное хранилище, "
            f"которое доступно с помощью команды /storage\n\n"
            f"Управляйте вашими данными 🗃️, создавайте папки 🗂️ и записи 📄, сохраняйте медиафайлы 📸, "
            f"используя кнопки и подсказки на клавиатуре📱\n\n"
            f"Для доступа ко всем функциям бота жмите на кнопку 'Меню' рядом с полем ввода сообщения ↙️\n\n"
            f"Приятного использования! ☺️")
    await bot.send_message(tg_user.id, text, reply_markup=ReplyKeyboardRemove())


async def start_url_data_item_handler(message, state, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    print(f"author_user_id {author_user_id}")
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)

        await start_handler(message, state, tg_user)
        url_data = from_url_data_item(message.text).split()[1]
        author_user_id = int(url_data.split('_')[0])
        item_id = url_data.split('_')[1]

        await show_item(user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id)
        await asyncio.sleep(5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)
    else:
        await bot.delete_message(tg_user.id, message.message_id)


async def start_url_data_file_handler(message, state, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    print(f"author_user_id {author_user_id}")
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)

        await start_handler(message, state, tg_user)
        url_data = from_url_data_item(message.text).split()[1]
        print(f"url_data = {url_data}")
        author_user_id = int(url_data.split('_')[0])
        item_id = url_data.split('_')[1]
        short_file_id = url_data[-8:]
        file_type: ContentType = ContentType(url_data[:-8].split('_')[-2])

        #print(f"author_user_id {author_user_id}\nitem_id {item_id}\nfile_type {file_type}\nfile_id {short_file_id}")

        inline_markup = InlineKeyboardMarkup(inline_keyboard=save_file_buttons)

        file_id = await FileFinder.get_file_id_in_item(author_user_id, item_id, file_type, short_file_id)
        if file_type == "photo":
            await bot.send_photo(tg_user.id, file_id,
                                 reply_markup=inline_markup)

        await asyncio.sleep(5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)
    else:
        await bot.delete_message(tg_user.id, message.message_id)


@router.message(Command(commands=["storage"]))
async def storage(message: Message, state: FSMContext):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future = executor.submit(functools.partial(show_storage, message, state))
        result = await future.result(timeout=5)


async def show_storage(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id

    data = await get_data(user_id)
    await set_current_folder_id(user_id)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    movement_item_initial_folder_id = get_folder_id(movement_item_id) if movement_item_id else None

    if movement_item_id:
        general_buttons = general_buttons_movement_item[:]
        if movement_item_initial_folder_id != ROOT_FOLDER_ID:
            general_buttons.insert(0, [KeyboardButton(text="🔀 Переместить в текущую папку")])
    else:
        general_buttons = general_buttons_folder[:]
        general_buttons.append([KeyboardButton(text="✏️ Переименовать папку"), KeyboardButton(text="🗑 Удалить папку")])

    markup = create_general_reply_markup(general_buttons)

    current_folder_path_names = await get_folder_path_names(user_id)

    folders_inline_markup, items_inline_markup = await get_folders_and_items(user_id, ROOT_FOLDER_ID)

    await bot.send_message(user_id, f"🗂️", reply_markup=markup)
    folders_message: Message
    folders_message = await bot.send_message(user_id, "⏳")
    #await asyncio.sleep(0.3)
    folders_message = await send_storage_folders(
        user_id=user_id,
        message=folders_message,
        text=f"🗂️ <b>{current_folder_path_names}</b>",
        inline_markup=folders_inline_markup,
        max_attempts=5
    )
    # folders_message = await asyncio.wait_for(folders_message.edit_text(
    #     text=f"🗂️ <b>{current_folder_path_names}</b>",
    #     reply_markup=folders_inline_markup,
    # ), timeout=1)

    if items_inline_markup.inline_keyboard:
        folders_inline_markup = get_folders_with_items_inline_markup(folders_inline_markup, items_inline_markup)
        # await folders_message.edit_reply_markup(reply_markup=folders_inline_markup)

    print(f"len {len(folders_inline_markup.inline_keyboard)}\n{folders_inline_markup.inline_keyboard}")

    folders_message = await send_storage_with_items(
        user_id=user_id,
        message=folders_message,
        inline_markup=folders_inline_markup,
        max_attempts=1
    )
    #await asyncio.sleep(0.3)
    print(len(folders_message.reply_markup.inline_keyboard))
    data['folders_message'] = folders_message
    data['current_keyboard'] = markup
    data['page_folders'] = str(1)
    data['page_items'] = str(1)
    data['item_id'] = None
    data['dict_search_data'] = None
    await set_data(user_id, data)


async def get_folders_and_items(user_id, root_folder_id):
    # Вызов двух асинхронных функций параллельно и ожидание результатов
    folders_inline_markup_task = get_inline_markup_folders(user_id, root_folder_id, 1)
    items_inline_markup_task = get_inline_markup_items_in_folder(user_id, root_folder_id, 1)

    # Ожидание завершения обоих задач
    folders_inline_markup = await folders_inline_markup_task
    items_inline_markup = await items_inline_markup_task

    return folders_inline_markup, items_inline_markup


@router.callback_query(F.data.contains("storage_show_all"))
async def show_all_entities_handler(call: CallbackQuery):
    user_id = call.from_user.id
    if 'folders' in call.data:
        await show_all_folders(user_id, need_resend=True)
    elif 'items' in call.data:
        await show_all_items(user_id, need_to_resend=True)
    await call.answer()


@router.message(F.text == "↪️ Перейти к общему виду папки 🗂️📄")
async def back_to_folder(message: aiogram.types.Message):
    folder_id = await get_current_folder_id(message.from_user.id)
    await show_folders(message.from_user.id, folder_id, page_folder=1, page_item=1, need_to_resend=True)


@router.message(F.via_bot == None, F.content_type == 'text')  # NotAddToFilter(),
async def any_message(message: Message, state: FSMContext):
    if not await is_message_allowed_new_item(message):
        return

    _state = await state.get_state()
    func = add_text_to_message_handler if _state == states.Item.AddTo else text_to_message_handler

    data = await state.get_data()
    text_messages = data.get('text_messages', [])
    print(f'text_messages {text_messages}')
    text_messages.append(message)
    await state.update_data(text_messages=text_messages)
    if len(text_messages) == 1:
        await func(text_messages, state)


async def text_to_message_handler(messages: List[Message], state: FSMContext):
    data = await state.get_data()
    item: Item = data.get('item', None)
    if not item:
        response_text = "Сейчас сохраним новую запись 👌"
        item = Item(id="", text=[])
    else:
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
    item.add_text(texts)

    add_item_messages.append(
        await bot.send_message(messages[0].chat.id, "Напишите заголовок или выберите действие на клавиатуре:")
    )

    await state.update_data(item=item, add_item_messages=add_item_messages)
    await state.set_state(states.Item.NewStepTitle)


@router.message(F.via_bot == None, F.content_type.in_(
    ['photo', 'document', 'video', 'audio', 'voice', 'video_note', 'sticker', 'location', 'contact']
))
async def media_files_handler(message: Message, state: FSMContext):
    # if message.via_bot:
    #     return
    print(f"message.text {message}")
    _state = await state.get_state()
    func = add_files_to_message_handler if _state == states.Item.AddTo else files_to_message_handler

    data = await state.get_data()
    file_messages = data.get('file_messages', [])
    file_messages.append(message)
    if message.media_group_id:
        await state.update_data(file_messages=file_messages)
        if len(file_messages) == 1:
            await func(file_messages, state)
    else:
        await func(file_messages, state)


async def files_to_message_handler(messages: List[Message], state: FSMContext):
    if not await is_message_allowed_new_item(messages[0]):
        return

    data = await state.get_data()
    item: Item = data.get('item', None)
    response_text = "Дополнил файлами новую запись ✅" if item else "Сейчас сохраним файлы в новую запись 👌"

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
        item = await get_new_item_from_state_data(message, state)
        file_id = get_file_id_by_content_type(message)
        if file_id:
            item.media[message.content_type].append(file_id)
    # if new_item.text == "":
    #     new_item.text = new_item.date_created.strftime("%Y-%m-%d %H:%M")

    await state.update_data(item=item, add_item_messages=add_item_messages)
    await state.set_state(states.Item.NewStepTitle)


async def get_new_item_from_state_data(message: Message, state: FSMContext):
    data = await state.get_data()
    new_item: Item = data.get('item', None)
    if new_item:
        if not new_item.get_text() and message.caption:
            new_item.text = [message.caption]
    else:
        message_text = message.caption or ""
        new_item = Item(id="", text=[message_text])
    await state.update_data(item=new_item)
    return new_item


async def is_message_allowed_new_item(message: aiogram.types.Message):
    if message.text == "🔄 Новый поиск 🔍️":
        return False

    user_id = message.from_user.id
    data = await get_data(user_id)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        current_folder_id = await get_current_folder_id(user_id)
        await movement_item_handler(message, current_folder_id)
        return False

    dict_search_data = data.get('dict_search_data', None)
    if dict_search_data:
        await message.reply('Завершите режим поиска 🔍 для добавления новой записи.')
        return False

    return True
