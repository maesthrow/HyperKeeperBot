from aiogram_dialog import DialogManager

from dialogs import general_keyboards
from resources.text_getter import get_text
from utils.utils_access import get_user_info
from utils.utils_data import get_current_lang


async def get_contact_support_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    title_text = await get_text(user.id, 'contact_support_title')
    contact_support_description = await get_text(user.id, 'contact_support_description')
    message_text = f'<b>{title_text}</b>\n\n{contact_support_description}'
    return {
        'message_text': message_text,
        'btn_cancel': general_keyboards.BUTTONS['cancel'].get(language)
    }


async def get_after_contact_support_message_text(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    message_text = await get_text(user.id, 'after_contact_support_text')
    return {
        'message_text': message_text,
    }


async def get_answer_user_contact_support_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    contact_user_id = dialog_manager.start_data.get('contact_user_id')
    contact_user_info = await get_user_info(str(contact_user_id))
    message_text = f'Введите текст ответа на обращение пользователя {contact_user_info} :'
    return {
        'message_text': message_text,
        'btn_cancel': general_keyboards.BUTTONS['cancel'].get(language)
    }


async def get_after_answer_user_contact_support_message_text(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    contact_user_id = dialog_manager.start_data.get('contact_user_id')
    contact_user_info = await get_user_info(str(contact_user_id))
    message_text = f'Ответ отправлен пользователю {contact_user_info}'
    return {
        'message_text': message_text,
    }
