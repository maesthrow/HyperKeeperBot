from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from handlers_pack.states import MainMenuState


async def open_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuState.Menu, show_mode=ShowMode.SEND)


async def close_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.delete()


async def open_storage_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def accesses_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def search_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def user_profile_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def settings_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def help_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass
