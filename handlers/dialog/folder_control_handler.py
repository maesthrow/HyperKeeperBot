import asyncio

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from handlers.handlers_folder import show_folders
from handlers.states import FolderControlStates
from load_all import bot
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
    #folder_id = manager.dialog_data.get('folder_id', None)
    folder_id = await get_current_folder_id(user_id)
    print(f'access_delete_all_items_handler folder_id = {await manager.load_data()}')
    result_message = ''
    if folder_id:
        try:
            # Вызываем метод для удаления папки
            result = await util_delete_all_items_in_folder(user_id, folder_id)
            print(f"result {result}")
            if result:
                result_message = await callback.message.answer(f"Все записи в папке удалены ☑️")
            else:
                result_message = await callback.message.answer(text=f"Не получилось удалить записи.'", show_alert=True)
            await callback.answer()
            await manager.switch_to(FolderControlStates.MainMenu)
            await show_folders(user_id, need_to_resend=False)
        except:
            await callback.answer(text=f"Что то пошло не так при удалении записей.", show_alert=True)
            await show_folders(user_id, need_to_resend=False)

        if result_message:
            await asyncio.sleep(0.7)
            await bot.delete_message(chat_id=result_message.chat.id, message_id=result_message.message_id)


async def cancel_delete_all_items_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FolderControlStates.MainMenu)

