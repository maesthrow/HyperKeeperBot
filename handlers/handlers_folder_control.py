import asyncio
import copy
import re

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import EditFolderCallback, StatisticFolderCallback, MessageBoxCallback, \
    SearchInFolderCallback, PinFolderCallback, PinKeyboardNumberCallback, PinKeyboardButtonCallback, \
    NewPinCodeButtonCallback, EnterPinCodeButtonCallback
from handlers import states
from handlers.handlers_folder import show_folders
from load_all import dp, bot
from models.folder_model import Folder
from models.item_model import INVISIBLE_CHAR
from utils.data_manager import get_data, set_data
from utils.utils_ import get_folder_name, smile_folder, get_inline_markup_for_accept_cancel, smile_item, get_folder_pin
from utils.utils_button_manager import cancel_button, create_general_reply_markup, general_buttons_search_items, \
    get_folder_pin_inline_markup, get_pin_control_inline_markup
from utils.utils_constants import numbers_ico
from utils.utils_folders import get_folder_statistic
from utils.utils_folders_reader import get_folder
from utils.utils_folders_writer import set_pin_folder
from utils.utils_items_reader import get_folder_items

router = Router()
dp.include_router(router)

numbers = numbers_ico.values()
pattern = r'|'.join(map(re.escape, numbers))

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
    await state.set_state(states.FolderState.EditName)


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


@router.callback_query(StatisticFolderCallback.filter())
async def statistic_handler(call: CallbackQuery):
    user_id = call.from_user.id
    call_data = StatisticFolderCallback.unpack(call.data)
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


def get_ok_inline_markup(insert_button=None):
    inline_markup = (
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='☑️ OK', callback_data=MessageBoxCallback(result='ok').pack())  # ☑️ ✔️
                ],
            ])
    )
    if insert_button:
        insert_button: InlineKeyboardButton = insert_button
        inline_markup.inline_keyboard.insert(0, [insert_button])
    return inline_markup


@router.callback_query(SearchInFolderCallback.filter())
async def search_in_folder_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data = SearchInFolderCallback.unpack(call.data)
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
    await state.set_state(states.ItemState.Search)
    await state.update_data(search_message=search_message)


@router.callback_query(PinFolderCallback.filter())
async def pin_folder_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data = PinFolderCallback.unpack(call.data)
    folder_id = call_data.folder_id
    folder: Folder = await get_folder(user_id, folder_id)
    pin = folder.get_pin()
    if pin:
        inline_markup = get_pin_control_inline_markup(folder_id)
        await bot.send_message(
                 chat_id=user_id,
                 text=f'Управление PIN-кодом папки {folder.name}:',
                 reply_markup=inline_markup
             )
    else:
        inline_markup = get_folder_pin_inline_markup(user_id, folder_id)
        await bot.send_message(
            chat_id=user_id,
            text=f'Придумайте PIN-код для папки\n{smile_folder} {folder.name}:',
            reply_markup=inline_markup
        )
    # if not pin:
    #     inline_markup = get_folder_pin_inline_markup(user_id, folder_id)
    #     await bot.send_message(
    #         chat_id=user_id,
    #         text=f'Придумайте PIN-код для папки\n{smile_folder} {folder.name}:',  # \n\n➖ ➖ ➖ ➖',
    #         reply_markup=inline_markup
    #     )
    # else:
    #     inline_markup = get_folder_pin_inline_markup(user_id, folder_id, pin=pin)
    #     await bot.send_message(
    #         chat_id=user_id,
    #         text=f'Введите текущий PIN-код для папки\n{smile_folder} {folder.name}:',  # \n\n➖ ➖ ➖ ➖',
    #         reply_markup=inline_markup
    #     )
    data = await get_data(user_id)
    data['enter_pin'] = ''
    await set_data(user_id, data)
    await call.answer()


@router.callback_query(PinKeyboardNumberCallback.filter())
async def number_pin_folder_handler(call: CallbackQuery, state: FSMContext):
    inline_markup = call.message.reply_markup
    pin_code_button: InlineKeyboardButton = inline_markup.inline_keyboard[0][0]
    if NewPinCodeButtonCallback.__prefix__ in pin_code_button.callback_data:
        await number_new_pin_folder_handler(call, inline_markup, pin_code_button)
    else:
        await number_enter_pin_folder_handler(call, inline_markup, pin_code_button)

    await call.answer()


async def number_new_pin_folder_handler(call, inline_markup, pin_code_button):
    user_id = call.from_user.id

    pin_code_data = NewPinCodeButtonCallback.unpack(pin_code_button.callback_data)
    print(f'pin_code_data {pin_code_data}')
    pin = pin_code_data.pin
    pin_repeat = pin_code_data.pin_repeat
    folder_id = pin_code_data.folder_id

    call_data = PinKeyboardNumberCallback.unpack(call.data)
    number = call_data.number
    if len(pin) < 4 or len(pin_repeat) < 4:
        if len(pin) < 4:
            pin += str(number)
        else:
            pin_repeat += str(number)

        pin_code_button.callback_data = NewPinCodeButtonCallback(
            folder_id=folder_id, pin=pin, pin_repeat=pin_repeat, visible=pin_code_data.visible
        ).pack()
        if pin_code_data.visible:
            pin_code_button.text = pin_code_button.text.replace('❔', numbers_ico[str(number)], 1)
        else:
            pin_code_button.text = pin_code_button.text.replace('➖', '🔘', 1)
        await bot.edit_message_reply_markup(
            chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )

    if len(pin) == 4 and len(pin_repeat) == 0:
        if pin_code_data.visible:
            pin_code_button.text = re.sub(pattern, '🟡', pin_code_button.text)
        else:
            pin_code_button.text = pin_code_button.text.replace('🔘', '🟡')
        await bot.edit_message_reply_markup(
            chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )
        await asyncio.sleep(0.5)
        message_text = 'Повторите PIN-код:'
        if pin_code_data.visible:
            pin_code_button.text = pin_code_button.text.replace('🟡', '❔')
        else:
            pin_code_button.text = pin_code_button.text.replace('🟡', '➖')

        await bot.edit_message_text(
            text=message_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )
    elif len(pin) == 4 and len(pin_repeat) == 4 and pin == pin_repeat:
        message_text = '✅ PIN-код установлен.'
        if pin_code_data.visible:
            pin_code_button.text = re.sub(pattern, '🟢', pin_code_button.text)
            pass
        else:
            pin_code_button.text = pin_code_button.text.replace('🔘', '🟢')
        await set_pin_folder(user_id, folder_id, pin)
        await asyncio.sleep(0.5)
        if pin_code_data.visible:
            for number in pin:
                pin_code_button.text = pin_code_button.text.replace('🟢', numbers_ico[number], 1)
        inline_markup = get_ok_inline_markup(pin_code_button)
        await bot.edit_message_text(
            text=message_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )
    elif len(pin) == 4 and len(pin_repeat) == 4 and pin != pin_repeat:
        if pin_code_data.visible:
            #pin_code_button.text = re.sub(pattern, '🔴', pin_code_button.text)
            pass
        else:
            pin_code_button.text = pin_code_button.text.replace('🔘', '🔴')
            await bot.edit_message_reply_markup(
                chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
            )
        await asyncio.sleep(0.5)
        message_text = '❌ PIN-код не совпадает.\nВыберите действие:'
        #pin_code_button.text = pin_code_button.text.replace('🟡', '➖')
        await bot.edit_message_text(
            text=message_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )


async def number_enter_pin_folder_handler(call, inline_markup, pin_code_button):
    user_id = call.from_user.id

    pin_code_data = EnterPinCodeButtonCallback.unpack(pin_code_button.callback_data)
    print(f'pin_code_data {pin_code_data}')
    pin = pin_code_data.pin
    pin_repeat = pin_code_data.pin_repeat
    folder_id = pin_code_data.folder_id

    call_data = PinKeyboardNumberCallback.unpack(call.data)
    number = call_data.number
    if len(pin_repeat) < 4:
        pin_repeat += str(number)

        pin_code_button.callback_data = EnterPinCodeButtonCallback(
            folder_id=folder_id, pin=pin, pin_repeat=pin_repeat, visible=pin_code_data.visible
        ).pack()
        if pin_code_data.visible:
            pin_code_button.text = pin_code_button.text.replace('❔', numbers_ico[str(number)], 1)
        else:
            pin_code_button.text = pin_code_button.text.replace('➖', '🔘', 1)
        await bot.edit_message_reply_markup(
            chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )

    if len(pin_repeat) == 4 and pin == pin_repeat:
        message_text = f'✅ PIN-код подтвержден.{INVISIBLE_CHAR * 10}'
        if pin_code_data.visible:
            await show_enter_pin_result(call, user_id, inline_markup, pin_code_button, pin, message_text, '🟢')
        else:
            pin_code_button.text = pin_code_button.text.replace('🔘', '🟢')
            await asyncio.sleep(0.4)
            # inline_markup = get_ok_inline_markup(pin_code_button)
            await bot.edit_message_text(
                text=message_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
            )
        await show_folders(user_id=user_id, current_folder_id=folder_id)
        await bot.delete_message(user_id, message_id=call.message.message_id)

    elif len(pin_repeat) == 4 and pin != pin_repeat:
        message_text = f'❌ PIN-код не совпадает.{INVISIBLE_CHAR * 20}\nПопробуйте еще раз:'
        if pin_code_data.visible:
            await show_enter_pin_result(call, user_id, inline_markup, pin_code_button, pin, message_text, '🔴')
        else:
            pin_code_button.text = pin_code_button.text.replace('🔘', '🔴')
            await asyncio.sleep(0.4)
            await bot.edit_message_reply_markup(
                chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
            )
        await asyncio.sleep(0.1)
        inline_markup = get_folder_pin_inline_markup(user_id, folder_id, pin)
        await bot.edit_message_reply_markup(
            chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )


async def show_enter_pin_result(call, user_id, inline_markup, pin_code_button, pin, message_text, icon):
    pin_code_button.text = re.sub(pattern, icon, pin_code_button.text)
    await bot.edit_message_reply_markup(
        chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
    )
    await asyncio.sleep(0.6)
    pin_button_text = pin_code_button.text
    for number in pin:
        pin_button_text = re.sub(icon, numbers_ico[number], pin_button_text, 1)
    pin_code_button.text = pin_button_text
    inline_markup.inline_keyboard[0][0] = pin_code_button
    await bot.edit_message_reply_markup(
        chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
    )


@router.callback_query(PinKeyboardButtonCallback.filter())
async def button_pin_folder_handler(call: CallbackQuery):
    user_id = call.from_user.id
    call_data = PinKeyboardButtonCallback.unpack(call.data)
    action = call_data.action
    if action == 'close':
        await bot.delete_message(user_id, call.message.message_id)
    elif action == 'backspace':
        inline_markup = call.message.reply_markup
        pin_code_button: InlineKeyboardButton = inline_markup.inline_keyboard[0][0]
        if NewPinCodeButtonCallback.__prefix__ in pin_code_button.callback_data:
            pin_code_data = NewPinCodeButtonCallback.unpack(pin_code_button.callback_data)
        else:
            pin_code_data = EnterPinCodeButtonCallback.unpack(pin_code_button.callback_data)

        if pin_code_data.pin_repeat and len(pin_code_data.pin_repeat) < 4:
            pin_code_data.pin_repeat = pin_code_data.pin_repeat[:-1]
        elif pin_code_data.pin and len(pin_code_data.pin) < 4:
            pin_code_data.pin = pin_code_data.pin[:-1]
        else:
            await call.answer()
            return

        pin_code_button.callback_data = pin_code_data.pack()
        if pin_code_data.visible:
            numbers = numbers_ico.values()
            text_reversed = pin_code_button.text[::-1]
            pattern_reversed = r'|'.join(map(lambda x: re.escape(x[::-1]), numbers))
            text_reversed_modified = re.sub(pattern_reversed, '❔'[::-1], text_reversed, 1)
            pin_code_button.text = text_reversed_modified[::-1]
        else:
            pin_code_button.text = pin_code_button.text[::-1].replace('🔘', '➖', 1)[::-1]
        inline_markup.inline_keyboard[0][0] = pin_code_button
        await bot.edit_message_reply_markup(
            chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        )
    await call.answer()


@router.callback_query(NewPinCodeButtonCallback.filter())
@router.callback_query(EnterPinCodeButtonCallback.filter())
async def number_pin_code_button_handler(call: CallbackQuery):
    inline_markup = call.message.reply_markup
    pin_code_button: InlineKeyboardButton = inline_markup.inline_keyboard[0][0]
    pin_button_text = pin_code_button.text

    is_new_pin = NewPinCodeButtonCallback.__prefix__ in pin_code_button.callback_data
    if is_new_pin:
        call_data = NewPinCodeButtonCallback.unpack(call.data)
    else:
        call_data = EnterPinCodeButtonCallback.unpack(call.data)
    user_id = call.from_user.id
    pin = call_data.pin_repeat if call_data.pin_repeat else call_data.pin
    visible = call_data.visible
    visible = not visible
    if visible:
        pattern = r'🔘|🟡|🔴|🟢'
        for number in pin:
            pin_button_text = re.sub(pattern, numbers_ico[number], pin_button_text, 1)
        pin_button_text = pin_button_text.replace('➖', '❔')
        pin_button_text = pin_button_text.replace('🫣', '🧐')
    else:
        #pattern = r'0|1|2|3|4|5|6|7|8|9'
        numbers = numbers_ico.values()
        pattern = r'|'.join(map(re.escape, numbers))
        if len(pin) < 4:
            pin_button_text = re.sub(pattern, '🔘', pin_button_text)
            pin_button_text = pin_button_text.replace('❔', '➖')
        elif len(pin) == 4:
            if call_data.pin_repeat and call_data.pin == call_data.pin_repeat:
                pin_button_text = re.sub(pattern, '🟢', pin_button_text)
            elif call_data.pin_repeat and call_data.pin != call_data.pin_repeat:
                pin_button_text = re.sub(pattern, '🔴', pin_button_text)
            elif not call_data.pin_repeat:
                pin_button_text = re.sub(pattern, '🟡', pin_button_text)
        pin_button_text = pin_button_text.replace('❔', '➖')
        pin_button_text = pin_button_text.replace('🧐', '🫣')
    pin_code_button.text = pin_button_text
    if is_new_pin:
        pin_code_button.callback_data = NewPinCodeButtonCallback(
            folder_id=call_data.folder_id,
            pin=call_data.pin,
            pin_repeat=call_data.pin_repeat,
            visible=visible
        ).pack()
    else:
        pin_code_button.callback_data = EnterPinCodeButtonCallback(
            folder_id=call_data.folder_id,
            pin=call_data.pin,
            pin_repeat=call_data.pin_repeat,
            visible=visible
        ).pack()
    inline_markup.inline_keyboard[0] = [pin_code_button]
    await bot.edit_message_reply_markup(
        chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
    )

