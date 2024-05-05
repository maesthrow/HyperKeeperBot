from aiogram_dialog import DialogManager

from dialogs.giga_chat import keyboards
from resources.text_getter import get_text
from utils.utils_data import get_current_lang


async def get_new_chat_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    start_text = await get_text(user.id, 'start_chat_text')
    message_text = start_text
    return {
        'message_text': message_text,
        'btn_stop_chat': keyboards.BUTTONS['stop_chat'].get(language),
    }


async def get_request_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    response_text = dialog_manager.current_context().dialog_data.get('response_text')
    message_text = response_text
    return {
        'message_text': message_text,
        'btn_stop_chat': keyboards.BUTTONS['stop_chat'].get(language),
    }