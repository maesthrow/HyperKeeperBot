import asyncio
from typing import List

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart
from aiogram.dispatcher.filters import Text, MediaGroupFilter
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove, User, Chat, CallbackQuery, KeyboardButton
from aiogram_media_group import media_group_handler

from firebase.firebase_collection_folders import add_user_folders, ROOT_FOLDER_ID
from firebase.firebase_collection_users import add_user
from firebase.firebase_folder_reader import get_folders_in_folder
from firebase.firebase_item_reader import get_folder_id
from handlers import states
from handlers.handlers_folder import create_folder_button, show_all_folders, show_folders
from handlers.handlers_item import movement_item_handler
from load_all import dp, bot
from models.item_model import Item
from utils.utils_ import get_inline_markup_items_in_folder, get_inline_markup_folders, get_folder_path_names
from utils.utils_button_manager import create_general_reply_markup, general_buttons_folder, \
    skip_enter_item_title_button, cancel_add_new_item_button, general_buttons_movement_item
from utils.utils_data import set_current_folder_id, get_current_folder_id
from utils.utils_items import show_all_items


# Используем фильтр CommandStart для команды /start
@dp.message_handler(CommandStart())
async def start(message: aiogram.types.Message, state: FSMContext):
    await state.reset_data()
    await state.reset_state()

    chat_id = message.from_user.id
    tg_user = aiogram.types.User.get_current()
    await add_user(tg_user)
    await add_user_folders(tg_user)

    bot_username = (await bot.me).username

    text = (f"Привет👋, {tg_user.first_name}, давайте начнем! 🚀️\n\nДля вас создано персональное хранилище, "
            f"которое доступно с помощью команды /storage\n\n"
            f"Управляйте вашими данными 🗃️, создавайте папки 🗂️ и записи 📄, сохраняйте медиафайлы 📸, "
            f"используя кнопки и подсказки на клавиатуре📱\n\n"
            f"Для доступа ко всем функциям бота жмите на кнопку 'Меню' рядом с полем ввода сообщения ↙️\n\n"
            f"Приятного использования! ☺️")
    await bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())


# Используем фильтр CommandStart для команды /storage
@dp.message_handler(commands=["storage"])
async def storage(message: aiogram.types.Message, state: FSMContext):
    await state.reset_data()
    await state.reset_state()

    tg_user = User.get_current()
    chat = Chat.get_current()
    user_folders = await get_folders_in_folder()

    data = await dp.storage.get_data(user=tg_user, chat=chat)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    movement_item_initial_folder_id = get_folder_id(movement_item_id) if movement_item_id else None

    await set_current_folder_id()

    folder_buttons = [
        await create_folder_button(folder_id, folder_data.get("name"))
        for folder_id, folder_data in user_folders.items()
    ]

    if movement_item_id:
        general_buttons = general_buttons_movement_item[:]
        if movement_item_initial_folder_id != ROOT_FOLDER_ID:
            general_buttons.insert(0, [KeyboardButton("🔀 Переместить в текущую папку")])
    else:
        general_buttons = general_buttons_folder[:]
        general_buttons.append([KeyboardButton("✏️ Переименовать папку"), KeyboardButton("🗑 Удалить папку")])

    markup = create_general_reply_markup(general_buttons)

    current_folder_path_names = await get_folder_path_names()
    await bot.send_message(chat.id, f"🗂️", reply_markup=markup)
    folders_inline_markup = await get_inline_markup_folders(folder_buttons, 1)

    folders_message = await bot.send_message(chat.id, f"🗂️ <b>{current_folder_path_names}</b>",
                                             reply_markup=folders_inline_markup)

    # load_message = await bot.send_message(chat.id, f"⌛️")
    items_inline_markup = await get_inline_markup_items_in_folder(ROOT_FOLDER_ID, 1)
    if items_inline_markup.inline_keyboard:
        for row in items_inline_markup.inline_keyboard:
            folders_inline_markup.add(*row)
        await folders_message.edit_reply_markup(reply_markup=folders_inline_markup)

    # await bot.delete_message(chat_id=chat.id, message_id=load_message.message_id)
    folders_message.reply_markup = folders_inline_markup

    data = await dp.storage.get_data(user=tg_user, chat=chat)
    data['current_keyboard'] = markup
    data['folders_message'] = folders_message
    data['page_folders'] = str(1)
    data['page_items'] = str(1)
    data['item_id'] = None
    data['dict_search_data'] = None
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)


@dp.callback_query_handler(text_contains="show_all")
async def show_all_entities_handler(call: CallbackQuery):
    if 'folders' in call.data:
        await show_all_folders(need_resend=True)
    elif 'items' in call.data:
        await show_all_items(need_to_resend=True)
    await call.answer()


@dp.message_handler(Text(equals="↪️ Перейти к общему виду папки 🗂️📄"))
async def back_to_folder(message: aiogram.types.Message):
    folder_id = await get_current_folder_id()
    await show_folders(folder_id, page_folder=1, page_item=1, need_to_resend=True)


@dp.message_handler(~Command(["start", "storage"]), content_types=['text'])
async def any_message(message: aiogram.types.Message, state: FSMContext):
    if not await is_message_allowed_new_item(message):
        return

    add_item_messages = [message]

    buttons = [[skip_enter_item_title_button, cancel_add_new_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    add_item_messages.append(
        await bot.send_message(message.chat.id, "Сейчас сохраним Вашу новую запись 👌")
                               #reply_markup=ReplyKeyboardRemove())
    )
    await asyncio.sleep(0.7)
    add_item_messages.append(
        await bot.send_message(message.chat.id, "Добавьте заголовок:",
                               reply_markup=inline_markup)
    )

    # if message.content_type == aiogram.types.ContentType.TEXT:
    item = Item(message.text)

    await state.update_data(item=item, add_item_messages=add_item_messages)

    await states.Item.NewStepTitle.set()


@dp.message_handler(MediaGroupFilter(is_media_group=True),
                    content_types=['photo', 'document', 'video', 'audio', 'voice', 'video_note', 'sticker'])
@media_group_handler
async def media_files_handler(messages: List[aiogram.types.Message], state: FSMContext):
    data = await state.get_data()
    add_item_messages = data.get('add_item_messages', None)
    if not add_item_messages:
        need_pre_save_message = True
    else:
        need_pre_save_message = False
    await files_in_message_handler(messages, state, need_pre_save_message=need_pre_save_message)


@dp.message_handler(content_types=['photo', 'document', 'video', 'audio', 'voice', 'video_note', 'sticker'])
async def media_file_handler(message: aiogram.types.Message, state: FSMContext):
    await files_in_message_handler([message], state)


async def files_in_message_handler(messages: List[aiogram.types.Message], state: FSMContext, need_pre_save_message=True):
    if not await is_message_allowed_new_item(messages[0]):
        return

    if need_pre_save_message:
        await state.update_data(add_item_messages="sample_add_item_messages")

    add_item_messages = []
    if need_pre_save_message:
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

    new_item: Item = Item("")
    for message in messages:
        new_item = await get_new_item_from_state_data(message, state)
        file_id = get_file_id(message)
        if file_id:
            new_item.media[message.content_type].append(file_id)
    # if new_item.text == "":
    #     new_item.text = new_item.date_created.strftime("%Y-%m-%d %H:%M")

    if need_pre_save_message:
        await state.update_data(item=new_item, add_item_messages=add_item_messages)
    else:
        await state.update_data(item=new_item)
    await states.Item.NewStepTitle.set()


def get_file_id(message: aiogram.types.Message):
    content_type = message.content_type
    file_id = None
    if content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif content_type == 'video':
        file_id = message.video.file_id
    elif content_type == 'audio':
        file_id = message.audio.file_id
    elif content_type == 'document':
        file_id = message.document.file_id
    elif content_type == 'voice':
        file_id = message.voice.file_id
    elif content_type == 'video_note':
        file_id = message.video_note.file_id
    # elif content_type == 'location':
    #     file_id = message.location
    # elif content_type == 'contact':
    #     file_id = message.contact
    elif content_type == 'sticker':
        file_id = message.sticker.file_id
    return file_id


async def get_new_item_from_state_data(message: aiogram.types.Message, state: FSMContext):
    # data = await dp.storage.get_data(user=message.from_user, chat=message.chat)
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
        new_item = Item(message_text)

    await state.update_data(item=new_item)
    return new_item


async def is_message_allowed_new_item(message: aiogram.types.Message):
    if message.text == "🔄 Новый поиск 🔍️":
        return False

    data = await dp.storage.get_data(user=message.from_user, chat=message.chat)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        current_folder_id = await get_current_folder_id()
        await movement_item_handler(message, current_folder_id)
        return False

    dict_search_data = data.get('dict_search_data', None)
    if dict_search_data:
        await message.reply('Завершите режим поиска 🔍 для добавления новой записи.')
        return False

    return True
