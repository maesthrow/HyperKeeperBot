import asyncio
import re
from html import escape

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, \
    KeyboardButton, User, Chat
from aiogram.utils.exceptions import MessageNotModified

import states
from button_manager import general_buttons_folder, create_general_reply_markup
from firebase import ROOT_FOLDER_ID
from firebase_folder_reader import get_folder_name, get_current_folder_id, get_folder_path_names, \
    get_parent_folder_id
from firebase_folder_writer import get_sub_folder_names, set_current_folder

# from handlers_item import get_items_in_folder
from load_all import dp, bot
from utils import get_inline_markup_items_in_folder, get_inline_markup_folders, folder_callback, create_folder_button, \
    is_valid_folder_name, invalid_chars, clean_folder_name, get_page_info
from utils_folders_db import util_delete_folder, util_get_user_folders, util_add_new_folder, util_rename_folder

cancel_enter_folder_name_button = InlineKeyboardButton("Отмена", callback_data=f"cancel_enter_folder_name")


@dp.callback_query_handler(text_contains="delete_folder_request")
async def delete_folder_request(call: CallbackQuery):
    tg_user = User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)

    folder_id = (call.data.replace("delete_folder_request_", "")
                 .replace("_accept", "")
                 .replace("_cancel", ""))
    folder_name = await get_folder_name(tg_user.id, folder_id)

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await to_folder(call=CallbackQuery(), callback_data={"folder_id": current_folder_id})
        return

    try:
        # Вызываем метод для удаления папки
        result = await util_delete_folder(folder_id)
        if result:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Папка '{folder_name}' удалена", show_alert=True)
            parent_folder_id = get_parent_folder_id(folder_id)
            await to_folder(call=CallbackQuery(), callback_data={"folder_id": parent_folder_id})
        else:
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить папку '{folder_name}'", show_alert=True)
    except MessageNotModified:
        await call.answer(text=f"Что то пошло не так при удалении папки", show_alert=True)


# Определяем функцию для обработки отображения папок
async def show_folders(current_folder_id=None):
    tg_user = User.get_current()
    chat = Chat.get_current()
    if not current_folder_id:
        current_folder_id = await get_current_folder_id(tg_user.id)

    await set_current_folder(tg_user.id, current_folder_id)
    user_folders = await util_get_user_folders(current_folder_id)

    folder_buttons = [
        await create_folder_button(folder_id, folder_data.get("name"))
        for folder_id, folder_data in user_folders.items()
    ]

    general_buttons = general_buttons_folder[:]
    if current_folder_id != ROOT_FOLDER_ID:
        general_buttons.append([KeyboardButton("✏️ Переименовать папку"), KeyboardButton("🗑 Удалить папку")])
        general_buttons.append([KeyboardButton("↩️ Назад")])
    markup = create_general_reply_markup(general_buttons)

    current_folder_path_names = await get_folder_path_names(tg_user.id, current_folder_id)
    await bot.send_message(chat.id, f"🗂️", reply_markup=markup)

    folders_page_info = await get_page_info(current_folder_id, 'folders') #get_folders_page_info(current_folder_id)
    current_folder_page = folders_page_info.get('current_page_folders')
    new_page_folders = folders_page_info.get('page_folders')

    folders_inline_markup = await get_inline_markup_folders(folder_buttons, current_folder_page)

    folders_message = await bot.send_message(chat.id, f"🗂️ <b>{current_folder_path_names}</b>",
                                             reply_markup=folders_inline_markup)
    #load_message = await bot.send_message(chat.id, f"⌛️")
    items_page_info = await get_page_info(current_folder_id, 'items')
    current_item_page = items_page_info.get('current_page_items')
    new_page_items = items_page_info.get('page_items')
    items_inline_markup = await get_inline_markup_items_in_folder(current_folder_id, current_page=current_item_page)
    if items_inline_markup.inline_keyboard:
        for row in items_inline_markup.inline_keyboard:
            folders_inline_markup.add(*row)
        await folders_message.edit_reply_markup(reply_markup=folders_inline_markup)

    #await bot.delete_message(chat_id=chat.id, message_id=load_message.message_id)
    folders_message.reply_markup = folders_inline_markup
    await dp.storage.update_data(user=tg_user, chat=chat,
                                 data={'current_keyboard': markup, 'folders_message': folders_message,
                                       'page_folders': str(new_page_folders), 'page_items': str(new_page_items)})


# Используем обработчик CallbackQuery для навигации по папкам
@dp.callback_query_handler(folder_callback.filter())
async def to_folder(call: CallbackQuery, callback_data: dict):
    folder_id = callback_data["folder_id"]
    await show_folders(folder_id)


# Используем обработчик CallbackQuery для навигации по папкам
@dp.message_handler(Text(equals="↩️ Назад"))
async def back_to_folders(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    folder_id = await get_current_folder_id(tg_user.id)
    back_to_folder_id = get_parent_folder_id(folder_id)
    await to_folder(call=CallbackQuery(), callback_data={"folder_id": back_to_folder_id})


async def edit_this_folder(message: aiogram.types.Message, folder_id):
    buttons = [[cancel_enter_folder_name_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    tg_user = aiogram.types.User.get_current()
    folder_name = await get_folder_name(tg_user.id, folder_id)

    await dp.storage.update_data(user=tg_user, chat=message.chat, data={'folder_id': folder_id})

    await bot.send_message(message.chat.id, f"<b>Переименовать папку</b> 📁\n'{folder_name}'",
                           reply_markup=inline_markup)
    await bot.send_message(message.chat.id, "Придумайте новое название папки:", reply_markup=ReplyKeyboardRemove())

    await states.Folder.EditName.set()


async def get_enter_folder_name(message: aiogram.types.Message):
    buttons = [[cancel_enter_folder_name_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)

    new_folder_name = message.text

    if not is_valid_folder_name(new_folder_name):
        invalid_chars_list = ' '.join([char for char in invalid_chars if char in new_folder_name])
        invalid_chars_message = escape(
            f"❗Название папки содержит недопустимые символы ➡️ {invalid_chars_list}\nПридумайте другое название:")
        await bot.send_message(message.chat.id, invalid_chars_message, reply_markup=inline_markup)
        return None

    if len(new_folder_name) > 50:
        await bot.send_message(message.chat.id, "Слишком длинное название для папки, уложитесь в 50 символов ☺️:",
                               reply_markup=inline_markup)
        return None

    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)
    parent_folder_id = get_parent_folder_id(current_folder_id)
    sub_folders_names = await get_sub_folder_names(tg_user.id, parent_folder_id)
    new_folder_name = clean_folder_name(new_folder_name)

    if new_folder_name.lower() in map(str.lower, sub_folders_names):
        await bot.send_message(message.chat.id, "Папка с таким названием здесь уже существует.\nПридумайте другое:",
                               reply_markup=inline_markup)
        return None

    return new_folder_name


@dp.message_handler(state=states.Folder.NewName)
async def new_folder(message: aiogram.types.Message, state: FSMContext):
    new_folder_name = await get_enter_folder_name(message)
    if not new_folder_name:
        return

    tg_user = User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)
    result = await util_add_new_folder(new_folder_name, current_folder_id)
    if result:
        sent_message = await bot.send_message(message.chat.id, text=f"Новая папка '{new_folder_name}' успешно создана ✅")
    else:
        sent_message = await bot.send_message(message.chat.id,
                                              text=f"Не удалось создать папку ❌")
    # await message.answer("Новая папка успешно создана ✅")
    await state.reset_data()
    await state.reset_state()
    await show_folders()

    # await asyncio.sleep(1)
    # await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@dp.message_handler(state=states.Folder.EditName)
async def edit_folder(message: aiogram.types.Message, state: FSMContext):
    folder_new_name = await get_enter_folder_name(message)
    if not folder_new_name:
        return

    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    folder_id = data.get('folder_id')  # Получаем значение по ключу 'folder_id'

    result = await util_rename_folder(folder_id, folder_new_name)
    if result:
        sent_message = await bot.send_message(message.chat.id, "Папка успешно переименована ✅")
    else:
        sent_message = await bot.send_message(message.chat.id, "Что то пошло не так при редактировании папки ❌")

    await dp.storage.reset_data(chat=message.chat, user=tg_user)
    await state.reset_data()
    await state.reset_state()
    await show_folders()

    # await asyncio.sleep(1)
    # await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@dp.callback_query_handler(text_contains="cancel_enter_folder_name",
                           state=[states.Folder.NewName, states.Folder.EditName])
async def cancel_create_new_folder(call: CallbackQuery, state: FSMContext):
    tg_user = aiogram.types.User.get_current()
    await dp.storage.reset_data(chat=call.message.chat, user=tg_user)
    await state.reset_data()
    await state.reset_state()
    await show_folders()


@dp.message_handler(Text(contains="Новая папка"))
async def create_new_folder(message: aiogram.types.Message):
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
    )
    buttons = [[cancel_enter_folder_name_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    await bot.send_message(message.chat.id, "<b>Создание новой папки</b> 📁", reply_markup=inline_markup)
    await bot.send_message(message.chat.id, "Придумайте название:", reply_markup=ReplyKeyboardRemove())

    await states.Folder.NewName.set()


@dp.message_handler(Text(equals="✏️ Переименовать папку"))
async def edit_folder_handler(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)
    await edit_this_folder(message, current_folder_id)


async def on_delete_folder(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    # Извлекаем из callback_data идентификатор папки, который прикреплен к кнопке
    folder_id = await get_current_folder_id(tg_user.id)
    folder_name = await get_folder_name(tg_user.id, folder_id)

    sent_message = await bot.send_message(message.chat.id, "<b>Подготовка к удалению папки</b>",
                                          reply_markup=ReplyKeyboardRemove())

    inline_markup = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text="Да, удалить", callback_data=f"delete_folder_request_{folder_id}_accept"),
            ],
            [
                InlineKeyboardButton(text="Не удалять", callback_data=f"delete_folder_request_{folder_id}_cancel")
            ],
        ]
    )

    await asyncio.sleep(0.8)
    await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    await bot.send_message(message.chat.id,
                           f"Хотите удалить папку 📁 '{folder_name}' и все ее содержимое?",
                           reply_markup=inline_markup)


@dp.callback_query_handler(text_contains="go_to_page_folders")
async def go_to_page_folders(call: CallbackQuery):
    match = re.match(r"go_to_page_folders_(\d+)", call.data)

    if match:
        page = int(match.group(1))

        tg_user = User.get_current()
        chat = Chat.get_current()
        data = await dp.storage.get_data(chat=call.message.chat, user=tg_user)
        current_folder_id = await get_current_folder_id(tg_user.id)
        folders_page_info = await get_page_info(current_folder_id, 'folders', page) #get_folders_page_info(current_folder_id, page)
        new_page_folders = folders_page_info.get('page_folders')

        folders_message = data.get('folders_message')

        current_folder_id = await get_current_folder_id(tg_user.id)
        user_folders = await util_get_user_folders(current_folder_id)

        folder_buttons = [
            await create_folder_button(folder_id, folder_data.get("name"))
            for folder_id, folder_data in user_folders.items()
        ]

        folders_inline_markup = await get_inline_markup_folders(folder_buttons, page)
        inline_markup = folders_message.reply_markup
        for row in inline_markup.inline_keyboard:
            for button in row[-1:]:
                if 'item' in button.callback_data:  # and 'page_items' not in button.callback_data):
                    folders_inline_markup.add(*row)

        folders_message = await folders_message.edit_text(
            folders_message.text,
            reply_markup=folders_inline_markup,
        )
        await dp.storage.update_data(user=tg_user, chat=chat,
                                     data={'folders_message': folders_message, 'page_folders': str(new_page_folders)})


@dp.callback_query_handler(text_contains="go_to_page_items")
async def go_to_page_items(call: CallbackQuery):
    match = re.match(r"go_to_page_items_(\d+)", call.data)

    if match:
        page = int(match.group(1))

        tg_user = aiogram.types.User.get_current()
        chat = aiogram.types.Chat.get_current()
        data = await dp.storage.get_data(chat=call.message.chat, user=tg_user)
        current_folder_id = await get_current_folder_id(tg_user.id)
        items_page_info = await get_page_info(current_folder_id, 'items', page)
        new_page_items = items_page_info.get('page_items')

        folders_message = data.get('folders_message')

        current_folder_id = await get_current_folder_id(tg_user.id)

        items_inline_markup = await get_inline_markup_items_in_folder(current_folder_id, current_page=page)
        inline_markup = folders_message.reply_markup
        new_inline_markup = InlineKeyboardMarkup()
        for row in inline_markup.inline_keyboard:
            button = row[0]  # Получаем первую кнопку в строке
            if 'folder' in button.callback_data:
                new_inline_markup.add(*row)

        for row in items_inline_markup.inline_keyboard:
            new_inline_markup.add(*row)

        folders_message = await folders_message.edit_text(
            folders_message.text,
            reply_markup=new_inline_markup,
        )
        await dp.storage.update_data(user=tg_user, chat=chat,
                                     data={'folders_message': folders_message, 'page_items': str(new_page_items)})
