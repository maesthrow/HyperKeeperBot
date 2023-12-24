import asyncio
import re
from html import escape

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, KeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

import states
from button_manager import general_buttons_folder
from firebase import ROOT_FOLDER_ID
from firebase_folder_reader import get_folder_name, get_current_folder_id, get_user_folders, get_folder_path_names, \
    get_parent_folder_id
from firebase_folder_writer import delete_folder, get_sub_folder_names, add_new_folder, rename_folder, \
    set_current_folder
from handlers import create_general_reply_markup
from load_all import dp, bot

invalid_chars = r'/\:,.*?"<>|'
cancel_enter_folder_name_button = InlineKeyboardButton("Отмена", callback_data=f"cancel_enter_folder_name")
folder_callback = CallbackData("folder", "folder_id")


def is_valid_folder_name(name):
    return all(char not in invalid_chars for char in name)


def clean_folder_name(name):
    cleaned_name = ''.join(char if char not in invalid_chars and char not in '\n\r' else ' ' for char in name)
    return cleaned_name


# Определяем функцию для создания кнопок папок
async def create_folder_button(folder_id, folder_name):
    return InlineKeyboardButton(
        f"📁 {folder_name}",
        callback_data=folder_callback.new(folder_id=folder_id)
    )


# Определяем функцию для создания инлайн-разметки для папок
def create_folder_inline_markup(folder_buttons):
    inline_markup = InlineKeyboardMarkup(row_width=3)

    for button in folder_buttons:
        folder_name_button = button
        # edit_button = InlineKeyboardButton("✏️", callback_data=f"edit_{button.callback_data}")
        # delete_button = InlineKeyboardButton("🗑", callback_data=f"delete_{button.callback_data}")

        # Вычисляем ширину кнопок на основе длины текста
        folder_name_width = len(button.text)

        # Устанавливаем ширину кнопки с названием папки
        folder_name_button.resize_keyboard = True
        folder_name_button.resize_keyboard_width = folder_name_width + 2  # Добавляем отступ справа

        # Добавляем кнопки на одну строку
        inline_markup.row(folder_name_button, InlineKeyboardButton(text='', callback_data='empty'),
                          InlineKeyboardButton(text='', callback_data='empty'))
        #inline_markup.row(edit_button, delete_button, InlineKeyboardButton(text='', callback_data='empty'))

    # Регистрируем обработчик кнопок только один раз
    # edit_button_handler = lambda q: on_edit_button_click(q)
    # dp.register_callback_query_handler(edit_button_handler, lambda c: c.data.startswith("edit_"))
    # delete_button_handler = lambda q: on_delete_button_click(q)
    # dp.register_callback_query_handler(delete_button_handler, lambda c: c.data.startswith("delete_"))

    return inline_markup


# async def on_edit_button_click(query: CallbackQuery):
#     # Извлекаем из callback_data идентификатор папки, который прикреплен к кнопке
#     folder_id = query.data.replace("edit_", "").replace("folder:", "")
#     await edit_this_folder(query.message, folder_id)
#
#
# async def on_delete_button_click(query: CallbackQuery):
#     tg_user = aiogram.types.User.get_current()
#     # Извлекаем из callback_data идентификатор папки, который прикреплен к кнопке
#     folder_id = query.data.replace("delete_", "").replace("folder:", "")
#     folder_name = await get_folder_name(tg_user.id, folder_id)
#
#     sent_message = await bot.send_message(query.message.chat.id, "<b>Подготовка к удалению папки</b>",
#                                           reply_markup=ReplyKeyboardRemove())
#
#     inline_markup = InlineKeyboardMarkup(
#         row_width=2,
#         inline_keyboard=
#         [
#             [
#                 InlineKeyboardButton(text="Да, удалить", callback_data=f"delete_folder_request_{folder_id}_accept"),
#             ],
#             [
#                 InlineKeyboardButton(text="Не удалять", callback_data=f"delete_folder_request_{folder_id}_cancel")
#             ],
#         ]
#     )
#
#     await asyncio.sleep(0.8)
#     await bot.delete_message(chat_id=query.message.chat.id, message_id=sent_message.message_id)
#     await bot.send_message(query.message.chat.id,
#                            f"Хотите удалить папку 📁 '{folder_name}' и все ее содержимое?",
#                            reply_markup=inline_markup)
#     # await states.Folder.Delete.set()


@dp.callback_query_handler(text_contains="delete_folder_request")
async def delete_folder_request(call: CallbackQuery):
    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)

    folder_id = (call.data.replace("delete_folder_request_", "")
                 .replace("_accept", "")
                 .replace("_cancel", ""))
    folder_name = await get_folder_name(tg_user.id, folder_id)

    fake_callback_query = aiogram.types.CallbackQuery(
        id=call.message.message_id,
        from_user=tg_user,
        message=call.message,
        chat_instance=f"{call.message.chat.id}_{call.message.message_id}"
    )

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await to_folder(fake_callback_query, {"folder_id": current_folder_id})
        return

    try:
        # Вызываем метод для удаления папки
        result = await delete_folder(tg_user.id, folder_id)
        if result:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Папка '{folder_name}' удалена", show_alert=True)
            parent_folder_id = get_parent_folder_id(folder_id)
            await to_folder(fake_callback_query, {"folder_id": parent_folder_id})
        else:
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить папку '{folder_name}'", show_alert=True)
    except MessageNotModified:
        await call.answer(text=f"Что то пошло не так при удалении папки", show_alert=True)


# Определяем функцию для обработки отображения папок
async def show_folders(call: CallbackQuery = None, current_folder_id=None):
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    if not current_folder_id:
        current_folder_id = await get_current_folder_id(tg_user.id)
    if call:
        try:
            await call.message.edit_reply_markup()
        except:
            pass

    await set_current_folder(tg_user.id, current_folder_id)
    user_folders = await get_user_folders(tg_user.id, current_folder_id)

    folder_buttons = [
        await create_folder_button(folder_id, folder_data.get("name"))
        for folder_id, folder_data in user_folders.items()
    ]

    inline_markup = create_folder_inline_markup(folder_buttons)

    general_buttons = general_buttons_folder[:]
    if current_folder_id != ROOT_FOLDER_ID:
        general_buttons.append([KeyboardButton("✏️ Редактировать"), KeyboardButton("🗑 Удалить")])
        general_buttons.append([KeyboardButton("↩️ Назад")])
    markup = create_general_reply_markup(general_buttons)
    await dp.storage.update_data(user=tg_user, chat=chat, data={'current_keyboard': markup})

    current_folder_path_names = await get_folder_path_names(tg_user.id, current_folder_id)
    bot_message = await bot.send_message(chat.id, "🗂️", reply_markup=markup)
    await dp.storage.update_data(user=tg_user, chat=chat, data={'bot_message': bot_message})
    await bot.send_message(chat.id, f"<b>{current_folder_path_names}</b>", reply_markup=inline_markup)


# Используем обработчик CallbackQuery для навигации по папкам
@dp.callback_query_handler(folder_callback.filter())
async def to_folder(call: CallbackQuery, callback_data: dict):
    folder_id = callback_data["folder_id"]
    await show_folders(call, folder_id)


async def handle_back_to_folder(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    folder_id = await get_current_folder_id(tg_user.id)

    # Найдем соответствие паттерну
    if not re.search(r'назад к папкам', message.text, re.IGNORECASE):
        folder_id = folder_id[:folder_id.rfind("/")]

    # Создайте фиктивный CallbackQuery
    fake_callback_query = aiogram.types.CallbackQuery(
        id=message.message_id,
        from_user=tg_user,
        message=message,
        chat_instance=f"{message.chat.id}_{message.message_id}"
    )
    # Имитируйте вызов to_folder
    await to_folder(fake_callback_query, {"folder_id": folder_id})


# Используем обработчик CallbackQuery для навигации по папкам
@dp.message_handler(lambda message: re.search(r'назад', message.text, re.IGNORECASE)
                                    and not re.search(r'назад к записям', message.text, re.IGNORECASE))
async def back_to_folder(message: aiogram.types.Message):
    await handle_back_to_folder(message)


async def edit_this_folder(message: aiogram.types.Message, folder_id):
    buttons = [[cancel_enter_folder_name_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    tg_user = aiogram.types.User.get_current()
    folder_name = await get_folder_name(tg_user.id, folder_id)

    await dp.storage.update_data(user=tg_user, chat=message.chat, data={'folder_id': folder_id})

    await bot.send_message(message.chat.id, f"<b>Редактирование папки</b> 📁\n'{folder_name}'",
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

    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)
    await add_new_folder(tg_user.id, new_folder_name, current_folder_id)

    sent_message = await bot.send_message(message.chat.id, text=f"Новая папка '{new_folder_name}' успешно создана ✅")
    # await message.answer("Новая папка успешно создана ✅")
    await state.reset_data()
    await state.reset_state()
    message.text = "Назад к папкам"
    await handle_back_to_folder(message)

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

    if await rename_folder(tg_user.id, folder_id, folder_new_name):
        sent_message = await bot.send_message(message.chat.id, "Папка успешно переименована ✅")
    else:
        sent_message = await bot.send_message(message.chat.id, "Что то пошло не так при редактировании папки ❌")

    await dp.storage.reset_data(chat=message.chat, user=tg_user)
    await state.reset_data()
    await state.reset_state()
    message.text = "Назад к папкам"
    await handle_back_to_folder(message)

    # await asyncio.sleep(1)
    # await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@dp.callback_query_handler(text_contains="cancel_enter_folder_name",
                           state=[states.Folder.NewName, states.Folder.EditName])
async def cancel_create_new_folder(call: CallbackQuery, state: FSMContext):
    tg_user = aiogram.types.User.get_current()
    await dp.storage.reset_data(chat=call.message.chat, user=tg_user)
    await state.reset_data()
    await state.reset_state()
    call.message.text = "Назад к папкам"
    await handle_back_to_folder(call.message)


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


@dp.message_handler(Text(equals="✏️ Редактировать"))
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