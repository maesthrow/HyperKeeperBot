import os

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from handlers_pack.states import MainMenuState, UserSupportState
from load_all import bot
from resources.text_getter import get_text
from utils.data_manager import get_data, set_data, set_any_message_ignore
from utils.utils_access import get_user_info
from utils.utils_button_manager import get_contact_support_admin_markup, get_contact_support_user_markup
from utils.utils_data import get_current_lang


async def on_contact_support(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    user_info = await get_user_info(str(user_id))
    message_to_admin_text = f'<b>Обращение от пользователя:</b>\n{user_info}\n\n<i>{input_text}</i>'
    inline_markup = get_contact_support_admin_markup('💬 Быстрый ответ', str(user_id))
    await bot.send_message(os.getenv('ADMIN_SUPPORT_ID'), message_to_admin_text, reply_markup=inline_markup)
    await set_any_message_ignore(user_id, False)
    await dialog_manager.switch_to(UserSupportState.AfterContactSupport)


async def cancel_contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    await set_any_message_ignore(user_id, False)
    await dialog_manager.done()
    await dialog_manager.start(MainMenuState.HelpMenu)


async def after_contact_support_ok_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await dialog_manager.start(MainMenuState.HelpMenu)


async def on_answer_user_contact_support(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    contact_user_id = dialog_manager.start_data.get('contact_user_id')
    answer_title_text = await get_text(contact_user_id, 'answer_user_contact_support_title')
    message_to_user_text = f'<b>{answer_title_text}</b>\n\n<i>{input_text}</i>'
    inline_markup = await get_contact_support_user_markup('💬 Быстрый ответ', str(contact_user_id))
    await bot.send_message(contact_user_id, message_to_user_text, reply_markup=inline_markup)
    await set_any_message_ignore(user_id, False)
    await dialog_manager.switch_to(UserSupportState.AfterAnswerUserContactSupport)


async def cancel_answer_user_contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    await set_any_message_ignore(user_id, False)
    await dialog_manager.done()
    await callback.message.delete()


async def after_answer_user_contact_support_ok_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.delete()
