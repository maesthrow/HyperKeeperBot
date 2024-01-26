import concurrent.futures
import asyncio
import functools
import re
from html import escape

import aiogram
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, \
    KeyboardButton, Message

from callbacks.callbackdata import FolderCallback
from firebase_pack.firebase_collection_folders import ROOT_FOLDER_ID
from handlers import states
from handlers.message_manager import send_ok_info_message
from handlers.states import Folder
from load_all import bot, dp
from utils.data_manager import get_data, set_data
from utils.utils_ import get_inline_markup_items_in_folder, get_inline_markup_folders, \
    get_page_info, get_folder_name, get_sub_folder_names, get_folder_path_names
from utils.utils_button_manager import (general_buttons_folder, create_general_reply_markup,
                                        general_buttons_folder_show_all, general_buttons_movement_item, \
                                        general_buttons_statistic_folder, check_button_exists_part_of_text,
                                        get_folders_with_items_inline_markup)
from utils.utils_data import get_current_folder_id, set_current_folder_id
from utils.utils_folders import get_folder_statistic, \
    get_parent_folder_id, is_valid_folder_name, invalid_chars, clean_folder_name
from utils.utils_folders_db import util_delete_folder, util_add_new_folder, util_rename_folder
from utils.utils_items import show_all_items

# from aiogram.utils.exceptions import MessageNotModified

cancel_enter_folder_name_button = InlineKeyboardButton(text="Отмена", callback_data=f"cancel_enter_folder_name")
back_to_up_level_folder_button = InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_up_level_folder")

router = Router()
dp.include_router(router)


async def show_folders(user_id, current_folder_id=None, page_folder=None, page_item=None, need_to_resend=False):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future = executor.submit(functools.partial(
            do_show_folders,
            user_id=user_id,
            current_folder_id=current_folder_id,
            page_folder=page_folder,
            page_item=page_item,
            need_to_resend=need_to_resend))
        result = await future.result(timeout=30)


async def do_show_folders(user_id, current_folder_id=None, page_folder=None, page_item=None, need_to_resend=False):
    if not current_folder_id:
        current_folder_id = await get_current_folder_id(user_id)
    await set_current_folder_id(user_id, current_folder_id)

    data = await get_data(user_id)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        general_buttons = general_buttons_movement_item[:]
    else:
        general_buttons = general_buttons_folder[:]
    if True:  # current_folder_id != ROOT_FOLDER_ID:
        if not movement_item_id:
            general_buttons.append([
                KeyboardButton(text="✏️ Переименовать папку"),
                KeyboardButton(text="🗑 Удалить папку")
            ])
    markup = create_general_reply_markup(general_buttons)

    folders_page_info = await get_page_info(user_id, current_folder_id, 'folders', page_folder)
    current_folder_page = folders_page_info.get('current_page_folders')
    new_page_folders = folders_page_info.get('page_folders')

    if current_folder_page == 0:
        await show_all_folders(user_id, need_resend=need_to_resend)
        return

    items_page_info = await get_page_info(user_id, current_folder_id, 'items', page_item)
    current_item_page = items_page_info.get('current_page_items')
    new_page_items = items_page_info.get('page_items')

    if current_item_page == 0:
        await show_all_items(user_id)
        return

    current_folder_path_names = await get_folder_path_names(user_id, current_folder_id)

    folders_inline_markup = await get_inline_markup_folders(user_id, current_folder_id, current_folder_page)
    folders_message: Message = data.get('folders_message')

    if current_folder_page > 0:
        items_inline_markup = await get_inline_markup_items_in_folder(
            user_id, current_folder_id, current_page=current_item_page
        )
        if items_inline_markup.inline_keyboard:
            folders_inline_markup = get_folders_with_items_inline_markup(folders_inline_markup,
                                                                         items_inline_markup)
        if current_folder_id != ROOT_FOLDER_ID:
            folders_inline_markup.inline_keyboard.append([back_to_up_level_folder_button])

    if await is_only_folders_mode_keyboard(user_id) and current_folder_page > 0:
        need_to_resend = True

    try:
        if not need_to_resend:
            # Изменение существующего сообщения
            folders_message = await folders_message.edit_text(
                text=f"🗂️ <b>{current_folder_path_names}</b>",
                reply_markup=folders_inline_markup,
            )
        else:
            data['current_keyboard'] = markup
            await bot.send_message(user_id, f"🗂️", reply_markup=markup)
            folders_message = await send_new_folders_message(user_id, current_folder_path_names, folders_inline_markup)
    except:
        data['current_keyboard'] = markup
        await bot.send_message(user_id, f"🗂️", reply_markup=markup)
        folders_message = await send_new_folders_message(user_id, current_folder_path_names, folders_inline_markup)

    data['folders_message'] = folders_message
    data['page_folders'] = str(new_page_folders)
    data['page_items'] = str(new_page_items)
    await set_data(user_id, data)


async def send_new_folders_message(user_id, current_folder_path_names, folders_inline_markup):
    folders_message = await bot.send_message(user_id, f"⏳")
    folders_message = await folders_message.edit_text(
        text=f"🗂️ <b>{current_folder_path_names}</b>",
        reply_markup=folders_inline_markup)
    return folders_message


async def show_all_folders(user_id, current_folder_id=None, need_resend=False):
    if not current_folder_id:
        current_folder_id = await get_current_folder_id(user_id)

    general_buttons = general_buttons_folder_show_all[:]
    if current_folder_id != ROOT_FOLDER_ID:
        general_buttons.append([KeyboardButton(text="✏️ Переименовать папку"), KeyboardButton(text="🗑 Удалить папку")])
    general_buttons.append([KeyboardButton(text="↪️ Перейти к общему виду папки 🗂️📄")])
    markup = create_general_reply_markup(general_buttons)

    current_folder_path_names = await get_folder_path_names(user_id, current_folder_id)

    folders_page_info = await get_page_info(user_id, current_folder_id, 'folders', 0)
    current_folder_page = folders_page_info.get('current_page_folders')
    new_page_folders = folders_page_info.get('page_folders')

    folders_inline_markup = await get_inline_markup_folders(user_id, current_folder_id, current_folder_page)
    if current_folder_id != ROOT_FOLDER_ID:
        folders_inline_markup.inline_keyboard.append([back_to_up_level_folder_button])

    if not await is_only_folders_mode_keyboard(user_id):
        need_resend = True

    data = await get_data(user_id)

    if not need_resend:
        folders_message = data.get('folders_message', None)
        if folders_message:
            try:
                await bot.edit_message_text(chat_id=folders_message.chat.id,
                                            message_id=folders_message.message_id,
                                            text=f"🗂️ <b>{current_folder_path_names}</b>",
                                            reply_markup=folders_inline_markup,
                                            )
            except:
                await bot.send_message(user_id, f"🗂️", reply_markup=markup)
                folders_message = await bot.send_message(user_id, f"🗂️ <b>{current_folder_path_names}</b>",
                                                         reply_markup=folders_inline_markup)
                data['folders_message'] = folders_message
                data['current_keyboard'] = markup
                data['page_folders'] = str(new_page_folders)
                await set_data(user_id, data)
    else:
        await bot.send_message(user_id, f"🗂️", reply_markup=markup)
        folders_message = await bot.send_message(user_id, f"🗂️ <b>{current_folder_path_names}</b>",
                                                 reply_markup=folders_inline_markup)

    data['folders_message'] = folders_message
    data['current_keyboard'] = markup
    data['page_folders'] = str(new_page_folders)
    await set_data(user_id, data)


async def is_only_folders_mode_keyboard(user_id):
    data = await get_data(user_id)
    current_keyboard = data.get('current_keyboard', None)
    if current_keyboard:
        return check_button_exists_part_of_text(current_keyboard, "к общему виду папки")
    return False


@router.callback_query(FolderCallback.filter())
async def to_folder(call: CallbackQuery, callback_data: FolderCallback):
    user_id = call.from_user.id
    folder_id = callback_data.folder_id
    await show_folders(user_id=user_id, current_folder_id=folder_id)
    try:
        await call.answer()
    except:
        pass


@router.callback_query(lambda callback_query: callback_query.data == 'back_to_up_level_folder')
async def back_to_folders(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    folder_id = await get_current_folder_id(user_id)
    back_to_folder_id = get_parent_folder_id(folder_id)
    await show_folders(user_id, back_to_folder_id)
    await callback_query.answer()


@router.callback_query(F.data.contains("delete_folder_request"))
async def delete_folder_request(call: CallbackQuery):
    # current_folder_id = await get_current_folder_id()
    user_id = call.from_user.id
    folder_id = (call.data.replace("delete_folder_request_", "")
                 .replace("_accept", "")
                 .replace("_cancel", ""))
    folder_name = await get_folder_name(user_id, folder_id)

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        # await to_folder(call=CallbackQuery(), callback_data={"folder_id": folder_id})
        await call.answer()
        return

    try:
        # Вызываем метод для удаления папки
        result = await util_delete_folder(user_id, folder_id)
        if result:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # Отправляем ответ в виде всплывающего уведомления
            # await call.answer(text=f"Папка '{folder_name}' удалена", show_alert=True)
            result_message = await bot.send_message(call.message.chat.id, f"Папка '{folder_name}' удалена ☑️")
            await asyncio.sleep(0.5)
            parent_folder_id = get_parent_folder_id(folder_id)
            await to_folder(call=call, callback_data=FolderCallback(folder_id=parent_folder_id))
            await bot.delete_message(chat_id=result_message.chat.id, message_id=result_message.message_id)
        else:
            # Отправляем ответ в виде всплывающего уведомления
            # await call.answer(text=f"Не получилось удалить папку '{folder_name}'", show_alert=True)
            result_message = await bot.send_message(call.message.chat.id,
                                                    f"Не получилось удалить папку '{folder_name}'")
            await asyncio.sleep(0.5)
            await bot.delete_message(chat_id=result_message.chat.id, message_id=result_message.message_id)
    except:
        # await call.answer(text=f"Что то пошло не так при удалении папки", show_alert=True)
        result_message = await bot.send_message(call.message.chat.id,
                                                f"Что то пошло не так при удалении папки")
        await asyncio.sleep(0.5)
        await bot.delete_message(chat_id=result_message.chat.id, message_id=result_message.message_id)

    await call.answer()


async def edit_this_folder(message: aiogram.types.Message, folder_id, state: FSMContext):
    buttons = [[cancel_enter_folder_name_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    user_id = message.from_user.id
    folder_name = await get_folder_name(user_id, folder_id)

    data = await get_data(user_id)
    data['folder_id'] = folder_id
    await set_data(user_id, data)

    await bot.send_message(message.chat.id, f"<b>Переименовать папку</b> 📁\n'{folder_name}'",
                           reply_markup=inline_markup)
    await bot.send_message(message.chat.id,
                           "Придумайте новое название папки:", reply_markup=ReplyKeyboardRemove())

    await state.set_state(states.Folder.EditName)


async def get_enter_folder_name(message: aiogram.types.Message):
    user_id = message.from_user.id
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

    current_folder_id = await get_current_folder_id(message.from_user.id)
    parent_folder_id = get_parent_folder_id(current_folder_id)
    sub_folders_names = await get_sub_folder_names(user_id, parent_folder_id)
    new_folder_name = clean_folder_name(new_folder_name)

    if new_folder_name.lower() in map(str.lower, sub_folders_names):
        await bot.send_message(message.chat.id, "Папка с таким названием здесь уже существует.\nПридумайте другое:",
                               reply_markup=inline_markup)
        return None

    return new_folder_name


@router.message(states.Folder.NewName)
async def new_folder(message: aiogram.types.Message, state: FSMContext):
    new_folder_name = await get_enter_folder_name(message)
    if not new_folder_name:
        return

    user_id = message.from_user.id

    current_folder_id = await get_current_folder_id(user_id)
    result = await util_add_new_folder(user_id, new_folder_name, current_folder_id)
    if result:
        sent_message = await bot.send_message(message.chat.id,
                                              text=f"Новая папка '{new_folder_name}' успешно создана ✅")
    else:
        sent_message = await bot.send_message(message.chat.id,
                                              text=f"Не удалось создать папку ❌")
    # await message.answer("Новая папка успешно создана ✅")
    await state.set_state()
    await show_folders(user_id, need_to_resend=True)

    # await asyncio.sleep(1)
    # await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@router.message(states.Folder.EditName)
async def edit_folder(message: aiogram.types.Message, state: FSMContext):
    folder_new_name = await get_enter_folder_name(message)
    if not folder_new_name:
        return

    user_id = message.from_user.id
    data = await get_data(user_id)
    folder_id = data.get('folder_id')  # Получаем значение по ключу 'folder_id'

    result = await util_rename_folder(user_id, folder_id, folder_new_name)
    if result:
        sent_message = await bot.send_message(message.chat.id, "Папка успешно переименована ✅")
    else:
        sent_message = await bot.send_message(message.chat.id, "Что то пошло не так при редактировании папки ❌")

    # await dp.storage.reset_data(chat=message.chat, user=tg_user)
    await state.set_state()
    await show_folders(user_id, need_to_resend=True)

    # await asyncio.sleep(1)
    # await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@router.callback_query(F.data == "cancel_enter_folder_name", Folder.NewName)
@router.callback_query(F.data == "cancel_enter_folder_name", Folder.EditName)
async def cancel_create_new_folder(call: CallbackQuery, state: FSMContext):
    await state.set_state()
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    await show_folders(call.from_user.id)
    await call.answer()


@router.message(F.text.contains("Новая папка"))
async def create_new_folder(message: aiogram.types.Message, state: FSMContext):
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
    )
    buttons = [[cancel_enter_folder_name_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    await bot.send_message(message.chat.id, "<b>Создание новой папки</b> 📁", reply_markup=inline_markup)
    await bot.send_message(message.chat.id, "Придумайте название:", reply_markup=ReplyKeyboardRemove())

    await state.set_state(states.Folder.NewName)


@router.message(F.text == "✏️ Переименовать папку")
async def edit_folder_handler(message: aiogram.types.Message, state: FSMContext):
    current_folder_id = await get_current_folder_id(message.from_user.id)
    if current_folder_id == ROOT_FOLDER_ID:
        await asyncio.sleep(0.3)
        await send_ok_info_message(message.from_user.id, "Нельзя переименовать корневую папку 🚫")
        await bot.delete_message(message.chat.id, message.message_id)
        return

    await edit_this_folder(message, current_folder_id, state)
    await bot.delete_message(message.chat.id, message.message_id)


async def on_delete_folder(message: aiogram.types.Message):
    user_id = message.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)

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

    await bot.send_message(message.chat.id,
                           f"Хотите удалить папку 📁 '{folder_name}' и все ее содержимое?",
                           reply_markup=inline_markup)


@router.message(F.text == "🗑 Удалить папку")
async def delete_handler(message: aiogram.types.Message):
    current_folder_id = await get_current_folder_id(message.from_user.id)
    if current_folder_id == ROOT_FOLDER_ID:
        await asyncio.sleep(0.3)
        await send_ok_info_message(message.from_user.id, "Нельзя удалить корневую папку 🚫")
        await bot.delete_message(message.chat.id, message.message_id)
        return

    await on_delete_folder(message)
    await bot.delete_message(message.chat.id, message.message_id)


@router.callback_query(F.data.contains("go_to_page_folders"))
async def go_to_page_folders(call: CallbackQuery):
    match = re.match(r"(\d+)", call.data.split('_')[-1])

    if match:
        page = int(match.group(1))

        user_id = call.from_user.id
        data = await get_data(user_id)
        current_folder_id = await get_current_folder_id(user_id)
        folders_page_info = await get_page_info(user_id, current_folder_id, 'folders',
                                                page)  # get_folders_page_info(current_folder_id, page)
        new_page_folders = folders_page_info.get('page_folders')

        folders_message = data.get('folders_message')

        # user_folders = await get_folders_in_folder(user_id, current_folder_id)
        #
        # folder_buttons = [
        #     await create_folder_button(folder_id, folder_data.get("name"))
        #     for folder_id, folder_data in user_folders.items()
        # ]

        folders_inline_markup = await get_inline_markup_folders(user_id, current_folder_id, page)
        inline_markup = folders_message.reply_markup
        if inline_markup and inline_markup.inline_keyboard:
            for row in inline_markup.inline_keyboard:
                if 'item' in row[-1].callback_data:  # and 'page_items' not in button.callback_data):
                    folders_inline_markup.inline_keyboard.append(row)
        if current_folder_id != ROOT_FOLDER_ID:
            folders_inline_markup.inline_keyboard.append([back_to_up_level_folder_button])

        folders_message = await folders_message.edit_text(
            folders_message.text,
            reply_markup=folders_inline_markup,
        )

        data['folders_message'] = folders_message
        data['page_folders'] = str(new_page_folders)
        await set_data(user_id, data)

    await call.answer()


@router.callback_query(F.data.contains("go_to_page_items"))
async def go_to_page_items(call: CallbackQuery):
    match = re.match(r"(\d+)", call.data.split('_')[-1])

    if match:
        page = int(match.group(1))

        user_id = call.from_user.id
        data = await get_data(user_id)
        current_folder_id = await get_current_folder_id(user_id)
        items_page_info = await get_page_info(user_id, current_folder_id, 'items', page)
        new_page_items = items_page_info.get('page_items')

        folders_message = data.get('folders_message')

        items_inline_markup = await get_inline_markup_items_in_folder(user_id, current_folder_id, current_page=page)
        inline_markup = folders_message.reply_markup
        new_inline_markup = InlineKeyboardMarkup(inline_keyboard=[])
        if inline_markup and inline_markup.inline_keyboard:
            for row in inline_markup.inline_keyboard:
                button = row[0]  # Получаем первую кнопку в строке
                if 'folder' in button.callback_data and 'back' not in button.callback_data:
                    new_inline_markup.inline_keyboard.append(row)

        for row in items_inline_markup.inline_keyboard:
            new_inline_markup.inline_keyboard.append(row)
        if current_folder_id != ROOT_FOLDER_ID:
            new_inline_markup.inline_keyboard.append([back_to_up_level_folder_button])

        folders_message = await folders_message.edit_text(
            folders_message.text,
            reply_markup=new_inline_markup,
        )

        data['folders_message'] = folders_message
        data['page_items'] = str(new_page_items)
        await set_data(user_id, data)

    await call.answer()


@router.message(F.text == "️📊 Статистика")
async def statistic_folder_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    current_folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, current_folder_id)
    dict_folder_statistic = await get_folder_statistic(user_id, current_folder_id)
    folders_count = dict_folder_statistic['folders_count']
    items_count = dict_folder_statistic['items_count']
    deep_folders_count = dict_folder_statistic['deep_folders_count']
    deep_items_count = dict_folder_statistic['deep_items_count']
    statistic_text = (f"<u>Количество папок</u> 🗂️: <b>{folders_count}</b>\n"
                      f"<u>Количество записей</u> 📄: <b>{items_count}</b>\n\n"
                      f"<b>С учетом вложенных папок:</b>\n"
                      f"<u>Всего папок</u> 🗂️: <b>{deep_folders_count}</b>\n"
                      f"<u>Всего записей</u> 📄: <b>{deep_items_count}</b>")

    general_buttons = general_buttons_statistic_folder[:]
    markup = create_general_reply_markup(general_buttons)
    await bot.send_message(message.chat.id, f"📊 <b>Статистика папки</b>\n"
                                            f"🗂️ {folder_name}:\n\n"
                                            f"{statistic_text}",
                           reply_markup=markup)

    data = await get_data(user_id)
    data['current_keyboard'] = markup
    await set_data(user_id, data)
