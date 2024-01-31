import concurrent.futures
import asyncio
import functools
from typing import List

import aiogram
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove, CallbackQuery, KeyboardButton, Message

from handlers import states
from handlers.handlers_folder import show_all_folders, show_folders
from handlers.handlers_item import movement_item_handler, show_item
from load_all import dp, bot
from models.item_model import Item
from mongo_db.mongo_collection_folders import add_user_folders, ROOT_FOLDER_ID
from mongo_db.mongo_collection_users import add_user
from utils.data_manager import get_data, set_data
from utils.utils_ import get_inline_markup_items_in_folder, get_inline_markup_folders, get_folder_path_names
from utils.utils_bot import from_url_data_item
from utils.utils_button_manager import create_general_reply_markup, general_buttons_folder, \
    skip_enter_item_title_button, cancel_add_new_item_button, general_buttons_movement_item, \
    get_folders_with_items_inline_markup
from utils.utils_data import set_current_folder_id, get_current_folder_id
from utils.utils_files import get_file_id_by_content_type
from utils.utils_items import show_all_items
from utils.utils_items_reader import get_folder_id
from utils.utils_sender_message_loop import send_storage, send_storage_folders, send_storage_with_items

# from aiogram_media_group import media_group_handler, MediaGroupFilter

router = Router()
dp.include_router(router)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    tg_user = message.from_user
    url_data = from_url_data_item(message.text).split()
    if len(url_data) > 1:
        await start_url_data_handler(message, state, tg_user)
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


async def start_url_data_handler(message, state, tg_user):
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    if not author_user_id:
        await start_handler(message, state, tg_user)
        url_data = from_url_data_item(message.text).split()[1]
        author_user_id = int(url_data.split('_')[0])
        item_id = url_data.split('_')[1]

        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        await show_item(user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id)
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
        max_attempts=10
    )
    # folders_message = await asyncio.wait_for(folders_message.edit_text(
    #     text=f"🗂️ <b>{current_folder_path_names}</b>",
    #     reply_markup=folders_inline_markup,
    # ), timeout=1)

    if items_inline_markup.inline_keyboard:
        folders_inline_markup = get_folders_with_items_inline_markup(folders_inline_markup, items_inline_markup)
        # await folders_message.edit_reply_markup(reply_markup=folders_inline_markup)
    #await asyncio.sleep(0.3)
    data['folders_message'] = await send_storage_with_items(
        user_id=user_id,
        message=folders_message,
        inline_markup=folders_inline_markup,
        max_attempts=10
    )
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


@router.message(F.content_type == 'text')
async def any_message(message: aiogram.types.Message, state: FSMContext):
    if not await is_message_allowed_new_item(message):
        return

    add_item_messages = [message]

    buttons = [[skip_enter_item_title_button, cancel_add_new_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    add_item_messages.append(
        await bot.send_message(message.chat.id, "Сейчас сохраним Вашу новую запись 👌")
        # reply_markup=ReplyKeyboardRemove())
    )
    await asyncio.sleep(0.7)
    add_item_messages.append(
        await bot.send_message(message.chat.id, "Добавьте заголовок:",
                               reply_markup=inline_markup)
    )

    # if message.content_type == aiogram.types.ContentType.TEXT:
    item = Item(id="", text=message.text)

    await state.update_data(item=item, add_item_messages=add_item_messages)

    await state.set_state(states.Item.NewStepTitle)


@router.message(F.content_type.in_(
    ['photo', 'document', 'video', 'audio', 'voice', 'video_note', 'sticker', 'location', 'contact']
))
async def media_files_handler(message: Message, state: FSMContext):
    if message.content_type == 'sticker':
        print(f"message: {message.sticker}")
    if message.media_group_id:
        data = await state.get_data()
        file_messages = data.get('file_messages', [])

        if len(file_messages) == 0:
            file_messages = [message]
            data['file_messages'] = file_messages
            await state.update_data(file_messages=file_messages)
            await asyncio.sleep(1)
            data = await state.get_data()
            await files_in_message_handler(data['file_messages'], state)
        else:
            file_messages.append(message)
            await state.update_data(file_messages=file_messages)
    else:
        await files_in_message_handler([message], state)


async def files_in_message_handler(messages: List[aiogram.types.Message], state: FSMContext):
    if not await is_message_allowed_new_item(messages[0]):
        return

    add_item_messages = []
    for message in messages:
        add_item_messages.append(message)

    buttons = [[skip_enter_item_title_button, cancel_add_new_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    add_item_messages.append(
       await bot.send_message(messages[0].chat.id, "Сейчас сохраним Вашу новую запись 👌",
                               reply_markup=ReplyKeyboardRemove())
    )
    await asyncio.sleep(0.7)
    add_item_messages.append(
        await bot.send_message(messages[0].chat.id, "Добавьте заголовок:",
                               reply_markup=inline_markup)
    )

    new_item: Item = Item(id="", text="")
    for message in messages:
        new_item = await get_new_item_from_state_data(message, state)
        file_id = get_file_id_by_content_type(message)
        if file_id:
            new_item.media[message.content_type].append(file_id)
    # if new_item.text == "":
    #     new_item.text = new_item.date_created.strftime("%Y-%m-%d %H:%M")

    await state.update_data(item=new_item, add_item_messages=add_item_messages)
    await state.set_state(states.Item.NewStepTitle)


async def get_new_item_from_state_data(message: aiogram.types.Message, state: FSMContext):
    data = await state.get_data()
    new_item: Item = data.get('item', None)
    if new_item:
        if new_item.text == "" and message.caption:
            new_item.text = message.caption
    else:
        if message.caption:
            message_text = message.caption
        else:
            message_text = ""
        new_item = Item(id="", text=message_text)

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
