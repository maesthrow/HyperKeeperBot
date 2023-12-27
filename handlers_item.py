import asyncio

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, \
    ReplyKeyboardRemove
from aiogram.utils.exceptions import MessageNotModified
from datetime import datetime

from aiogram.utils.markdown import escape_md

import states
from button_manager import create_general_reply_markup, skip_enter_item_title_button, general_buttons_items, \
    general_buttons_item, cancel_add_new_item_button
from enums import Environment
from firebase_folder_reader import get_current_folder_id, get_folder_name, get_parent_folder_id
from firebase_item_reader import get_folder_items, get_item
from firebase_item_writer import add_item_to_folder, delete_item, delete_all_items_in_folder, edit_item
from handlers_folder import show_folders
from load_all import dp, bot
from models import Item
from utils import get_environment, get_inline_markup_for_accept_cancel

cancel_edit_item_button = InlineKeyboardButton("Отменить", callback_data=f"cancel_edit_item")
add_none_title_item_button = InlineKeyboardButton("Пустой заголовок", callback_data=f"add_none_title_item")


# Обработчик для ответа на нажатие кнопки
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('item_'))
async def show_item_button(callback_query: CallbackQuery):
    # Получаем item_id из callback_data
    item_id = callback_query.data.split('_')[1]
    await show_item(item_id)


async def show_item(item_id):
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    item = await get_item(tg_user.id, item_id)

    # ВСПЛЫВАЮЩЕЕ СООБЩЕНИЕ!!!
    # await callback_query.answer(f"{item.title}\n{item.text}")

    if item.title:
        item_content = f"📄 <b>{item.title}</b>\n\n{item.text}"
    else:
        item_content = f"📄\n{item.text}"
    markup = create_general_reply_markup(general_buttons_item)
    bot_message = await dp.storage.update_data(user=tg_user, chat=chat, data={'current_keyboard': markup})
    await dp.storage.update_data(user=tg_user, chat=chat, data={'bot_message': bot_message, 'item_id': item_id})
    await bot.send_message(tg_user.id, item_content, reply_markup=markup)


@dp.message_handler(Text(equals="️↩️ Назад к папке"))
async def back_to_folder(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    folder_id = await get_current_folder_id(tg_user.id)
    await show_folders(folder_id)


@dp.callback_query_handler(text_contains="cancel_add_new_item", state=states.Item.NewStepTitle)
async def cancel_add_new_item(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message in add_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)

    await state.reset_data()
    await state.reset_state()
    await show_folders()


@dp.callback_query_handler(text_contains="skip_enter_item_title", state=states.Item.NewStepTitle)
async def skip_enter_item_title_handler(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    # await bot.send_message(call.message.chat.id,
    #                       f"Новая запись:\n{item.title}\n{item.text}"
    #                       )

    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)
    result = await add_item_to_folder(tg_user.id, current_folder_id, item)

    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message in add_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    await asyncio.sleep(0.4)

    if result:
        await bot.send_message(call.message.chat.id, "Новая запись успешно добавлена ✅")
    else:
        await bot.send_message(call.message.chat.id, "Не получилось добавить запись ❌")
    await asyncio.sleep(0.4)

    await state.reset_data()
    await state.reset_state()
    await show_folders()


@dp.message_handler(state=states.Item.NewStepTitle)
async def new_item(message: aiogram.types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    item.title = message.text
    # await state.update_data(item=item)
    # data = await state.get_data()
    # item = data.get('item')
    # await bot.send_message(message.chat.id,
    #                       f"Новая запись:\n{item.title}\n{item.text}"
    #                       )

    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)
    result = await add_item_to_folder(tg_user.id, current_folder_id, item)

    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message in add_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)
    await asyncio.sleep(0.4)

    if result:
        await bot.send_message(message.chat.id, "Новая запись успешно добавлена ✅")
    else:
        await bot.send_message(message.chat.id, "Не получилось добавить запись ❌")
    await asyncio.sleep(0.4)

    await state.reset_data()
    await state.reset_state()
    await show_folders()


async def on_delete_item(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id')

    sent_message = await bot.send_message(message.chat.id, "⌛️",
                                          reply_markup=ReplyKeyboardRemove())

    inline_markup = await get_inline_markup_for_accept_cancel(text_accept="Да, удалить", text_cancel="Не удалять",
                                                        callback_data=f"delete_item_request_{item_id}")

    #await asyncio.sleep(0.5)

    await bot.send_message(message.chat.id,
                           f"Хотите удалить эту запись ?",
                           reply_markup=inline_markup)
    await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@dp.callback_query_handler(text_contains="delete_item_request")
async def delete_item_request(call: CallbackQuery):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=call.message.chat, user=tg_user)
    item_id = data.get('item_id')

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await show_item(item_id)
        return

    try:
        # Вызываем метод для удаления папки
        result = await delete_item(tg_user.id, item_id)
        if result:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # Отправляем ответ в виде всплывающего уведомления
            # await call.answer(f"Запись удалена") #всплывающее сообщение сверху
            await call.answer(text=f"Запись удалена.", show_alert=True)
        else:
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить запись.'", show_alert=True)
        await show_folders()
    except MessageNotModified:
        await call.answer(text=f"Что то пошло не так при удалении записи.", show_alert=True)
        await show_folders()


@dp.message_handler(Text(equals="️🧹 Удалить все записи в папке"))
async def delete_all_items_handler(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)

    sent_message = await bot.send_message(message.chat.id, "⌛️",
                                          reply_markup=ReplyKeyboardRemove())

    inline_markup = await get_inline_markup_for_accept_cancel(text_accept="Да, удалить", text_cancel="Не удалять",
                                                        callback_data=f"delete_all_items_request_{current_folder_id}")

    #await asyncio.sleep(0.5)

    await bot.send_message(message.chat.id,
                           f"Действительно хотите удалить все записи в этой папке?",
                           reply_markup=inline_markup)
    await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@dp.callback_query_handler(text_contains="delete_all_items_request")
async def delete_all_items_request(call: CallbackQuery):
    tg_user = aiogram.types.User.get_current()
    current_folder_id = await get_current_folder_id(tg_user.id)

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        await show_folders()
        return

    try:
        # Вызываем метод для удаления папки
        result = await delete_all_items_in_folder(tg_user.id, current_folder_id)
        if result:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # Отправляем ответ в виде всплывающего уведомления
            # await call.answer(f"Запись удалена") #всплывающее сообщение сверху
            await call.answer(text=f"Все записи в папке удалены.", show_alert=True)
        else:
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить записи.'", show_alert=True)
        await show_folders()
    except MessageNotModified:
        await call.answer(text=f"Что то пошло не так при удалении записей.", show_alert=True)
        await show_folders()


@dp.message_handler(Text(equals="️✏️ Редактировать заголовок"))
async def edit_item_title_handler(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id')

    item: Item = await get_item(tg_user.id, item_id)
    if item.title and item.title != "":
        item_title = f"<b>{item.title}</b>"
    else:
        item_title = "[пусто]"

    edit_item_message_1 = await bot.send_message(message.chat.id, f"Текущий заголовок:",
                                                 reply_markup=ReplyKeyboardRemove())
    edit_item_message_2 = await bot.send_message(message.chat.id, f"{item_title}")

    await asyncio.sleep(0.5)

    buttons = [[add_none_title_item_button, cancel_edit_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)

    edit_item_message_3 = await bot.send_message(message.chat.id,
                                                 f"Придумайте новый заголовок:",
                                                 reply_markup=inline_markup)

    await dp.storage.update_data(user=tg_user, chat=message.chat,
                                 data={'edit_item_messages':
                                           (edit_item_message_1, edit_item_message_2, edit_item_message_3)})

    await states.Item.EditTitle.set()


@dp.message_handler(Text(equals="️📝 Редактировать текст"))
async def edit_item_text_handler(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id')

    item: Item = await get_item(tg_user.id, item_id)
    if item.text and item.text != "":
        item_text = item.text
    else:
        item_text = "[пусто]"

    edit_item_message_1 = await bot.send_message(message.chat.id, f"Текущий текст:",
                                                 reply_markup=ReplyKeyboardRemove())
    edit_item_message_2 = await bot.send_message(message.chat.id, f"{item_text}")

    await asyncio.sleep(0.5)

    buttons = [[cancel_edit_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)

    edit_item_message_3 = await bot.send_message(message.chat.id,
                                                 f"Напишите новый текст:",
                                                 reply_markup=inline_markup)

    await dp.storage.update_data(user=tg_user, chat=message.chat,
                                 data={'edit_item_messages':
                                           (edit_item_message_1, edit_item_message_2, edit_item_message_3)})

    await states.Item.EditText.set()


@dp.message_handler(state=[states.Item.EditTitle, states.Item.EditText])
async def edit_item_handler(message: aiogram.types.Message, state: FSMContext):
    await on_edit_item(message.text, state)


async def on_edit_item(edit_text, state: FSMContext):
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current(())
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    item_id = data.get('item_id')
    item: Item = await get_item(tg_user.id, item_id)
    current_state = await state.get_state()
    if current_state == states.Item.EditTitle.state:
        item.title = edit_text
        message_success_text = "Новый заголовок сохранен ✅"
        message_failure_text = "Что то пошло не так при сохранении заголовка ❌"
    else:
        item.text = edit_text
        message_success_text = "Новый текст сохранен ✅"
        message_failure_text = "Что то пошло не так при сохранении текста ❌"

    item.date_modified = datetime.now()

    result = await edit_item(tg_user.id, item_id, item)
    if result:
        sent_message = await bot.send_message(chat.id, message_success_text)
    else:
        sent_message = await bot.send_message(chat.id, message_failure_text)

    await asyncio.sleep(0.4)

    await state.reset_state()
    await show_item(item_id)



@dp.callback_query_handler(text_contains="cancel_edit_item",
                           state=[states.Item.EditTitle, states.Item.EditText])
async def cancel_edit_item(call: CallbackQuery, state: FSMContext):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=call.message.chat, user=tg_user)
    item_id = data.get('item_id')
    edit_item_messages = data.get('edit_item_messages')
    if edit_item_messages:
        for message in edit_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)

    await dp.storage.update_data(user=tg_user, chat=call.message.chat,
                                 data={'edit_item_messages': None})
    await state.reset_state()
    await show_item(item_id)


@dp.callback_query_handler(text_contains="add_none_title_item",
                           state=states.Item.EditTitle)
async def cancel_edit_item(call: CallbackQuery, state: FSMContext):
    await on_edit_item(None, state)