from aiogram_dialog import DialogManager

from dialogs import general_keyboards
from dialogs.giga_chat import keyboards
from resources.text_getter import get_text
from utils.utils_data import get_current_lang


async def get_menu_chats_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    giga_menu_chats_title = await get_text(user.id, 'giga_menu_chats_title')
    message_text = giga_menu_chats_title
    return {
        'message_text': message_text,
        'btn_new_chat': keyboards.BUTTONS['new_chat'].get(language),
        'btn_menu': general_keyboards.BUTTONS['menu'].get(language),
    }


async def get_new_chat_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    start_text = await get_text(user.id, 'start_chat_text')
    message_text = start_text
    return {
        'message_text': message_text,
    }


async def get_query_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    response_text = dialog_manager.current_context().dialog_data.get('response_text')
    message_text = response_text
    return {
        'message_text': message_text,
    }