from typing import List

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from langchain_core.messages import SystemMessage, HumanMessage

from handlers_pack.states import MainMenuState, GigaChatState
from load_all import giga_chat, bot
from utils.data_manager import set_any_message_ignore, get_data, set_data
from utils.utils_parse_mode_converter import escape_markdown


async def on_first_user_request(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id

    await bot.send_chat_action(message.chat.id, "typing")

    giga_chat_messages = [
        SystemMessage(
            content="Ты эмпатичный бот-помощник, который помогает пользователю решить любые его задачи."
        ),
        HumanMessage(content=input_text)
    ]
    response = await _get_response(giga_chat_messages)
    giga_chat_messages.append(response)
    data = await get_data(user_id)
    data['giga_chat_messages'] = giga_chat_messages
    await set_data(user_id, data)
    dialog_manager.current_context().dialog_data = {'response_text': escape_markdown(response.content)}
    await set_any_message_ignore(user_id, True)
    await dialog_manager.switch_to(GigaChatState.Request)


async def on_user_request(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id

    await bot.send_chat_action(message.chat.id, "typing")

    data = await get_data(user_id)
    giga_chat_messages: List = data.get('giga_chat_messages')
    giga_chat_messages.append(HumanMessage(content=input_text))
    response = await _get_response(giga_chat_messages)
    giga_chat_messages.append(response)
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
