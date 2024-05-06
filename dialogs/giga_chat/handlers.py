import asyncio
from typing import List

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from dialogs.giga_chat import keyboards
from dialogs.giga_chat.keyboards import get_chat_reply_keyboard
from handlers_pack.states import MainMenuState, GigaChatState
from load_all import giga_chat, bot
from resources.text_getter import get_text
from utils.data_manager import set_any_message_ignore, get_data, set_data
from utils.utils_data import get_current_lang
from utils.utils_parse_mode_converter import escape_markdown


async def on_first_user_request(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)

    await bot.send_chat_action(message.chat.id, "typing")

    start_text = await get_text(user_id, 'start_chat_text')
    giga_chat_system_message = await get_text(user_id, 'giga_chat_system_message')

    giga_chat_messages = [
        SystemMessage(content=giga_chat_system_message),
        AIMessage(content=start_text),
        HumanMessage(content=input_text)
    ]
    response = await _get_response(giga_chat_messages)
    giga_chat_messages.append(response)
    data = await get_data(user_id)

    if await _check_stop_chat(user_id, language, input_text, response, dialog_manager, data):
        return

    data['giga_chat_messages'] = giga_chat_messages
    await set_data(user_id, data)
    dialog_manager.current_context().dialog_data = {'response_text': escape_markdown(response.content)}
    await set_any_message_ignore(user_id, True)
    await dialog_manager.switch_to(GigaChatState.Request)


async def on_user_request(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)

    await bot.send_chat_action(message.chat.id, "typing")

    data = await get_data(user_id)
    giga_chat_messages: List = data.get('giga_chat_messages')
    giga_chat_messages.append(HumanMessage(content=input_text))
    response = await _get_response(giga_chat_messages)
    giga_chat_messages.append(response)

    if await _check_stop_chat(user_id, language, input_text, response, dialog_manager, data):
        return

    data['giga_chat_messages'] = giga_chat_messages
    await set_data(user_id, data)
    dialog_manager.current_context().dialog_data = {'response_text': escape_markdown(response.content)}
    await set_any_message_ignore(user_id, True)
    await dialog_manager.switch_to(GigaChatState.Request)


async def stop_chat_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    await set_any_message_ignore(user_id, False)
    await dialog_manager.done()
    await dialog_manager.start(MainMenuState.Menu)


async def _get_response(messages: List):
    res = giga_chat(messages)
    print(res)
    return res


async def _check_stop_chat(user_id, language, input_text, response, dialog_manager, data):
    print(f'{input_text}')
    stop_chat_btn_text = keyboards.BUTTONS.get('stop_chat').get(language)
    print(f'{input_text}\n{stop_chat_btn_text}')
    if input_text == stop_chat_btn_text:
        data['giga_chat_messages'] = None
        await set_any_message_ignore(user_id, False)
        await set_data(user_id, data)
        await bot.send_message(user_id, response.content, reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(0.5)
        await dialog_manager.done()
        #await dialog_manager.start(MainMenuState.Menu)
        print('stop')
        return True
    return False
