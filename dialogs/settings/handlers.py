from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ChatEvent
from aiogram_dialog.widgets.kbd import Button, ManagedCheckbox

from handlers_pack.states import SettingsMenuState


async def language_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(SettingsMenuState.Language)


async def language_changed(event: ChatEvent, checkbox: ManagedCheckbox, dialog_manager: DialogManager):
    print(checkbox.is_checked())
