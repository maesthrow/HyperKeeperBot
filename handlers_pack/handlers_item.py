import asyncio
import copy

import aiogram
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

from callbacks.callbackdata import SendItemCallback, ItemShowCallback, MarkFileCallback, BackToStandardFolderView
from handlers_pack import states
from handlers_pack.filters import NotInButtonsFilter, InButtonsFilter
from handlers_pack.handlers_edit_item_title_text import edit_item
from handlers_pack.handlers_folder import show_folders
from handlers_pack.handlers_search import show_search_results
from load_all import dp, bot
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.message_box import MessageBox
from utils.utils_ import update_message_reply_markup
from utils.utils_button_manager import item_inline_buttons, item_inline_buttons_with_files, \
    complete_edit_item_button, clean_title_buttons, clean_text_buttons, cancel_save_new_item_button, \
    general_new_item_buttons, \
    without_title_button, add_to_item_button, FilesButtons, get_text_pages_buttons, \
    create_general_reply_markup, general_add_to_new_item_mode_buttons, cancel_add_mode_button, \
    general_buttons_edit_item_files, get_delete_files_inline_markup
from utils.utils_data import get_current_folder_id, set_current_folder_id
from utils.utils_items_db import util_add_item_to_folder, util_delete_all_items_in_folder, \
    util_move_item
from utils.utils_items_reader import get_item, get_folder_id
from utils.utils_parse_mode_converter import preformat_text
from utils.utils_show_item_entities import show_item_full_mode

# cancel_edit_item_button = InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_edit_item")

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
# @router.callback_query(lambda c: c.data and c.data.startswith('item_'))
@router.callback_query(ItemShowCallback.filter())
async def show_item_button(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    data = await get_data(user_id)
    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    if movement_item_id:
        current_folder_id = await get_current_folder_id(user_id)
        await movement_item_message_handler(callback_query.message, current_folder_id)
        await callback_query.answer()
        return

    call_data: ItemShowCallback = ItemShowCallback.unpack(callback_query.data)
    author_user_id = call_data.author_user_id
    item_id = call_data.item_id
    with_folders = call_data.with_folders

    if user_id == author_user_id:
        if with_folders:
            await show_folders(user_id, need_to_resend=True)
        await show_item(user_id, item_id)
    else:
        await show_item_full_mode(user_id, item_id, author_user_id)

    await callback_query.answer()


async def show_item(user_id, item_id, author_user_id=None, page=0):
    if not author_user_id:
        author_user_id = user_id
    item = await get_item(author_user_id, item_id)

    inline_markup = await get_item_inline_markup(user_id, author_user_id, item, page=page)
    message_text = item.get_body_markdown(page)
    if item.files_count() > 0:
        message_text = f'{message_text}\n_{item.get_files_statistic_text()}_'
    bot_message = await bot.send_message(
        chat_id=user_id,
        text=message_text,
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )

    # print(f"item {item}")
    # await show_item_files(user_id, item)

    data = await get_data(author_user_id)
    data['bot_message'] = bot_message
    data['item_id'] = item_id
    data['current_item'] = item
    data['current_inline_markup'] = inline_markup
    await set_data(author_user_id, data)


async def get_item_inline_markup(user_id, author_user_id, item: Item, page: int):
    if item.files_count() == 0:
        item_inlines = copy.deepcopy(item_inline_buttons)
        if user_id != author_user_id:
            item_inlines = [item_inline_buttons[0]]
    else:
        item_inlines = copy.deepcopy(item_inline_buttons_with_files)
        if user_id != author_user_id:
            item_inlines.pop(1)
        files_button: InlineKeyboardButton = FilesButtons.get_show_button(item.files_count())
        item_inlines[-1][-1] = files_button

    item_inlines[0][0].switch_inline_query = f"browse_{author_user_id}_{item.id}_{-1}"
    item_inlines[-1][0].switch_inline_query_current_chat = f"browse_{author_user_id}_{item.id}_{-1}_content"
    if item.pages_count() > 1:
        item_inlines.insert(0, get_text_pages_buttons(author_user_id, item, page))

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


@router.message(states.ItemState.NewStepTitle, F.text == cancel_save_new_item_button.text)
@router.message(states.ItemState.NewStepAdd, F.text == cancel_save_new_item_button.text)
@router.message(states.ItemState.ChooseTypeAddTextToNewItem, F.text == cancel_save_new_item_button.text)
async def cancel_add_new_item(message: Message, state: FSMContext):
    data = await state.get_data()
    add_item_messages = data.get('add_item_messages')
    if add_item_messages:
        for add_message in add_item_messages:
            add_message: Message = add_message
            if add_message.from_user.id == bot.id:
                await bot.delete_message(add_message.chat.id, add_message.message_id)
                await asyncio.sleep(0.1)

    await bot.delete_message(message.chat.id, message.message_id)
    await state.set_state()
    await state.update_data(add_item_messages=[], text_messages=[], item=None)
    await show_folders(message.from_user.id, need_to_resend=True)


@router.message(states.ItemState.NewStepAdd, F.text == cancel_add_mode_button.text)
@router.message(states.ItemState.ChooseTypeAddTextToNewItem, F.text == cancel_add_mode_button.text)
@router.message(states.ItemState.ChooseTypeAddText, F.text == cancel_add_mode_button.text)
async def cancel_add_mode_on_new_item(message: Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get('item', None)

    state_data = await state.get_data()
    add_item_messages = state_data.get('add_item_messages', [])

    markup = create_general_reply_markup(general_new_item_buttons)
    add_item_messages.append(
        await bot.send_message(
            chat_id=message.chat.id,
            text="<i>Напишите заголовок или выберите действие на клавиатуре:</i>",
            reply_markup=markup
        )
    )

    await state.update_data(item=item, add_item_messages=add_item_messages)
    await state.set_state(states.ItemState.NewStepTitle)


@router.message(states.ItemState.NewStepTitle, F.text == without_title_button.text)
async def skip_enter_item_title_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get('item', None)
    await on_create_new_item(state, item, message=message)


@router.message(states.ItemState.NewStepTitle, F.text == add_to_item_button.text)
async def add_to_new_item_handler(message: Message, state: FSMContext):
    markup = create_general_reply_markup(general_add_to_new_item_mode_buttons)
    await bot.send_message(
        chat_id=message.chat.id,
        text="<i>Отправьте в сообщении то, чем хотите дополнить новую запись:</i>",
        reply_markup=markup
    )
    await state.update_data(file_messages=[], text_messages=[])
    await state.set_state(states.ItemState.NewStepAdd)


@router.message(states.ItemState.NewStepTitle, NotInButtonsFilter(general_new_item_buttons))
async def new_item(message: aiogram.types.Message, state: FSMContext):
    data = await state.get_data()
    item: Item = data.get('item', None)
    if item:
        item.title = message.text.strip()  # to_markdown_text(message.text, message.entities)
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
            try:
                await bot.delete_message(message_del.chat.id, message_del.message_id)
            except:
                pass

    await state.clear()
    data = await state.get_data()

    if new_item_id:
        #accept_add_item_message = await bot.send_message(chat_id=user_id, text="Новая запись успешно добавлена ✅")
        #data['accept_add_item_message'] = accept_add_item_message
        #await set_data(user_id, data)
        #await asyncio.sleep(0.4)
        await show_folders(user_id, current_folder_id=current_folder_id, need_to_resend=False)
        await asyncio.sleep(0.2)
        await show_item(user_id, new_item_id)
        await asyncio.sleep(0.2)
        if call:
            await call.answer("Новая запись успешно добавлена ✅")
        #await MessageBox.show(user_id, "Новая запись успешно добавлена ✅")
    else:
        await show_folders(user_id, current_folder_id=current_folder_id, need_to_resend=True)
        await asyncio.sleep(0.2)
        await MessageBox.show(user_id, "Не получилось добавить запись ❌")


# @router.message(F.text == "️🧹 Удалить все записи в папке")
# async def delete_all_items_handler(message: Message):
#     current_folder_id = await get_current_folder_id(message.from_user.id)
#     count_items = len(await get_folder_items(message.from_user.id, current_folder_id))
#     if not count_items:
#         sent_message = await bot.send_message(message.chat.id, "В этой папке нет записей.")
#         await asyncio.sleep(1)
#         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#         await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
#     else:
#         inline_markup = get_inline_markup_for_accept_cancel(
#             text_accept="✔️Да, удалить", text_cancel="✖️Не удалять",
#             callback_data=f"delete_all_items_request")
#         await bot.send_message(message.chat.id,
#                                f"Действительно хотите удалить все записи ({count_items}) в этой папке?",
#                                reply_markup=inline_markup)
#         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


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
            data = await get_data(user_id)
            bot_message = data.get('bot_message', None)
            if bot_message:
                try:
                    await bot.delete_message(user_id, bot_message.message_id)
                except:
                    pass
                data['bot_message'] = None
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


@router.message(states.ItemState.EditTitle, NotInButtonsFilter(clean_title_buttons + [complete_edit_item_button]))
@router.message(states.ItemState.EditText, NotInButtonsFilter(clean_text_buttons + [complete_edit_item_button]))
async def edit_item_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    message_text = message.text if message.text else ""
    format_message_text = preformat_text(message_text, message.entities)
    await do_edit_item(user_id, item_id, state, edit_text=format_message_text)


@router.message(states.ItemState.EditTitle, InButtonsFilter(clean_title_buttons))
@router.message(states.ItemState.EditText, InButtonsFilter(clean_text_buttons))
async def add_none_title_or_text_item_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    await do_edit_item(user_id, item_id, state, edit_text=None)


async def do_edit_item(user_id, item_id, state, edit_text):
    await edit_item(user_id, state, edit_text)
    state_data = await state.get_data()
    text_page = state_data.get('item_text_page', 0)
    await state.set_state(state=None)
    await show_folders(user_id, need_to_resend=True)
    await show_item(user_id, item_id, page=text_page)


@router.message(states.ItemState.EditTitle, F.text == complete_edit_item_button.text)
@router.message(states.ItemState.EditText, F.text == complete_edit_item_button.text)
@router.message(states.ItemState.EditFiles, F.text == complete_edit_item_button.text)
@router.message(states.ItemState.EditFileCaption, F.text == complete_edit_item_button.text)
async def cancel_edit_item(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await on_cancel_edit_item(user_id, state)


async def on_cancel_edit_item(user_id, state: FSMContext):
    data = await get_data(user_id)
    item_id = data.get('item_id')
    edit_item_messages = data.get('edit_item_messages')
    if edit_item_messages:
        for item_message in edit_item_messages:
            await bot.delete_message(item_message.chat.id, item_message.message_id)

    data['edit_item_messages'] = None
    await set_data(user_id, data)
    await state.set_state()
    await show_folders(user_id, need_to_resend=True)
    await show_item(user_id, item_id)


@router.message(states.ItemState.EditFiles, F.text == general_buttons_edit_item_files[0][0].text)
@router.message(states.ItemState.EditFiles, F.text == general_buttons_edit_item_files[0][1].text)
async def mark_all_edit_files_handler(message: Message, state: FSMContext):
    mark = message.text == general_buttons_edit_item_files[0][0].text
    user_id = message.from_user.id
    data = await get_data(user_id)
    edit_file_messages = data.get('edit_file_messages')
    delete_file_ids = data.get('delete_file_ids')
    tasks = []
    for index, file_message in enumerate(edit_file_messages):
        task = update_message_reply_markup(user_id, delete_file_ids, file_message, mark)
        tasks.append(task)

    await asyncio.gather(*tasks)
    await bot.delete_message(user_id, message.message_id)


@router.message(states.ItemState.EditFiles, F.text == general_buttons_edit_item_files[1][0].text)
async def delete_marked_edit_files_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    edit_file_messages = data.get('edit_file_messages')
    delete_file_ids = data.get('delete_file_ids')
    delete_count = 0
    call_data = None
    for index, file_message in enumerate(edit_file_messages):
        inline_markup = file_message.reply_markup
        mark_button = inline_markup.inline_keyboard[-1][0]
        call_data = MarkFileCallback.unpack(mark_button.callback_data)
        if call_data.file_id in delete_file_ids and delete_file_ids[call_data.file_id][1]:
            delete_count += 1

    if delete_count:
        inline_markup = get_delete_files_inline_markup(call_data.item_id)
        await bot.send_message(user_id, f'Хотите удалить {delete_count} выбранных файлов?', reply_markup=inline_markup)
    else:
        info_message = await bot.send_message(user_id, f'Ничего не выбрано')
        await asyncio.sleep(1)
        await bot.delete_message(chat_id=user_id, message_id=info_message.message_id)

    await bot.delete_message(chat_id=user_id, message_id=message.message_id)


@router.message(states.ItemState.EditFiles, F.text == general_buttons_edit_item_files[1][1].text)
async def delete_all_marked_edit_files_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    edit_file_messages = data.get('edit_file_messages')
    file_message = edit_file_messages[0]
    inline_markup = file_message.reply_markup
    mark_button = inline_markup.inline_keyboard[-1][0]
    call_data = MarkFileCallback.unpack(mark_button.callback_data)
    inline_markup = get_delete_files_inline_markup(call_data.item_id, is_all=True)
    await bot.send_message(user_id, f'Хотите удалить все файлы?', reply_markup=inline_markup)
    await bot.delete_message(chat_id=user_id, message_id=message.message_id)


@router.message(F.text == "️🔀 Переместить")
async def movement_item_message_handler(message: aiogram.types.Message, folder_id=None):
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


@router.callback_query(SendItemCallback.filter())
async def send_item_handler(call: CallbackQuery, callback_data: SendItemCallback):
    #print("send_item_handler")
    user_id = call.from_user.id
    author_user_id = callback_data.author_user_id
    item_id = callback_data.item_id
    await show_item(user_id=user_id, author_user_id=author_user_id, item_id=item_id)


@router.callback_query(BackToStandardFolderView.filter())
async def send_item_handler(call: CallbackQuery):
    call_data = BackToStandardFolderView.unpack(call.data)
    user_id = call.from_user.id
    current_folder_id = await get_current_folder_id(user_id)
    await show_folders(
        user_id,
        current_folder_id,
        page_folder=call_data.page_folder,
        page_item=call_data.page_item,
        need_to_resend=False
    )
