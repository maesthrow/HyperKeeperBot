import asyncio

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from callbacks.callbackdata import EditFolderCallback, StatisticFolderHandler, MessageBoxCallback, \
    SearchInFolderHandler, PinFolderHandler, PinKeyboardNumberHandler
from handlers import states
from load_all import dp, bot
from utils.data_manager import get_data, set_data
from utils.utils_ import get_folder_name, smile_folder, get_inline_markup_for_accept_cancel, smile_item, get_folder_pin
from utils.utils_button_manager import cancel_button, create_general_reply_markup, general_buttons_search_items, \
    get_folder_pin_inline_markup
from utils.utils_folders import get_folder_statistic
from utils.utils_folders_writer import set_pin_folder
from utils.utils_items_reader import get_folder_items

router = Router()
dp.include_router(router)


@router.callback_query(EditFolderCallback.filter())
async def edit_folder_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data = EditFolderCallback.unpack(call.data)
    folder_id = call_data.folder_id
    folder_name = await get_folder_name(user_id, folder_id)
    action = call_data.action
    if action == 'rename':
        await edit_folder_name_handler(user_id, folder_id, folder_name, state)
    elif action == 'delete':
        await delete_folder_handler(user_id, folder_id, folder_name)
    elif action == 'delete_all_items':
        await delete_all_items_handler(user_id, folder_id, folder_name)
    await call.answer()


async def edit_folder_name_handler(user_id, folder_id, folder_name, state: FSMContext):
    data = await get_data(user_id)
    data['folder_id'] = folder_id
    await set_data(user_id, data)

    general_buttons = [[cancel_button]]
    markup = create_general_reply_markup(general_buttons)

    question_messages = data.get('question_messages', [])
    question_messages.append(
        await bot.send_message(
            chat_id=user_id,
            text=f"*Переименовать папку* {smile_folder}"
                 f"\n\nМожете скопировать текущее название:"
                 f"\n'`{folder_name}`'"
                 f"\n\n_Напишите новое название папки:_",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=markup
        )
    )
    await state.update_data(question_messages=question_messages)
    await state.set_state(states.Folder.EditName)


async def delete_folder_handler(user_id, folder_id, folder_name):
    inline_markup = get_inline_markup_for_accept_cancel(
        "✔️Да, удалить",
        "✖️Не удалять",
        f"delete_folder_request_{folder_id}")

    await bot.send_message(user_id,
                           f"Хотите удалить папку {smile_folder} '{folder_name}' и все ее содержимое?",
                           reply_markup=inline_markup)


async def delete_all_items_handler(user_id, folder_id, folder_name):
    count_items = len(await get_folder_items(user_id, folder_id))
    if not count_items:
        sent_message = await bot.send_message(user_id, "В этой папке нет записей.")
        await asyncio.sleep(1)
        await bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    else:
        inline_markup = get_inline_markup_for_accept_cancel(
            text_accept="✔️Да, удалить", text_cancel="✖️Не удалять",
            callback_data=f"delete_all_items_request")
        await bot.send_message(user_id,
                               f"Действительно хотите удалить все записи ({count_items}) в папке "
                               f"{smile_folder} {folder_name} ?",
                               reply_markup=inline_markup)


@router.callback_query(StatisticFolderHandler.filter())
async def statistic_handler(call: CallbackQuery):
    user_id = call.from_user.id
    call_data = StatisticFolderHandler.unpack(call.data)
    folder_id = call_data.folder_id
    folder_name = await get_folder_name(user_id, folder_id)
    dict_folder_statistic = await get_folder_statistic(user_id, folder_id)
    folders_count = dict_folder_statistic['folders_count']
    items_count = dict_folder_statistic['items_count']
    deep_folders_count = dict_folder_statistic['deep_folders_count']
    deep_items_count = dict_folder_statistic['deep_items_count']
    statistic_text = (f"<u>Количество папок</u> {smile_folder}: <b>{folders_count}</b>\n"
                      f"<u>Количество записей</u> {smile_item}: <b>{items_count}</b>\n\n"
                      f"<b>С учетом вложенных папок:</b>\n"
                      f"<u>Всего папок</u> {smile_folder}: <b>{deep_folders_count}</b>\n"
                      f"<u>Всего записей</u> {smile_item}: <b>{deep_items_count}</b>")

    # general_buttons = general_buttons_statistic_folder[:]
    # markup = create_general_reply_markup(general_buttons)
    inline_markup = get_ok_inline_markup()
    await bot.send_message(user_id, f"📊 <b>Статистика папки</b>\n"
                                            f"{smile_folder} {folder_name}:\n\n"
                                            f"{statistic_text}",
                           reply_markup=inline_markup)

    # data = await get_data(user_id)
    # data['current_keyboard'] = markup
    # await set_data(user_id, data)
    await call.answer()


def get_ok_inline_markup():
    inline_markup = (
        InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text='☑️ OK', callback_data=MessageBoxCallback(result='ok').pack())  # ☑️ ✔️
            ]])
    )
    return inline_markup

@router.callback_query(SearchInFolderHandler.filter())
async def search_in_folder_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data = SearchInFolderHandler.unpack(call.data)
    folder_id = call_data.folder_id
    await search_in_folder(user_id, state)
    await call.answer()


async def search_in_folder(user_id, state):
    data = await get_data(user_id)
    data['dict_search_data'] = None
    await set_data(user_id, data)

    general_buttons = [general_buttons_search_items[-1]]
    markup = create_general_reply_markup(general_buttons)
    search_message = await bot.send_message(user_id, "Введите текст для поиска 🔍", reply_markup=markup)
    await state.set_state(states.Item.Search)
    await state.update_data(search_message=search_message)


@router.callback_query(PinFolderHandler.filter())
async def pin_folder_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data = PinFolderHandler.unpack(call.data)
    folder_id = call_data.folder_id
    folder_name = await get_folder_name(user_id, folder_id)
    pin = await get_folder_pin(user_id, folder_id)
    inline_markup = get_folder_pin_inline_markup(user_id, folder_id)
    if not pin:
        await bot.send_message(
            chat_id=user_id,
            text=f'Придумайте PIN-код для папки\n{smile_folder} {folder_name}:\n\n➖ ➖ ➖ ➖',
            reply_markup=inline_markup
        )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=f'Введите текущий PIN-код для папки\n{smile_folder} {folder_name}:\n\n➖ ➖ ➖ ➖',
            reply_markup=inline_markup
        )
    data = await get_data(user_id)
    data['enter_pin'] = ''
    await set_data(user_id, data)
    await call.answer()


@router.callback_query(PinKeyboardNumberHandler.filter())
async def number_pin_folder_handler(call: CallbackQuery, state: FSMContext):
    message_text = call.message.text
    inline_markup = call.message.reply_markup
    user_id = call.from_user.id

    data = await get_data(user_id)
    enter_pin = data['enter_pin']

    call_data = PinKeyboardNumberHandler.unpack(call.data)
    folder_id = call_data.folder_id
    number = call_data.number
    pin_str = message_text.split('\n')[-1]
    numbers = pin_str.split()
    for char in numbers:
        if char == '➖':
            enter_pin += str(number)
            message_text = call.message.text.replace('➖', '🔘', 1)
            await bot.edit_message_text(
                text=message_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
            )
            await asyncio.sleep(0.4)
            break
    if message_text.find('➖') < 0:
        message_text = 'PIN-код установлен ✅'
        await set_pin_folder(user_id, folder_id, enter_pin)
        data['enter_pin'] = None
        inline_markup = get_ok_inline_markup()
        await bot.edit_message_text(
            text=message_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )
    else:
        data['enter_pin'] = enter_pin
    await set_data(user_id, data)
    await call.answer()


