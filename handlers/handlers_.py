import asyncio
from typing import List

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text, MediaGroupFilter
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove, User, Chat, CallbackQuery, KeyboardButton
from aiogram_media_group import media_group_handler

from firebase.firebase_collection_folders import add_user_folders, ROOT_FOLDER_ID
from firebase.firebase_collection_users import add_user
from handlers import states
from handlers.handlers_item import movement_item_handler
from utils.utils_button_manager import create_general_reply_markup, general_buttons_folder, \
    skip_enter_item_title_button, cancel_add_new_item_button, general_buttons_movement_item, ok_info_button
from firebase.firebase_folder_reader import get_folders_in_folder
from firebase.firebase_item_reader import get_folder_id
from handlers.handlers_folder import create_folder_button, show_all_folders, show_folders
from load_all import dp, bot
from models.item_model import Item
from utils.utils_ import get_inline_markup_items_in_folder, get_inline_markup_folders, get_folder_path_names
from utils.utils_data import set_current_folder_id, get_current_folder_id
from utils.utils_items import show_all_items

import handlers.handlers_settings
import handlers.handlers_files


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

    text = (f"Привет👋, {tg_user.first_name}, давайте начнем! 🚀️\n\nДля Вас создано персональное хранилище, "
            f"которое доступно с помощью команды /storage\n\n"
            f"Управляйте вашими данными 💼, создавайте папки 🗂️ и записи 📄, "
            f"используя кнопки и подсказки на клавиатуре📱\n\n"
            f"Для доступа ко всем функциям бота жмите на кнопку Меню рядом с полем ввода сообщения ↙️\n\n"
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
        await show_all_items()


@dp.message_handler(Text(equals="↪️ Перейти к общему виду папки 🗂️📄"))
async def back_to_folder(message: aiogram.types.Message):
    folder_id = await get_current_folder_id()
    await show_folders(folder_id, page_folder=1, page_item=1, need_to_resend=True)


@dp.message_handler(~Command(["start", "storage"]), content_types=['text', 'document'])
async def any_message(message: aiogram.types.Message, state: FSMContext):
    if message.text == "🔄 Новый поиск 🔍️":
        return

    tg_user = User.get_current()

    data = await dp.storage.get_data(user=tg_user, chat=message.chat)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        current_folder_id = await get_current_folder_id()
        await movement_item_handler(message, current_folder_id)
        return

    dict_search_data = data.get('dict_search_data', None)
    if dict_search_data:
        await message.reply('Завершите режим поиска 🔍 для добавления новой записи.')
        return

    current_state = await state.get_state()
    if not current_state or current_state != 'processing_media':

        buttons = [[skip_enter_item_title_button, cancel_add_new_item_button]]
        inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
        add_item_message_1 = await bot.send_message(message.chat.id, "Сейчас сохраним Вашу новую запись 👌",
                                                    reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.7)
        add_item_message_2 = await bot.send_message(message.chat.id, "Добавьте заголовок:",
                                                    reply_markup=inline_markup)

    if message.content_type == aiogram.types.ContentType.TEXT:
        item = Item(message.text)
    elif message.content_type == aiogram.types.ContentType.PHOTO:
        media_group_id = message.media_group_id
        if message.media_group_id:
            chat_history = await bot.get_chat_history(chat_id=message.chat.id, limit=100)

            # Фильтруем сообщения с тем же media_group_id от конкретного пользователя
            user_media_group_messages = [msg for msg in chat_history if
                                         msg.media_group_id == media_group_id and msg.from_user.id == message.from_user.id]

            # Выводим количество сообщений с тем же media_group_id от этого пользователя
            print(
                f"Количество сообщений с media_group_id {media_group_id} "
                f"от пользователя {message.from_user.id}: {len(user_media_group_messages)}")

            await state.set_data({"message_media_group_id": message.media_group_id})
            #media_group = await message.get_media_group(message.chat.id, message.media_group_id)

            # for media_message in media_group:
            #     for photo in media_message.photo:
            #         # Обрабатываем каждую фотографию
            #         file_id = photo.file_id
            #         file_info = await bot.get_file(file_id)
            #         file_path = file_info.file_path
            #         print(f"file_info {file_info}")


        # if not current_state:
        #     await state.set_state(state="processing_media")
        #     #await state.set_data({"message_media_group_id": message.media_group_id.})
        # print(f"message.message_id {message.message_id}")
        #
        # print(len(message.photo))
        # for id in message.photo:
        #     print(id)
        file_id = message.photo[-1].file_id
        if message.caption:
            message_text = message.caption
        else:
            message_text = "⬇️"
        item = Item(message_text)
        media = {"photo": [file_id]}
        item.media = media
        #await bot.send_photo(chat_id=message.chat.id, photo=file_id, caption=message.caption)
        #return

    elif message.content_type == aiogram.types.ContentType.DOCUMENT:
        print(message.document.file_name)
        await message.answer(await message.document.get_file())
        return

    await state.update_data(item=item, add_item_messages=(add_item_message_1, add_item_message_2))

    await states.Item.NewStepTitle.set()



@dp.message_handler(MediaGroupFilter(is_media_group=True), content_types=aiogram.types.ContentType.PHOTO)
@media_group_handler
async def album_handler(messages: List[aiogram.types.Message]):
    for message in messages:
        print(message)
        for photo in message.photo:
            file_id = photo.file_id
            file_info = await bot.get_file(file_id)
            file_path = file_info.file_path
            print(f"file_info {file_info}")
            await bot.send_ph

