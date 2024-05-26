import asyncio
import os

from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from dialogs.general_handlers import try_delete_message
from dialogs.giga_chat.keyboards import get_chat_reply_keyboard
from handlers_pack.handlers import show_storage
from handlers_pack.states import MainMenuState, AccessesState, SettingsMenuState, UserSupportState, GigaChatState
from load_all import bot
from resources.text_getter import get_text
from utils.data_manager import get_data, set_data, set_any_message_ignore
from utils.utils_access import get_user_info
from utils.utils_button_manager import get_contact_support_admin_markup
from utils.utils_data import get_current_folder_id, get_current_lang


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


async def chatgpt_new_chat_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(GigaChatState.MenuChats)


async def search_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenuState.QuickSearch)


async def user_profile_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenuState.UserProfile)


async def settings_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(SettingsMenuState.Menu)


async def help_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuState.HelpMenu)


async def contact_support_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    await set_any_message_ignore(user_id, True)
    await dialog_manager.start(UserSupportState.ContactSupport)

