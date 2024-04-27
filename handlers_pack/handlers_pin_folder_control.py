import asyncio
import re

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager

from callbacks.callbackdata import MessageBoxCallback, \
    SearchInFolderCallback, PinFolderCallback, PinKeyboardNumberCallback, PinKeyboardButtonCallback, \
    NewPinCodeButtonCallback, EnterPinCodeButtonCallback, PinControlCallback
from handlers_pack import states
from handlers_pack.handlers_folder import show_folders
from handlers_pack.states import FolderControlStates
from load_all import dp, bot
from models.folder_model import Folder
from models.item_model import INVISIBLE_CHAR
from utils.data_manager import get_data, set_data
from utils.message_box import MessageBox
from utils.utils_ import smile_folder
from utils.utils_button_manager import create_general_reply_markup, general_buttons_search_items, \
    get_folder_pin_inline_markup, get_pin_control_inline_markup
from utils.utils_constants import numbers_ico
from utils.utils_folders_reader import get_folder
from utils.utils_folders_writer import set_pin_folder, remove_pin_folder

router = Router()
dp.include_router(router)

numbers = numbers_ico.values()
pattern = r'|'.join(map(re.escape, numbers))


def get_ok_inline_markup(insert_button=None):
    inline_markup = (
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='OK', callback_data=MessageBoxCallback(result='ok').pack())  # ☑️ ✔️
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
async def pin_folder_handler(call: CallbackQuery, state: FSMContext = None):
    user_id = call.from_user.id
    call_data = PinFolderCallback.unpack(call.data)
    folder_id = call_data.folder_id
    folder: Folder = await get_folder(user_id, folder_id)
    #folder_long_name = await get_folders_message_text(user_id, folder_id)
    pin = folder.get_pin()
    if pin:
        inline_markup = get_pin_control_inline_markup(folder_id)
        message_text = f'🔑 *Управление PIN\-кодом папки*\n\n{smile_folder} {folder.name}'
    else:
        inline_markup = get_folder_pin_inline_markup(user_id, folder_id)
        message_text = f'_Придумайте PIN\-код для папки:_\n\n{smile_folder} {folder.name}'
    await bot.send_message(
        chat_id=user_id,
        text=message_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inline_markup
    )
    await call.answer()


@router.callback_query(PinControlCallback.filter())
async def pin_folder_control_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data = PinControlCallback.unpack(call.data)
    folder_id = call_data.folder_id
    folder: Folder = await get_folder(user_id, folder_id)
    if call_data.action == 'change':
        inline_markup = get_folder_pin_inline_markup(user_id, folder_id)
        await bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text=f'_Придумайте новый PIN\-код для папки:_\n\n{smile_folder} {folder.name}',
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )
    elif call_data.action == 'remove':
        result = await remove_pin_folder(user_id, folder_id)
        if result:
            await MessageBox.show(user_id, 'PIN-код удален ☑️')
            await bot.delete_message(user_id, call.message.message_id)
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
        message_text = f'_Повторите PIN\-код:_{INVISIBLE_CHAR * 12}'
        if pin_code_data.visible:
            pin_code_button.text = pin_code_button.text.replace('🟡', '❔')
        else:
            pin_code_button.text = pin_code_button.text.replace('🟡', '➖')

        await bot.edit_message_text(
            text=message_text,
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )
    elif len(pin) == 4 and len(pin_repeat) == 4 and pin == pin_repeat:
        message_text = 'PIN\-код установлен ✅'
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
            text=message_text,
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )
    elif len(pin) == 4 and len(pin_repeat) == 4 and pin != pin_repeat:
        message_text = f'❌ _PIN\-код не совпадает\.{INVISIBLE_CHAR * 20}\nПопробуйте еще раз:_'
        if pin_code_data.visible:
            await show_enter_pin_result(call, user_id, inline_markup, pin_code_button, pin, '🔴')
        else:
            pin_code_button.text = pin_code_button.text.replace('🔘', '🔴')
            await asyncio.sleep(0.4)
            await bot.edit_message_reply_markup(
                chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
            )
        await asyncio.sleep(0.1)
        inline_markup = get_folder_pin_inline_markup(user_id, folder_id)
        await bot.edit_message_text(
            text=message_text,
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )
        # if pin_code_data.visible:
        #     #pin_code_button.text = re.sub(pattern, '🔴', pin_code_button.text)
        #     pass
        # else:
        #     pin_code_button.text = pin_code_button.text.replace('🔘', '🔴')
        #     await bot.edit_message_reply_markup(
        #         chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        #     )
        # await asyncio.sleep(0.5)
        # message_text = '❌ PIN-код не совпадает.\nВыберите действие:'
        # #pin_code_button.text = pin_code_button.text.replace('🟡', '➖')
        # await bot.edit_message_text(
        #     text=message_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup
        # )


async def get_user_code_word():
    pass


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
        message_text = f'PIN-код подтвержден ✅ {INVISIBLE_CHAR * 10}'
        if pin_code_data.visible:
            await show_enter_pin_result(call, user_id, inline_markup, pin_code_button, pin, '🟢')
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
        #message_text = f'❌ _PIN-код не совпадает.{INVISIBLE_CHAR * 20}\nПопробуйте еще раз:_'
        if pin_code_data.visible:
            await show_enter_pin_result(call, user_id, inline_markup, pin_code_button, pin, '🔴')
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


async def show_enter_pin_result(call, user_id, inline_markup, pin_code_button, pin, icon):
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
async def button_pin_folder_handler(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    user_id = call.from_user.id
    call_data = PinKeyboardButtonCallback.unpack(call.data)
    action = call_data.action
    if action == 'close':
        # print(f'state {state}')
        # print(f'state.get_state() = {state.get_state()}')
        if await state.get_state() == states.FolderState.EnterPin.state:
            await bot.delete_message(user_id, call.message.message_id)
            await state.set_state(state=None)
        else:
            await dialog_manager.start(FolderControlStates.MainMenu)
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
            pin_numbers = numbers_ico.values()
            text_reversed = pin_code_button.text[::-1]
            pattern_reversed = r'|'.join(map(lambda x: re.escape(x[::-1]), pin_numbers))
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
