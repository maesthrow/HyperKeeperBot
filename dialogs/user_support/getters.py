from aiogram_dialog import DialogManager

from dialogs import general_keyboards
from resources.text_getter import get_text
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