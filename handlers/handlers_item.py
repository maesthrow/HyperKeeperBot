import asyncio
import copy

import aiogram
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove

import load_all
from enums.enums import Environment
from handlers import states
from handlers.handlers_edit_item_title import on_edit_item
from handlers.handlers_folder import show_folders
from handlers.handlers_search import show_search_results
from handlers.handlers_settings import CURRENT_LABEL, get_inline_markup_with_selected_current_setting
from load_all import dp, bot
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_ import get_inline_markup_for_accept_cancel, get_environment
from utils.utils_button_manager import item_inline_buttons, item_inline_buttons_with_files, hide_item_files_button
from utils.utils_data import get_current_folder_id, set_current_folder_id
from utils.utils_item_show_files import show_item_files
from utils.utils_items_db import util_add_item_to_folder, util_delete_item, util_delete_all_items_in_folder, \
    util_move_item

import handlers.handlers_item_edit_inline_buttons
from utils.utils_items_reader import get_item, get_folder_id

cancel_edit_item_button = InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_edit_item")

choose_edit_item_content_buttons = [
    InlineKeyboardButton(text="📝 Текст", callback_data=f"edit_content_text"),
    InlineKeyboardButton(text="📸 Медиафайлы", callback_data=f"edit_content_media")
]

choose_type_edit_item_buttons = [
    InlineKeyboardButton(text="➕ Добавить", callback_data=f"new_text_type_add"),
    InlineKeyboardButton(text="🔄 Перезаписать", callback_data=f"new_text_type_rewrite")
]
add_none_title_item_button = InlineKeyboardButton(text="🪧 Пустой заголовок", callback_data=f"add_none_title_item")


router = Router()
dp.include_router(router)


# Обработчик для ответа на нажатие кнопки
@router.callback_query(lambda c: c.data and c.data.startswith('item_'))
async def show_item_button(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = await get_data(user_id)
    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        current_folder_id = await get_current_folder_id(user_id)
        await movement_item_handler(callback_query.message, current_folder_id)
        await callback_query.answer()
        return

    # Получаем item_id из callback_data
    item_id = callback_query.data.split('_')[1]
    await show_item(user_id, item_id)
    await callback_query.answer()


async def show_item(user_id, item_id):
    item = await get_item(user_id, item_id)

    #item_inlines = await get_item_inlines(item)
    inline_markup = await get_item_inline_markup(item) #InlineKeyboardMarkup(row_width=2, inline_keyboard=item_inlines)
    message_text = await item.get_body()
    bot_message = await bot.send_message(chat_id=user_id, text=message_text, reply_markup=inline_markup)

    await show_item_files(user_id, item)

    # await dp.storage.update_data(user=tg_user, chat=chat, data={'current_keyboard': markup})
    data = await get_data(user_id)
    data['bot_message'] = bot_message
    data['item_id'] = item_id
    data['current_item'] = item
    data['current_inline_markup'] = inline_markup
    #data['current_keyboard'] = markup
    await set_data(user_id, data)
    load_all.current_item[user_id] = item


async def get_item_inline_markup(item: Item):
    all_media_values = await item.get_all_media_values()
    if len(all_media_values) == 0:
        item_inlines = item_inline_buttons
    else:
        item_inlines = item_inline_buttons_with_files
        item_inlines[-1][-1] = hide_item_files_button
    item_inlines[0][0].switch_inline_query = await item.get_inline_title()
    return InlineKeyboardMarkup(row_width=2, inline_keyboard=item_inlines)


@router.message(F.text == "️↩️ Назад к папке")
async def back_to_folder(message: aiogram.types.Message):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id', None)
    if item_id:
        folder_id = get_folder_id(item_id)
    else:
        folder_id = await get_current_folder_id(user_id)
    await show_folders(user_id, folder_id, need_to_resend=True)


@router.message(F.text == "️↩️ К результатам поиска 🔎")
async def back_to_search_results(message: aiogram.types.Message):
    user_id = message.from_user.id
    data = await get_data(user_id)
    await show_search_results(message.from_user.id, data['dict_search_data'])


@router.message(F.text == "️🗂️ Перейти к папке текущей записи")
async def back_to_folder(message: aiogram.types.Message):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data['item_id']
    folder_id = get_folder_id(item_id)
    data['dict_search_data'] = None
    await set_data(user_id, data)
    await show_folders(user_id, folder_id, need_to_resend=True)


@router.callback_query(states.Item.NewStepTitle, F.data == "cancel_add_new_item")
async def cancel_add_new_item(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message in add_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)

    await state.clear()
    await show_folders(call.from_user.id)
    await call.answer()


@router.callback_query(states.Item.NewStepTitle, F.data == "skip_enter_item_title")
async def skip_enter_item_title_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    await on_add_new_item(item, call.message, state)
    await call.answer()


@router.message(states.Item.NewStepTitle)
async def new_item(message: aiogram.types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    item.title = message.text
    await on_add_new_item(item, message, state)
    await bot.delete_message(message.chat.id, message.message_id)


async def on_add_new_item(item: Item, message: aiogram.types.Message, state: FSMContext):
    user_id = message.from_user.id
    current_folder_id = await get_current_folder_id(user_id)
    new_item_id = await util_add_item_to_folder(user_id, current_folder_id, item)

    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message_del in add_item_messages:
            await bot.delete_message(message_del.chat.id, message_del.message_id)
            await asyncio.sleep(0.2)
    # await asyncio.sleep(0.4)

    await state.set_state()
    await state.set_data({})

    if new_item_id:
        accept_add_item_message = await bot.send_message(message.chat.id, "Новая запись успешно добавлена ✅")
        data['accept_add_item_message'] = accept_add_item_message
        await set_data(user_id, data)
        await asyncio.sleep(0.4)
        await show_folders(user_id, need_to_resend=False)
        await asyncio.sleep(0.2)
        await show_item(user_id, new_item_id)
    else:
        await bot.send_message(message.chat.id, "Не получилось добавить запись ❌")
        # await asyncio.sleep(0.4)
        await show_folders(user_id, need_to_resend=True)


@router.message(F.text == "🗑 Удалить")
async def delete_handler(message: aiogram.types.Message):
    await on_delete_item(message)


async def on_delete_item(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id')

    # sent_message = await bot.send_message(message.chat.id, "⌛️",
    #                                       reply_markup=ReplyKeyboardRemove())

    inline_markup = await get_inline_markup_for_accept_cancel(text_accept="Да, удалить", text_cancel="Не удалять",
                                                              callback_data=f"delete_item_request_{item_id}")

    # await asyncio.sleep(0.5)

    await bot.send_message(message.chat.id,
                           f"Хотите удалить эту запись ?",
                           reply_markup=inline_markup)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@router.callback_query(F.data == "delete_item_request")
async def delete_item_request(call: CallbackQuery):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        # await show_item(item_id)
        await call.answer()
        return

    try:
        # Вызываем метод для удаления папки
        result = await util_delete_item(user_id, item_id)
        if result:
            await bot.send_message(call.message.chat.id,
                                   f"Запись удалена ☑️")  # , reply_markup=inline_markup)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # await call.answer(text=f"Запись удалена ☑️", show_alert=True)

            await asyncio.sleep(0.4)
            folder_id = await get_current_folder_id(user_id)
            await show_folders(user_id, current_folder_id=folder_id, need_to_resend=True)
            item_message = data.get('bot_message', None)
            if item_message:
                await bot.delete_message(chat_id=item_message.chat.id, message_id=item_message.message_id)
        else:
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить запись.'", show_alert=True)

    except:
        await call.answer(text=f"Что то пошло не так при удалении записи.", show_alert=True)
        # await show_folders(need_to_resend=True)

    await call.answer()


@router.message(F.text == "️🧹 Удалить все записи в папке")
async def delete_all_items_handler(message: aiogram.types.Message):
    current_folder_id = await get_current_folder_id(message.from_user.id)

    sent_message = await bot.send_message(message.chat.id, "⌛️")  # , reply_markup=ReplyKeyboardRemove())

    inline_markup = await get_inline_markup_for_accept_cancel(
        text_accept="Да, удалить", text_cancel="Не удалять",
        callback_data=f"delete_all_items_request_{current_folder_id}")

    # await asyncio.sleep(0.5)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(message.chat.id,
                           f"Действительно хотите удалить все записи в этой папке?",
                           reply_markup=inline_markup)

    await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@router.callback_query(F.data == "delete_all_items_request")
async def delete_all_items_request(call: CallbackQuery):
    user_id = call.from_user.id
    current_folder_id = await get_current_folder_id(user_id)

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        # await show_folders()
        await call.answer()
        return

    result_message = None

    try:
        # Вызываем метод для удаления папки
        result = await util_delete_all_items_in_folder(user_id, current_folder_id)
        if result:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # await call.answer(f"Запись удалена") #всплывающее сообщение сверху
            result_message = await bot.send_message(call.message.chat.id,
                                                    f"Все записи в папке удалены ☑️")
        else:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить записи.'", show_alert=True)
        await show_folders(user_id, need_to_resend=False)
    except:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await call.answer(text=f"Что то пошло не так при удалении записей.", show_alert=True)
        await show_folders(user_id, need_to_resend=False)

    if result_message:
        await asyncio.sleep(0.7)
        await bot.delete_message(chat_id=result_message.chat.id, message_id=result_message.message_id)

    await call.answer()


# @dp.message_handler(Text(equals="️✏️ Заголовок"))
# async def edit_item_title_handler(message: aiogram.types.Message, state: FSMContext:
#     tg_user = aiogram.types.User.get_current()
#     data = await dp.storage.get_data(chat=message.chat, user=tg_user)
#     item_id = data.get('item_id')
#
#     item: Item = await get_item(item_id)
#     if item.title and item.title != "":
#         item_title = f"<b>{item.title}</b>"
#     else:
#         item_title = "[пусто]"
#
#     edit_item_message_1 = await bot.send_message(message.chat.id, f"Текущий заголовок:",
#                                                  reply_markup=ReplyKeyboardRemove())
#     edit_item_message_2 = await bot.send_message(message.chat.id, f"{item_title}")
#
#     await asyncio.sleep(0.5)
#
#     buttons = [[add_none_title_item_button, cancel_edit_item_button]]
#     inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)
#
#     edit_item_message_3 = await bot.send_message(message.chat.id,
#                                                  f"Придумайте новый заголовок:",
#                                                  reply_markup=inline_markup)
#
#     data = await dp.storage.get_data(user=tg_user, chat=message.chat)
#     data['edit_item_messages'] = (edit_item_message_1, edit_item_message_2, edit_item_message_3)
#     await dp.storage.update_data(user=tg_user, chat=message.chat, data=data)
#
#     await state.set_state(states.Item.EditTitle)


@router.message(F.text == "️📝 Текст")
async def edit_item_content_handler(message: aiogram.types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    item: Item = await get_item(user_id, item_id)
    await edit_item_text_handler(message, item, state)
    # if len(item.get_all_media_values()) > 0:
    #     buttons = [choose_edit_item_content_buttons]
    #     inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)
    #     await bot.send_message(message.chat.id,
    #                                f"Что будете редактировать?",
    #                                reply_markup=inline_markup)
    #
    # else:
    #     await edit_item_text_handler(message, item)


@router.callback_query(F.data == "edit_content")
async def choose_edit_content_item(call: CallbackQuery, state: FSMContext):
    await call.answer()
    if "text" in call.data:
        user_id = call.from_user.id
        data = await get_data(user_id)
        item_id = data.get('item_id')
        item: Item = await get_item(user_id, item_id)
        await edit_item_text_handler(call.message, item, state)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    else:
        pass


async def edit_item_text_handler(message: aiogram.types.Message, item: Item, state: FSMContext):
    user_id = message.from_user.id

    if item.text and item.text != "":
        item_text = item.text
    else:
        item_text = "[пусто]"

    edit_item_messages = []
    edit_item_messages.append(
        await bot.send_message(message.chat.id, f"<b>Текущий текст:</b>",
                               reply_markup=ReplyKeyboardRemove())
    )
    edit_item_messages.append(
        await bot.send_message(message.chat.id, f"{item_text}")
    )

    await asyncio.sleep(0.2)

    buttons = copy.deepcopy([choose_type_edit_item_buttons])
    button_add: InlineKeyboardButton = buttons[0][0]
    button_add.text += f" {CURRENT_LABEL}"

    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)

    edit_item_messages.append(
        await bot.send_message(message.chat.id,
                               f"<b>Выберите способ редактирования:</b>",
                               reply_markup=inline_markup)
    )

    buttons = [[cancel_edit_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)

    await asyncio.sleep(0.2)
    edit_item_messages.append(
        await bot.send_message(message.chat.id,
                               f"<b>Введите новый текст:</b>",
                               reply_markup=inline_markup)
    )

    data = await get_data(user_id)
    data['edit_item_messages'] = edit_item_messages
    await set_data(user_id, data)

    await state.set_state(states.Item.EditText)


@router.callback_query(states.Item.EditText, F.data.contains("new_text_type"))
async def choose_type_edit_text_item(call: CallbackQuery, state: FSMContext):
    if "add" in call.data:
        current_btn_text = "➕ Добавить"
    else:
        current_btn_text = "🔄 Перезаписать"
    new_buttons = get_inline_markup_with_selected_current_setting(
        copy.deepcopy([choose_type_edit_item_buttons]), current_btn_text)

    new_inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=new_buttons)

    user_id = call.from_user.id
    data = await get_data(user_id)
    edit_item_messages = data.get('edit_item_messages')
    choose_message: aiogram.types.Message = edit_item_messages[2]
    await bot.edit_message_text(chat_id=choose_message.chat.id,
                                message_id=choose_message.message_id,
                                text=choose_message.text,
                                reply_markup=new_inline_markup,
                                )
    await state.set_data({"type_edit_text": call.data})
    await call.answer()


@router.message(states.Item.EditTitle)
@router.message(states.Item.EditText)
async def edit_item_handler(message: aiogram.types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    await on_edit_item(user_id, message.text, state)
    await show_folders(user_id, need_to_resend=True)
    await show_item(user_id, item_id)


@router.callback_query(F.data.contains("cancel_edit_item"), states.Item.EditTitle)
@router.callback_query(F.data.contains("cancel_edit_item"), states.Item.EditText)
async def cancel_edit_item(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    edit_item_messages = data.get('edit_item_messages')
    if edit_item_messages:
        for message in edit_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)

    data['edit_item_messages'] = None
    await set_data(user_id, data)
    await state.set_state()
    await show_folders(user_id, need_to_resend=True)
    await show_item(user_id, item_id)
    await call.answer()


@router.callback_query(states.Item.EditTitle, F.data.contains("add_none_title_item"))
async def add_none_title_item_handler(call: CallbackQuery, state: FSMContext):
    await on_edit_item(call.from_user.id, None, state)
    await call.answer()
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    await show_folders(user_id, need_to_resend=True)
    await show_item(user_id, item_id)


@router.message(F.text == "️🔀 Переместить")
async def movement_item_handler(message: aiogram.types.Message, folder_id=None):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    if not data.get('movement_item_id'):
        data['movement_item_id'] = item_id
        await set_data(user_id, data)

    message_text = "❗Вы не завершили перемещение❗\n" if folder_id else ""
    message_text += f"Выберите папку, в которую хотите переместить запись: ⬇️"
    await bot.send_message(message.chat.id, message_text)
    await asyncio.sleep(0.5)

    if not folder_id:
        folder_id = get_folder_id(item_id)
    await show_folders(user_id, folder_id)


@router.message(F.text == "️🚫 Отменить перемещение")
async def movement_item_cancel(message: aiogram.types.Message, folder_id=None):
    user_id = message.from_user.id

    data = await get_data(user_id)
    movement_item_id = data.get('movement_item_id')
    data['movement_item_id'] = None
    await set_data(user_id, data)

    message_text = f"Перемещение записи отменено 🔀🚫"
    await bot.send_message(message.chat.id, message_text)
    await asyncio.sleep(0.4)

    folder_id = get_folder_id(movement_item_id)
    await set_current_folder_id(user_id, folder_id)
    await show_folders(user_id, folder_id, need_to_resend=True)
    await asyncio.sleep(0.2)
    await show_item(user_id, movement_item_id)


@router.message(F.text == "🔀 Переместить в текущую папку")
async def movement_item_execute(message: aiogram.types.Message, folder_id=None):
    user_id = message.from_user.id

    data = await get_data(user_id)
    movement_item_id = data.get('movement_item_id')
    data['movement_item_id'] = None
    await set_data(user_id, data)

    folder_id = await get_current_folder_id(user_id)
    new_movement_item_id = await util_move_item(user_id, movement_item_id, folder_id)
    if new_movement_item_id:
        movement_item_id = new_movement_item_id
        message_text = f"Запись была перемещена 🔀✅"
    else:
        folder_id = get_folder_id(movement_item_id)
        message_text = f"Не удалось переместить запись ❌"

    await bot.send_message(message.chat.id, message_text)
    await asyncio.sleep(0.4)
    await show_folders(user_id, folder_id, need_to_resend=True)
    await asyncio.sleep(0.2)
    await show_item(user_id, movement_item_id)


@router.message(F.text == "🫡 Завершить режим поиска 🔍️")
async def search_item_handler(message: aiogram.types.Message):
    user_id = message.from_user.id
    data = await get_data(user_id)
    data['dict_search_data'] = None
    await set_data(user_id, data)

    environment: Environment = await get_environment(user_id)
    if environment is Environment.FOLDERS:
        await show_folders(user_id)
    elif environment is Environment.ITEM_CONTENT:
        item_id = data.get('item_id')
        if item_id:
            current_folder = get_folder_id(item_id)
            await set_current_folder_id(user_id, current_folder)
            await show_item(user_id, item_id)
