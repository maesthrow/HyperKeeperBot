import asyncio

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from handlers.handlers_folder import show_folders
from handlers.states import FolderControlStates
from load_all import bot
from utils.message_box import MessageBox
from utils.utils_data import get_current_folder_id
from utils.utils_items_db import util_delete_all_items_in_folder


async def pin_code_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def access_settings_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def statistic_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FolderControlStates.StatisticMenu)


async def delete_all_items_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FolderControlStates.DeleteAllItemsQuestion)


async def rename_folder_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def delete_folder_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def search_in_folder_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    pass


async def close_menu_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.done()
    await callback.message.delete()


async def access_delete_all_items_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    user_id = manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    message_text = "Не получилось удалить записи ✖️"
    if folder_id:
        try:
            # Вызываем метод для удаления папки
            result = await util_delete_all_items_in_folder(user_id, folder_id)
            print(f"result {result}")
            await callback.answer()
            if result:
                await show_folders(user_id, need_to_resend=False)
                message_text = "Все записи в папке удалены ☑️"
        except:
            await callback.answer(text=f"Что то пошло не так при удалении записей.", show_alert=True)
    else:
        await callback.answer(text=f"Что то пошло не так при удалении записей.", show_alert=True)

    manager.current_context().dialog_data["message_text"] = message_text
    await manager.switch_to(FolderControlStates.InfoMessage)


async def cancel_delete_all_items_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FolderControlStates.MainMenu)


async def info_message_ok_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FolderControlStates.MainMenu)

