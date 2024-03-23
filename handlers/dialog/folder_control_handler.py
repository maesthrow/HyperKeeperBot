from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from handlers.states import FolderControlStates


async def pin_code_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def access_settings_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def statistic_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FolderControlStates.StatisticMenu)


async def delete_all_items_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def rename_folder_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def delete_folder_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def search_in_folder_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def close_menu_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done()
    await callback.message.delete()
