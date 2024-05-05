from aiogram_dialog import DialogManager

from dialogs import general_keyboards
from load_all import bot
from resources.text_getter import get_text
from utils.utils_data import get_current_lang
from utils.utils_parse_mode_converter import escape_markdown


async def get_contact_support_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    title_text = await get_text(user.id, 'contact_support_title')
    contact_support_description = await get_text(user.id, 'contact_support_description')
    message_text = f'<b>{title_text}</b>\n\n{contact_support_description}'
    return {
        'message_text': message_text,
        'btn_cancel': general_keyboards.BUTTONS['cancel'].get(language),
        #'btn_back': general_keyboards.BUTTONS['back'].get(language),
    }


async def get_after_contact_support_message_text(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    after_contact_support_text = await get_text(user.id, 'after_contact_support_text')
    message_text = f'{user.first_name}, {after_contact_support_text}'
    return {
        'message_text': message_text,
    }


async def get_answer_user_contact_support_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    contact_user_id = dialog_manager.start_data.get('contact_user_id')
    contact_user_info = escape_markdown(await get_user_info_for_admin(str(contact_user_id)))
    contact_text = escape_markdown(dialog_manager.start_data.get('contact_text'))
    message_text = f'_*Введите текст ответа на обращение пользователя:*_\n\n{contact_user_info}\n\n`{contact_text}`'
    return {
        'message_text': message_text,
        #'btn_cancel': general_keyboards.BUTTONS['cancel'].get(language),
        'btn_back': general_keyboards.BUTTONS['back'].get(language)
    }


async def get_after_answer_user_contact_support_message_text(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    contact_user_id = dialog_manager.start_data.get('contact_user_id')
    contact_user_info = await get_user_info_for_admin(str(contact_user_id))
    message_text = f'<b>Ответ отправлен пользователю:</b>\n\n{contact_user_info}'
    return {
        'message_text': message_text,
    }


async def get_user_info_for_admin(tg_user_id: str):
    try:
        chat = await bot.get_chat(chat_id=tg_user_id)
        if not chat:
            return None
        info = [chat.full_name]
        if chat.username:
            info.append(f'@{chat.username}')
        info.append(f'id: {chat.id}')
        user_info = '\n'.join(info)
        return user_info
    except:
        return None
