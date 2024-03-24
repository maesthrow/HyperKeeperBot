from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from handlers.handlers_folder import show_folders
from handlers.states import FolderControlStates
from load_all import bot
from utils.utils_data import get_current_folder_id
from utils.utils_folders import invalid_chars
from utils.utils_folders_db import util_rename_folder
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
    await manager.switch_to(FolderControlStates.Rename)


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


async def cancel_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(FolderControlStates.MainMenu)


async def on_rename_folder(message: Message, widget: ManagedTextInput, manager: DialogManager, input_text):
    user_id = message.from_user.id
    folder_id = await get_current_folder_id(user_id)
    result = await util_rename_folder(user_id, folder_id, input_text)
    if result:
        message_text = "Папка успешно переименована ✅"
    else:
        message_text = "Что то пошло не так при редактировании папки ❌"
    manager.current_context().dialog_data["message_text"] = message_text
    await show_folders(user_id, need_to_resend=True)
    await manager.switch_to(FolderControlStates.InfoMessage)


async def on_error_rename_folder(data, widget, manager):
    new_folder_name = data.get_value()
    invalid_chars_list = ' '.join([char for char in invalid_chars if char in new_folder_name])
    invalid_chars_message = f"❗Название папки содержит недопустимые символы:" \
                            f"\n{invalid_chars_list}" \
                            f"\n\n<i>Придумайте другое название:</i>"
    await manager.dialog().bot.send_message(manager.event.from_user.id, invalid_chars_message, parse_mode="HTML")
