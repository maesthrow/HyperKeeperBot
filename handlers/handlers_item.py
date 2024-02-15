import asyncio
import copy

import aiogram
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, Message

from callbacks.callbackdata import SendItemCallback
from enums.enums import Environment
from handlers import states
from handlers.filters import NotInButtonsFilter, InButtonsFilter
from handlers.handlers_edit_item_title_text import on_edit_item
from handlers.handlers_folder import show_folders
from handlers.handlers_search import show_search_results
from handlers.handlers_settings import CURRENT_LABEL, get_inline_markup_with_selected_current_setting
from load_all import dp, bot
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_ import get_inline_markup_for_accept_cancel, get_environment
from utils.utils_button_manager import item_inline_buttons, item_inline_buttons_with_files, \
    cancel_edit_item_button, clean_title_buttons, clean_text_buttons, cancel_save_new_item_button, new_item_buttons, \
    without_title_button, add_to_item_button, FilesButtons, text_pages_buttons, get_text_pages_buttons
from utils.utils_data import get_current_folder_id, set_current_folder_id
from utils.utils_item_show_files import show_item_files
from utils.utils_items_db import util_add_item_to_folder, util_delete_item, util_delete_all_items_in_folder, \
    util_move_item
from utils.utils_items_reader import get_item, get_folder_id
from utils.utils_parse_mode_converter import to_markdown_text, preformat_text

#cancel_edit_item_button = InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_edit_item")

# choose_edit_item_content_buttons = [
#     InlineKeyboardButton(text="📝 Текст", callback_data=f"edit_content_text"),
#     InlineKeyboardButton(text="📸 Медиафайлы", callback_data=f"edit_content_media")
# ]
#
# choose_type_edit_item_buttons = [
#     InlineKeyboardButton(text="➕ Добавить", callback_data=f"new_text_type_add"),
#     InlineKeyboardButton(text="🔄 Перезаписать", callback_data=f"new_text_type_rewrite")
# ]
# add_none_title_item_button = InlineKeyboardButton(text="🪧 Пустой заголовок", callback_data=f"add_none_title_item")


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
    callback_data = callback_query.data.split('_')
    print(f'callback_data {callback_data}')
    item_id = callback_data[1]
    if len(callback_data) > 2 and callback_data[2] == 'with-folders':
        await show_folders(user_id, need_to_resend=True)

    await show_item(user_id, item_id)
    await callback_query.answer()


async def show_item(user_id, item_id, author_user_id=None):
    if not author_user_id:
        author_user_id = user_id
    item = await get_item(author_user_id, item_id)

    inline_markup = await get_item_inline_markup(author_user_id, item, page=0)
    message_text = item.get_body_markdown()
    bot_message = await bot.send_message(
        chat_id=user_id,
        text=message_text,
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    print(f"item {item}")
    #await show_item_files(user_id, item)

    data = await get_data(author_user_id)
    data['bot_message'] = bot_message
    data['item_id'] = item_id
    data['current_item'] = item
    data['current_inline_markup'] = inline_markup
    await set_data(author_user_id, data)


async def get_item_inline_markup(user_id, item: Item, page: int):
    if item.files_count() == 0:
        item_inlines = copy.deepcopy(item_inline_buttons)
    else:
        item_inlines = copy.deepcopy(item_inline_buttons_with_files)
        files_button: InlineKeyboardButton = FilesButtons.get_show_button(item.files_count())
        item_inlines[-1][-1] = files_button

    item_inlines[0][0].switch_inline_query = f"{user_id}_{item.id}"
    item_inlines[-1][0].switch_inline_query_current_chat = f"{user_id}_{item.id}_content"
    if len(item.text) > 1:
        item_inlines.insert(0, get_text_pages_buttons(user_id, item, page))

    return InlineKeyboardMarkup(row_width=2, inline_keyboard=item_inlines, resize_keyboard=True)


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


@router.message(states.Item.NewStepTitle, F.text == cancel_save_new_item_button.text)
async def cancel_add_new_item(message: Message, state: FSMContext):
    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message in add_item_messages:
            await bot.delete_message(message.chat.id, message.message_id)
            await asyncio.sleep(0.1)

    await state.clear()
    await show_folders(message.chat.id)


@router.message(states.Item.NewStepTitle, F.text == without_title_button.text)
async def skip_enter_item_title_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get('item')
    await on_create_new_item(state, item, message=message)


@router.message(states.Item.NewStepTitle, F.text == add_to_item_button.text)
async def skip_enter_item_title_handler(message: Message, state: FSMContext):
    await bot.send_message(message.chat.id, "Отправьте в сообщении то, чем хотите дополнить новую запись:")
    await state.update_data(file_messages=[])
    await state.set_state(states.Item.NewStepAdd)


@router.message(states.Item.NewStepTitle, NotInButtonsFilter(new_item_buttons))
async def new_item(message: aiogram.types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get('item')
    item.title = message.text #to_markdown_text(message.text, message.entities)
    await on_create_new_item(state, item, message=message)
    await bot.delete_message(message.chat.id, message.message_id)


async def on_create_new_item(state: FSMContext, item: Item, message: Message = None, call: CallbackQuery = None):
    user_id = message.from_user.id if message else call.from_user.id if call else 0
    current_folder_id = await get_current_folder_id(user_id)
    new_item_id = await util_add_item_to_folder(user_id, current_folder_id, item)

    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for message_del in add_item_messages:
            await bot.delete_message(message_del.chat.id, message_del.message_id)
            #await asyncio.sleep(0.2)
    # await asyncio.sleep(0.4)

    await state.clear()
    data = await state.get_data()

    if new_item_id:
        accept_add_item_message = await bot.send_message(chat_id=user_id, text="Новая запись успешно добавлена ✅")
        data['accept_add_item_message'] = accept_add_item_message
        await set_data(user_id, data)
        await asyncio.sleep(0.4)
        await show_folders(user_id, current_folder_id=current_folder_id, need_to_resend=False)
        await asyncio.sleep(0.2)
        await show_item(user_id, new_item_id)
    else:
        await bot.send_message(chat_id=user_id, text="Не получилось добавить запись ❌")
        # await asyncio.sleep(0.4)
        await show_folders(user_id, current_folder_id=current_folder_id, need_to_resend=True)


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
async def delete_all_items_handler(message: Message):
    current_folder_id = await get_current_folder_id(message.from_user.id)

    sent_message = await bot.send_message(message.chat.id, "⌛️")  # , reply_markup=ReplyKeyboardRemove())

    inline_markup = await get_inline_markup_for_accept_cancel(
        text_accept="Да, удалить", text_cancel="Не удалять",
        callback_data=f"delete_all_items_request")

    # await asyncio.sleep(0.5)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(message.chat.id,
                           f"Действительно хотите удалить все записи в этой папке?",
                           reply_markup=inline_markup)

    await bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)


@router.callback_query(F.data.contains("delete_all_items_request"))
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
        print(f"result {result}")
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


@router.message(states.Item.EditTitle, NotInButtonsFilter(clean_title_buttons + [cancel_edit_item_button]))
@router.message(states.Item.EditText, NotInButtonsFilter(clean_text_buttons + [cancel_edit_item_button]))
async def edit_item_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    message_text = message.text if message.text else ""
    format_message_text = preformat_text(message_text, message.entities)
    await on_edit_item(user_id, format_message_text, state)
    await show_folders(user_id, need_to_resend=True)
    await show_item(user_id, item_id)


@router.message(states.Item.EditTitle, InButtonsFilter(clean_title_buttons))
@router.message(states.Item.EditText, InButtonsFilter(clean_text_buttons))
async def add_none_title_or_text_item_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await on_edit_item(user_id, "", state)
    data = await get_data(user_id)
    item_id = data.get('item_id')
    await show_folders(user_id, need_to_resend=True)
    await show_item(user_id, item_id)


@router.message(states.Item.EditTitle, F.text == cancel_edit_item_button.text)
@router.message(states.Item.EditText, F.text == cancel_edit_item_button.text)
async def cancel_edit_item(message: Message, state: FSMContext):
    user_id = message.from_user.id
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


@router.callback_query(SendItemCallback.filter())
async def send_item_handler(call: CallbackQuery, callback_data: SendItemCallback):
    print("send_item_handler")
    user_id = call.from_user.id
    author_user_id = callback_data.author_user_id
    item_id = callback_data.item_id
    await show_item(user_id=user_id, author_user_id=author_user_id, item_id=item_id)



