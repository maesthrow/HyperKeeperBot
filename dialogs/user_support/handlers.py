import os

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from dialogs.user_support.getters import get_user_info_for_admin
from handlers_pack.states import MainMenuState, UserSupportState
from load_all import bot
from resources.text_getter import get_text
from utils.data_manager import set_any_message_ignore
from utils.utils_button_manager import get_contact_support_admin_markup, get_contact_support_user_markup


async def on_contact_support(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    await _send_contact_message_to_admin(user_id, input_text)
    await set_any_message_ignore(user_id, False)
    await dialog_manager.switch_to(UserSupportState.AfterContactSupport)


async def cancel_contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    await set_any_message_ignore(user_id, False)
    await dialog_manager.done()
    await dialog_manager.start(MainMenuState.HelpMenu)


async def back_contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
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
    await _send_answer_contact_message_to_user(contact_user_id, input_text)
    await set_any_message_ignore(user_id, False)
    await dialog_manager.switch_to(UserSupportState.AfterAnswerUserContactSupport)


async def cancel_answer_user_contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    await set_any_message_ignore(user_id, False)
    await dialog_manager.done()
    await callback.message.delete()


async def back_answer_user_contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    contact_user_id = dialog_manager.current_context().start_data.get('contact_user_id')
    contact_text = dialog_manager.current_context().start_data.get('contact_text')
    await set_any_message_ignore(user_id, False)
    await dialog_manager.done()
    #await callback.message.delete()
    await _send_contact_message_to_admin(contact_user_id, contact_text, callback.message)


async def after_answer_user_contact_support_ok_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.delete()


async def _send_contact_message_to_admin(contact_user_id, contact_text, edit_message: Message = None):
    contact_user_info = await get_user_info_for_admin(str(contact_user_id))
    message_to_admin_text = f'<b>Обращение от пользователя:</b>\n\n{contact_user_info}\n\n<i>{contact_text}</i>'
    inline_markup = get_contact_support_admin_markup('💬 Быстрый ответ', str(contact_user_id))
    if not edit_message:
        await bot.send_message(os.getenv('ADMIN_SUPPORT_ID'), message_to_admin_text, reply_markup=inline_markup)
    else:
        await bot.edit_message_text(
            chat_id=os.getenv('ADMIN_SUPPORT_ID'),
            text=message_to_admin_text,
            message_id=edit_message.message_id,
            reply_markup=inline_markup
        )


async def _send_answer_contact_message_to_user(contact_user_id, answer_text, edit_message: Message = None):
    answer_title_text = await get_text(contact_user_id, 'answer_user_contact_support_title')
    message_to_user_text = f'<b>{answer_title_text}</b>\n\n<i>{answer_text}</i>'
    btn_quick_response_text = await get_text(contact_user_id, 'quick_response')
    inline_markup = await get_contact_support_user_markup(btn_quick_response_text, str(contact_user_id))
    await bot.send_message(contact_user_id, message_to_user_text, reply_markup=inline_markup)