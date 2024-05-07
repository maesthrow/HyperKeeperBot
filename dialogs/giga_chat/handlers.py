import asyncio
from typing import List

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, DateTime
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.internal import Widget
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
from utils.utils_wit_ai_voice import get_voice_text, get_video_note_text


async def new_chat_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    await set_any_message_ignore(user_id, True)
    reply_keyboard = get_chat_reply_keyboard(language)
    new_chat_title = await get_text(user_id, 'giga_new_chat_title')
    message_text = f'<b>{new_chat_title}</b>'
    tasks = []
    tasks.append(bot.send_message(user_id, message_text, reply_markup=reply_keyboard))
    tasks.append(dialog_manager.start(GigaChatState.NewChat, show_mode=ShowMode.DELETE_AND_SEND))
    await asyncio.gather(*tasks)


async def on_first_user_query(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)

    await bot.send_chat_action(message.chat.id, "typing")

    data = await get_data(user_id)

    if await _check_stop_chat(user_id, language, input_text, dialog_manager, data):
        return

    query_giga_chat_count = _get_query_giga_chat_count_info(data)
    if await _check_limit_giga_chat_queries(user_id, query_giga_chat_count, dialog_manager, data):
        return

    start_text = await get_text(user_id, 'start_chat_text')
    giga_chat_system_message = await get_text(user_id, 'giga_chat_system_message')
    giga_chat_messages = [
        SystemMessage(content=giga_chat_system_message),
        AIMessage(content=start_text),
        HumanMessage(content=input_text)
    ]
    response = await _get_response(giga_chat_messages)
    giga_chat_messages.append(response)

    data['query_giga_chat_count'] = query_giga_chat_count
    data['giga_chat_messages'] = giga_chat_messages
    await set_data(user_id, data)
    dialog_manager.current_context().dialog_data = {'response_text': escape_markdown(response.content)}
    await set_any_message_ignore(user_id, True)
    await dialog_manager.switch_to(GigaChatState.Query)


async def on_user_query(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)

    await bot.send_chat_action(message.chat.id, "typing")

    data = await get_data(user_id)

    if await _check_stop_chat(user_id, language, input_text, dialog_manager, data):
        return

    query_giga_chat_count = _get_query_giga_chat_count_info(data)
    if await _check_limit_giga_chat_queries(user_id, query_giga_chat_count, dialog_manager, data):
        return

    giga_chat_messages: List = data.get('giga_chat_messages')
    giga_chat_messages.append(HumanMessage(content=input_text))
    response = await _get_response(giga_chat_messages)
    giga_chat_messages.append(response)

    data['giga_chat_messages'] = giga_chat_messages
    await set_data(user_id, data)
    dialog_manager.current_context().dialog_data = {'response_text': escape_markdown(response.content)}
    await set_any_message_ignore(user_id, True)
    await dialog_manager.switch_to(GigaChatState.Query)


async def on_first_user_voice_query(message: Message, widget: Widget, dialog_manager: DialogManager):
    await _on_voice_query(message, widget, dialog_manager, on_first_user_query)


async def on_user_voice_query(message: Message, widget: Widget, dialog_manager: DialogManager):
    await _on_voice_query(message, widget, dialog_manager, on_user_query)


async def _on_voice_query(message: Message, widget: Widget, dialog_manager: DialogManager, func):
    if message.content_type == ContentType.VOICE:
        voice_text = await get_voice_text(message.voice, message)
        await func(message, None, dialog_manager, voice_text)
    elif message.content_type == ContentType.VIDEO_NOTE:
        voice_text = await get_video_note_text(message.video_note, message)
        await func(message, None, dialog_manager, voice_text)


async def _get_response(messages: List):
    res = giga_chat(messages)
    print(res)
    return res


async def _check_stop_chat(user_id, language, input_text, dialog_manager, data):
    close_chat_btn_text = keyboards.BUTTONS.get('close_chat').get(language)
    save_and_close_chat_btn_text = keyboards.BUTTONS.get('save_and_close_chat').get(language)
    if input_text == save_and_close_chat_btn_text:
        stop_text = await get_text(user_id, 'on_close_and_save_chat_text')
        await _stop_chat(user_id, stop_text, dialog_manager, data, time_sec=1)
        return True
    elif input_text == close_chat_btn_text:
        stop_text = await get_text(user_id, 'on_close_chat_text')
        await _stop_chat(user_id, stop_text, dialog_manager, data, time_sec=1)
        return True
    return False


def _get_query_giga_chat_count_info(data):
    query_giga_chat_count = data.get('query_giga_chat_count', [DateTime.now().day, 0])
    if query_giga_chat_count[0] == DateTime.now().day:
        query_giga_chat_count[1] += 1
    else:
        query_giga_chat_count[0] = DateTime.now().day
        query_giga_chat_count[1] = 0
    return query_giga_chat_count


async def _check_limit_giga_chat_queries(user_id, query_giga_chat_count, dialog_manager, data):
    if query_giga_chat_count[1] > 25:
        over_limit_text = await get_text(user_id, 'over_limit_giga_chat_text')
        await _stop_chat(user_id, over_limit_text, dialog_manager, data, time_sec=2)
        return True
    return False


async def _stop_chat(user_id, message_text, dialog_manager, data, time_sec):
    await bot.send_message(user_id, message_text, reply_markup=ReplyKeyboardRemove())
    data['giga_chat_messages'] = None
    await set_any_message_ignore(user_id, False)
    await set_data(user_id, data)
    await asyncio.sleep(time_sec)
    await dialog_manager.done()

