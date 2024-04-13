from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ChatEvent
from aiogram_dialog.widgets.kbd import Button, ManagedCheckbox

from enums.enums import Language
from handlers_pack.states import SettingsMenuState
from utils.utils_data import get_from_user_collection, set_to_user_collection


async def on_back_settings_click_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(SettingsMenuState.Menu)


async def folders_on_page_count_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(SettingsMenuState.FoldersOnPageCount)


async def items_on_page_count_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(SettingsMenuState.ItemsOnPagesCount)


async def language_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(SettingsMenuState.Language)


async def language_changed(event: ChatEvent, checkbox: ManagedCheckbox, dialog_manager: DialogManager):
    if not checkbox.is_checked():
        return

    user_id = dialog_manager.event.from_user.id
    settings = await get_from_user_collection(user_id, 'settings')
    current_language = Language(settings.get('language', "russian"))
    language: Language = Language(checkbox.widget.widget_id)
    if language != current_language:
        settings["language"] = language.value
        await set_to_user_collection(user_id, 'settings', settings)


async def folders_on_page_count_changed(event: ChatEvent, checkbox: ManagedCheckbox, dialog_manager: DialogManager):
    if not checkbox.is_checked():
        return

    user_id = dialog_manager.event.from_user.id
    settings = await get_from_user_collection(user_id, 'settings')
    folder_on_page_count = settings.get('folders_on_page_count', 6)
    count = int(checkbox.widget.widget_id.split('_')[-1])
    if count != folder_on_page_count:
        settings["folders_on_page_count"] = count
        await set_to_user_collection(user_id, 'settings', settings)


async def items_on_page_count_changed(event: ChatEvent, checkbox: ManagedCheckbox, dialog_manager: DialogManager):
    if not checkbox.is_checked():
        return

    user_id = dialog_manager.event.from_user.id
    settings = await get_from_user_collection(user_id, 'settings')
    items_on_page_count = settings.get('items_on_page_count', 6)
    count = int(checkbox.widget.widget_id.split('_')[-1])
    if count != items_on_page_count:
        settings["items_on_page_count"] = count
        await set_to_user_collection(user_id, 'settings', settings)
