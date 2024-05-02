import asyncio
import os

from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from dialogs.general_handlers import try_delete_message
from handlers_pack.handlers import show_storage
from handlers_pack.states import MainMenuState, AccessesState, SettingsMenuState
from load_all import bot
from utils.data_manager import get_data, set_data
from utils.utils_access import get_user_info
from utils.utils_button_manager import get_contact_support_admin_markup
from utils.utils_data import get_current_folder_id


async def close_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.delete()


async def open_storage_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    current_folder_id = await get_current_folder_id(user_id)
    await show_storage(user_id=user_id, folder_id=current_folder_id)


async def accesses_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    start_message = await bot.send_message(dialog_manager.event.from_user.id, '🔐', reply_markup=ReplyKeyboardRemove())
    await dialog_manager.start(
        AccessesState.UsersMenu,
        show_mode=ShowMode.DELETE_AND_SEND,
        data={
            'start_message': start_message,
        }
    )


async def search_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenuState.LiveSearch)


async def user_profile_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenuState.UserProfile)


async def settings_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(SettingsMenuState.Menu)


async def help_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuState.HelpMenu)


async def contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    data = await get_data(user_id)
    data['any_message_ignore'] = True
    await set_data(user_id, data)
    await dialog_manager.start(MainMenuState.ContactSupport)


async def on_contact_support(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = dialog_manager.event.from_user.id
    user_info = await get_user_info(str(user_id))
    message_to_admin_text = f'<b>Обращение от пользователя:</b>\n{user_info}\n\n<i>{input_text}</i>'
    inline_markup = get_contact_support_admin_markup('💬 Быстрый ответ', str(user_id))
    await bot.send_message(os.getenv('ADMIN_SUPPORT_ID'), message_to_admin_text, reply_markup=inline_markup)
    data = await get_data(user_id)
    data['any_message_ignore'] = False
    await set_data(user_id, data)
    await dialog_manager.switch_to(MainMenuState.AfterContactSupport)


async def cancel_contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    data = await get_data(user_id)
    data['any_message_ignore'] = False
    await set_data(user_id, data)
    await dialog_manager.switch_to(MainMenuState.HelpMenu)


async def after_contact_support_ok_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenuState.HelpMenu)
