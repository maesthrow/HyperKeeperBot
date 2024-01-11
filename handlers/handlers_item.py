import asyncio
from datetime import datetime

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, User, Chat, \
    KeyboardButton
from aiogram.utils.exceptions import MessageNotModified

from enums.enums import Environment
from handlers import states
from utils.utils_ import get_inline_markup_for_accept_cancel, get_environment
from utils.utils_button_manager import create_general_reply_markup, general_buttons_item
from firebase.firebase_item_reader import get_item, get_folder_id
from handlers.handlers_folder import show_folders
from handlers.handlers_search import show_search_results
from load_all import dp, bot
from models.item_model import Item
from utils.utils_data import get_current_folder_id, set_current_folder_id
from utils.utils_items_db import util_add_item_to_folder, util_delete_item, util_delete_all_items_in_folder, \
    util_edit_item, \
    util_move_item

cancel_edit_item_button = InlineKeyboardButton("Отменить", callback_data=f"cancel_edit_item")
add_none_title_item_button = InlineKeyboardButton("Пустой заголовок", callback_data=f"add_none_title_item")


# Обработчик для ответа на нажатие кнопки
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('item_'))
async def show_item_button(callback_query: CallbackQuery):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(user=tg_user, chat=chat)
    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        current_folder_id = await get_current_folder_id()
        await movement_item_handler(callback_query.message, current_folder_id)
        return

    # Получаем item_id из callback_data
    item_id = callback_query.data.split('_')[1]
    await show_item(item_id)


async def show_item(item_id):
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    item = await get_item(item_id)

    data = await dp.storage.get_data(chat=chat, user=tg_user)

    # ВСПЛЫВАЮЩЕЕ СООБЩЕНИЕ!!!
    # await callback_query.answer(f"{item.title}\n{item.text}")

    buttons = general_buttons_item[:]
    if data['dict_search_data']:
        buttons.pop(len(buttons) - 1)

        search_mode_buttons = [
            [KeyboardButton("️🗂️ Перейти к папке текущей записи")],
            [KeyboardButton("️↩️ К результатам поиска 🔎"), KeyboardButton("🔄 Новый поиск 🔍️")],
            [KeyboardButton("🫡 Завершить режим поиска 🔍️")]
        ]
        buttons.extend(search_mode_buttons)

        search_text = data['dict_search_data'].get('search_text', None)
        if search_text:
            item.select_search_text(search_text)

    markup = create_general_reply_markup(buttons)

    if item.title:
        item_content = f"📄 <b>{item.title}</b>\n\n{item.text}"
    else:
        item_content = f"📄\n\n{item.text}"

    bot_message = await bot.send_message(tg_user.id, item_content, reply_markup=markup)
    # await dp.storage.update_data(user=tg_user, chat=chat, data={'current_keyboard': markup})

    data = await dp.storage.get_data(user=tg_user, chat=chat)
    data['bot_message'] = bot_message
    data['item_id'] = item_id
    data['current_keyboard'] = markup
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)


@dp.message_handler(Text(equals="️↩️ Назад к папке"))
async def back_to_folder(message: aiogram.types.Message):
    tg_user = User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id', None)
    if item_id:
        folder_id = get_folder_id(item_id)
    else:
        folder_id = await get_current_folder_id()
    await show_folders(folder_id, need_to_resend=True)


@dp.message_handler(Text(equals="️↩️ К результатам поиска 🔎"))
async def back_to_search_results(message: aiogram.types.Message):
    data = await dp.storage.get_data(chat=Chat.get_current(), user=User.get_current())
    await show_search_results(data['dict_search_data'])


@dp.message_handler(Text(equals="️🗂️ Перейти к папке текущей записи"))
async def back_to_folder(message: aiogram.types.Message):
    data = await dp.storage.get_data(chat=Chat.get_current(), user=User.get_current())
    item_id = data['item_id']
    folder_id = get_folder_id(item_id)
    data['dict_search_data'] = None
    await dp.storage.update_data(user=User.get_current(), chat=Chat.get_current(), data=data)
    await show_folders(folder_id, need_to_resend=True)


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
    await on_add_new_item(item, call.message, state)


@dp.message_handler(state=states.Item.NewStepTitle)
async def new_item(message: aiogram.types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    item.title = message.text
    await on_add_new_item(item, message, state)


async def on_add_new_item(item: Item, message: aiogram.types.Message, state: FSMContext):
    current_folder_id = await get_current_folder_id()
    new_item_id = await util_add_item_to_folder(current_folder_id, item)

    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message_del in add_item_messages:
            await bot.delete_message(message_del.chat.id, message_del.message_id)
            await asyncio.sleep(0.2)
    #await asyncio.sleep(0.4)

    await state.reset_data()
    await state.reset_state()

    if new_item_id:
        await bot.send_message(message.chat.id, "Новая запись успешно добавлена ✅")
        await asyncio.sleep(0.5)
        await show_folders(need_to_resend=False)
        await asyncio.sleep(0.2)
        await show_item(new_item_id)
    else:
        await bot.send_message(message.chat.id, "Не получилось добавить запись ❌")
        # await asyncio.sleep(0.4)
        await show_folders(need_to_resend=True)


@dp.message_handler(Text(equals="🗑 Удалить"))
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


@dp.callback_query_handler(text_contains="delete_item_request")
async def delete_item_request(call: CallbackQuery):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=call.message.chat, user=tg_user)
    item_id = data.get('item_id')

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        #await show_item(item_id)
        return

    try:
        # Вызываем метод для удаления папки
        result = await util_delete_item(item_id)
        if result:
            await bot.send_message(call.message.chat.id,
                                   f"Запись удалена ☑️")  # , reply_markup=inline_markup)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            #await call.answer(text=f"Запись удалена ☑️", show_alert=True)

            await asyncio.sleep(0.4)
            folder_id = await get_current_folder_id()
            await show_folders(current_folder_id=folder_id, need_to_resend=True)
            item_message = data.get('bot_message', None)
            if item_message:
                await bot.delete_message(chat_id=item_message.chat.id, message_id=item_message.message_id)
        else:
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить запись.'", show_alert=True)

    except MessageNotModified:
        await call.answer(text=f"Что то пошло не так при удалении записи.", show_alert=True)
        #await show_folders(need_to_resend=True)


@dp.message_handler(Text(equals="️🧹 Удалить все записи в папке"))
async def delete_all_items_handler(message: aiogram.types.Message):
    current_folder_id = await get_current_folder_id()

    sent_message = await bot.send_message(message.chat.id, "⌛️") #, reply_markup=ReplyKeyboardRemove())

    inline_markup = await get_inline_markup_for_accept_cancel(
        text_accept="Да, удалить", text_cancel="Не удалять",
        callback_data=f"delete_all_items_request_{current_folder_id}")

    # await asyncio.sleep(0.5)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(message.chat.id,
                           f"Действительно хотите удалить все записи в этой папке?",
                           reply_markup=inline_markup)

    await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@dp.callback_query_handler(text_contains="delete_all_items_request")
async def delete_all_items_request(call: CallbackQuery):
    tg_user = User.get_current()
    current_folder_id = await get_current_folder_id()

    if "cancel" in call.data:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        #await show_folders()
        return

    try:
        # Вызываем метод для удаления папки
        result = await util_delete_all_items_in_folder(current_folder_id)
        if result:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            # Отправляем ответ в виде всплывающего уведомления
            # await call.answer(f"Запись удалена") #всплывающее сообщение сверху
            #await call.answer(text=f"Все записи в папке удалены.", show_alert=True)
        else:
            # Отправляем ответ в виде всплывающего уведомления
            await call.answer(text=f"Не получилось удалить записи.'", show_alert=True)
        await show_folders(need_to_resend=False)
    except MessageNotModified:
        await call.answer(text=f"Что то пошло не так при удалении записей.", show_alert=True)
        await show_folders(need_to_resend=False)


@dp.message_handler(Text(equals="️✏️ Редактировать заголовок"))
async def edit_item_title_handler(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id')

    item: Item = await get_item(item_id)
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

    data = await dp.storage.get_data(user=tg_user, chat=message.chat)
    data['edit_item_messages'] = (edit_item_message_1, edit_item_message_2, edit_item_message_3)
    await dp.storage.update_data(user=tg_user, chat=message.chat, data=data)

    await states.Item.EditTitle.set()


@dp.message_handler(Text(equals="️📝 Редактировать текст"))
async def edit_item_text_handler(message: aiogram.types.Message):
    tg_user = aiogram.types.User.get_current()
    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id')

    item: Item = await get_item(item_id)
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

    data = await dp.storage.get_data(user=tg_user, chat=message.chat)
    data['edit_item_messages'] = (edit_item_message_1, edit_item_message_2, edit_item_message_3)
    await dp.storage.update_data(user=tg_user, chat=message.chat, data=data)

    await states.Item.EditText.set()


@dp.message_handler(state=[states.Item.EditTitle, states.Item.EditText])
async def edit_item_handler(message: aiogram.types.Message, state: FSMContext):
    await on_edit_item(message.text, state)


async def on_edit_item(edit_text, state: FSMContext):
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current(())
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    item_id = data.get('item_id')
    item: Item = await get_item(item_id)
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

    result = await util_edit_item(item_id, item)
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
    tg_user = User.get_current()
    data = await dp.storage.get_data(chat=call.message.chat, user=tg_user)
    item_id = data.get('item_id')
    edit_item_messages = data.get('edit_item_messages')
    if edit_item_messages:
        for message in edit_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)

    data['edit_item_messages'] = None
    await dp.storage.update_data(user=tg_user, chat=call.message.chat, data=data)
    await state.reset_state()
    await show_item(item_id)


@dp.callback_query_handler(text_contains="add_none_title_item",
                           state=states.Item.EditTitle)
async def cancel_edit_item(call: CallbackQuery, state: FSMContext):
    await on_edit_item(None, state)


@dp.message_handler(Text(equals="️🔀 Переместить"))
async def movement_item_handler(message: aiogram.types.Message, folder_id=None):
    tg_user = User.get_current()

    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    item_id = data.get('item_id')
    if not data.get('movement_item_id'):
        data['movement_item_id'] = item_id
        await dp.storage.update_data(user=tg_user, chat=message.chat, data=data)

    message_text = "❗Вы не завершили перемещение❗\n" if folder_id else ""
    message_text += f"Выберите папку, в которую хотите переместить запись ⬇️"
    await bot.send_message(message.chat.id, message_text)
    await asyncio.sleep(0.5)

    if not folder_id:
        folder_id = get_folder_id(item_id)
    await show_folders(folder_id)


@dp.message_handler(Text(equals="️🚫 Отменить перемещение"))
async def movement_item_cancel(message: aiogram.types.Message, folder_id=None):
    tg_user = User.get_current()

    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    movement_item_id = data.get('movement_item_id')
    data['movement_item_id'] = None
    await dp.storage.update_data(user=tg_user, chat=message.chat, data=data)

    message_text = f"Перемещение записи отменено 🚫"
    await bot.send_message(message.chat.id, message_text)
    await asyncio.sleep(0.4)

    folder_id = get_folder_id(movement_item_id)
    await set_current_folder_id(folder_id)
    await show_folders(folder_id)
    await asyncio.sleep(0.2)
    await show_item(movement_item_id)


@dp.message_handler(Text(equals="🔀 Переместить в текущую папку"))
async def movement_item_execute(message: aiogram.types.Message, folder_id=None):
    tg_user = User.get_current()

    data = await dp.storage.get_data(chat=message.chat, user=tg_user)
    movement_item_id = data.get('movement_item_id')
    data['movement_item_id'] = None
    await dp.storage.update_data(user=tg_user, chat=message.chat, data=data)

    folder_id = await get_current_folder_id()
    new_movement_item_id = await util_move_item(movement_item_id, folder_id)
    if new_movement_item_id:
        movement_item_id = new_movement_item_id
        message_text = f"Запись была перемещена ✅"
    else:
        folder_id = get_folder_id(movement_item_id)
        message_text = f"Не удалось переместить запись ❌"

    await bot.send_message(message.chat.id, message_text)
    await asyncio.sleep(0.4)
    await show_folders(folder_id)
    await asyncio.sleep(0.2)
    await show_item(movement_item_id)


@dp.message_handler(Text(equals="🫡 Завершить режим поиска 🔍️"))
async def search_item_handler(message: aiogram.types.Message):
    data = await dp.storage.get_data(user=User.get_current(), chat=Chat.get_current())
    data['dict_search_data'] = None
    await dp.storage.update_data(user=User.get_current(), chat=Chat.get_current(), data=data)

    environment: Environment = await get_environment()
    if environment is Environment.FOLDERS:
        await show_folders()
    elif environment is Environment.ITEM_CONTENT:
        item_id = data.get('item_id')
        if item_id:
            current_folder = get_folder_id(item_id)
            await set_current_folder_id(current_folder)
            await show_item(item_id)
