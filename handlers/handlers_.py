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
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, KeyboardButton, Message, ReplyKeyboardRemove, Location, \
    Contact

from callbacks.callbackdata import ChooseTypeAddText
from handlers import states
from handlers.filters import NotEditFileCaptionFilter
from handlers.handlers_folder import show_all_folders, show_folders
from handlers.handlers_item import movement_item_handler, show_item
from handlers.handlers_item_add_mode import add_files_to_message_handler, add_text_to_item_handler
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
from utils.utils_files import get_file_info_by_content_type, dict_to_location, dict_to_contact
from utils.utils_items import show_all_items
from utils.utils_items_reader import get_folder_id, get_item
from utils.utils_parse_mode_converter import to_markdown_text, preformat_text
from utils.utils_sender_message_loop import send_storage, send_storage_folders, send_storage_with_items
from utils.utils_show_item_entities import show_item_page_as_text_only, show_item_full_mode

# from aiogram_media_group import media_group_handler, MediaGroupFilter

router = Router()
dp.include_router(router)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    tg_user = message.from_user
    print(f'start: tg_user {tg_user}')
    url_data = from_url_data_item(message.text).split()
    if len(url_data) > 1:
        if len(url_data[1].split('_')) <= 3:
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
    # await asyncio.sleep(1)
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
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        #await start_handler(message, state, tg_user)
        url_data = from_url_data_item(message.text).split()[1]
        url_data_split = url_data.split('_')
        author_user_id = int(url_data_split[0])
        item_id = url_data_split[1]
        page = int(url_data_split[2])
        if page == -1:
            if author_user_id != tg_user.id:
                await show_item_full_mode(
                    user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id
                )
            else:
                await show_folders(tg_user.id, need_to_resend=True)
                await show_item(tg_user.id, item_id)
        else:
            await show_item_page_as_text_only(
                user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id, page=page
            )
        data = await get_data(tg_user.id)

        await asyncio.sleep(0.5)
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
        #await start_handler(message, state, tg_user)

        url_data = from_url_data_item(message.text).split()[1]
        print(f"url_data = {url_data}")
        url_data_split = url_data.split('_')

        author_user_id = int(url_data_split[0])
        item_id = url_data_split[1]
        page = int(url_data_split[2])
        short_file_id = url_data[-8:]
        str_content_type = url_data[:-8].split('_')[-2]
        if str_content_type == 'video-note':
            str_content_type = 'video_note'
        file_type: ContentType = ContentType(str_content_type)
        file_info = await FileFinder.get_file_info_in_item(author_user_id, item_id, file_type, short_file_id)
        file_id = FileFinder.get_file_id(file_info)
        caption = file_info['caption']

        inline_markup = InlineKeyboardMarkup(inline_keyboard=save_file_buttons)

        if file_type == 'document':
            await bot.send_document(chat_id=tg_user.id, document=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'photo':
            await bot.send_photo(chat_id=tg_user.id, photo=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'audio':
            await bot.send_audio(chat_id=tg_user.id, audio=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'voice':
            await bot.send_voice(chat_id=tg_user.id, voice=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'video':
            await bot.send_video(chat_id=tg_user.id, video=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'video_note':
            await bot.send_video_note(chat_id=tg_user.id, video_note=file_id, reply_markup=inline_markup)
        elif file_type == 'sticker':
            await bot.send_sticker(chat_id=tg_user.id, sticker=file_id, reply_markup=inline_markup)
        elif file_type == 'location':
            location: Location = dict_to_location(file_info['fields'])
            await bot.send_location(
                chat_id=tg_user.id,
                latitude=location.latitude,
                longitude=location.longitude,
                horizontal_accuracy=location.horizontal_accuracy,
                live_period=location.live_period,
                heading=location.heading,
                proximity_alert_radius=location.proximity_alert_radius,
                reply_markup=inline_markup
            )
        elif file_type == 'contact':
            contact: Contact = dict_to_contact(file_info['fields'])
            await bot.send_contact(
                chat_id=tg_user.id,
                phone_number=contact.phone_number,
                first_name=contact.first_name,
                last_name=contact.last_name,
                vcard=contact.vcard,
                reply_markup=inline_markup
            )
            #await bot.send_contact(chat_id=tg_user.id, latitude=None, longitude=None, reply_markup=inline_markup)

        await asyncio.sleep(0.5)
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
    # await asyncio.sleep(0.3)
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
    # await asyncio.sleep(0.3)
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


@router.message(NotEditFileCaptionFilter(), F.via_bot == None, F.content_type == 'text')  # NotAddToFilter(),
async def any_message(message: Message, state: FSMContext):
    if not await is_message_allowed_new_item(message):
        return

    #_state = await state.get_state()
    # is_new_item = states.Item.NewStepAdd

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

    if not item and _state != states.Item.AddTo:
        response_text = "Сейчас сохраним новую запись 👌"
        item = Item(id="", text=[])
        await save_text_to_new_item_and_set_title(state=state, item=item, messages=messages,
                                                  response_text=response_text)
    else:
        is_new_item = _state == states.Item.NewStepAdd
        await add_text_to_item_handler(messages, state, is_new_item=is_new_item)


@router.callback_query(states.Item.ChooseTypeAddTextToNewItem, ChooseTypeAddText.filter())
async def add_text_to_new_item_handler(call: CallbackQuery, state: FSMContext):
    callback_data: ChooseTypeAddText = ChooseTypeAddText.unpack(call.data)
    is_new_page = callback_data.type == 'new_page'
    data = await state.get_data()
    item: Item = data.get('item')
    messages = data.get('text_messages', [])
    await save_text_to_new_item_and_set_title(state=state, item=item, messages=messages, is_new_page=is_new_page)
    await call.answer()


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
    await state.set_state(states.Item.NewStepTitle)


@router.message(F.via_bot == None, F.content_type.in_(
    ['photo', 'document', 'video', 'audio', 'voice', 'video_note', 'sticker', 'location', 'contact']
))
async def media_files_handler(message: Message, state: FSMContext):
    # if message.via_bot:
    #     return
    print(f'message = {message}')
    if message.content_type == 'photo':
        print(f"message.photo = {message.photo}")
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
    await state.set_state(states.Item.NewStepTitle)
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
