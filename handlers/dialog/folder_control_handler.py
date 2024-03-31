from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select

from callbacks.callbackdata import FolderCallback
from handlers.handlers_folder import show_folders, to_folder
from handlers.states import FolderControlStates
from load_all import bot
from models.folder_model import Folder
from utils.utils_ import smile_folder
from utils.utils_access import get_user_info
from utils.utils_accesses_folders_db import util_access_delete_from_user_folder
from utils.utils_button_manager import get_pin_control_inline_markup, get_folder_pin_inline_markup
from utils.utils_data import get_current_folder_id
from utils.utils_folders import invalid_chars, get_parent_folder_id
from utils.utils_folders_db import util_rename_folder, util_delete_folder
from utils.utils_folders_reader import get_folder_name, get_folder
from utils.utils_items_db import util_delete_all_items_in_folder

### НЕЛЬЗЯ УБИРАТЬ! ###
import handlers.handlers_access
h_a = handlers.handlers_access
#################################


async def pin_code_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder: Folder = await get_folder(user_id, folder_id)
    # folder_long_name = await get_folders_message_text(user_id, folder_id)
    pin = folder.get_pin()
    if pin:
        inline_markup = get_pin_control_inline_markup(folder_id)
        message_text = f'🔑 *Управление PIN\-кодом папки*\n\n{smile_folder} {folder.name}'
    else:
        inline_markup = get_folder_pin_inline_markup(user_id, folder_id)
        message_text = f'_Придумайте PIN\-код для папки:_\n\n{smile_folder} {folder.name}'

    await dialog_manager.done()

    await callback.message.delete()
    await bot.send_message(
        chat_id=user_id,
        text=message_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inline_markup
    )


async def access_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.AccessMenu)


async def statistic_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.StatisticMenu)


async def delete_all_items_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.DeleteAllItemsQuestion)


async def rename_folder_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.Rename)


async def delete_folder_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.Delete)


async def search_in_folder_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def close_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    #await DialogData.clear_manager(callback.from_user.id)
    await callback.message.delete()


async def access_delete_all_items_handler(
        callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    user_id = dialog_manager.event.from_user.id
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

    dialog_manager.current_context().dialog_data["message_text"] = message_text
    await dialog_manager.switch_to(FolderControlStates.InfoMessage)


async def info_message_ok_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.MainMenu)


async def cancel_delete_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.MainMenu)


async def on_rename_folder(
        message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, input_text
):
    user_id = message.from_user.id
    folder_id = await get_current_folder_id(user_id)
    result = await util_rename_folder(user_id, folder_id, input_text)
    if result:
        message_text = "Папка успешно переименована ✅"
    else:
        message_text = "Что то пошло не так при редактировании папки ❌"
    dialog_manager.current_context().dialog_data["message_text"] = message_text
    await show_folders(user_id, need_to_resend=True)
    await dialog_manager.switch_to(FolderControlStates.InfoMessage)


async def on_error_rename_folder(data, widget, dialog_manager):
    new_folder_name = data.get_value()
    invalid_chars_list = ' '.join([char for char in invalid_chars if char in new_folder_name])
    invalid_chars_message = f"❗Название папки содержит недопустимые символы:" \
                            f"\n{invalid_chars_list}" \
                            f"\n\n<i>Придумайте другое название:</i>"
    await dialog_manager.dialog().bot.send_message(
        dialog_manager.event.from_user.id, invalid_chars_message, parse_mode="HTML"
    )


async def access_delete_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    try:
        # Вызываем метод для удаления папки
        result = await util_delete_folder(user_id, folder_id)
        if result:
            message_text = f"Папка {smile_folder} '{folder_name}' удалена ☑️"
            parent_folder_id = get_parent_folder_id(folder_id)
            await to_folder(call=callback, callback_data=FolderCallback(folder_id=parent_folder_id))
            dialog_manager.current_context().dialog_data["message_text"] = message_text
            await dialog_manager.switch_to(FolderControlStates.AfterDelete)
            return
        else:
            message_text = f"Не получилось удалить папку {smile_folder} '{folder_name}'"
    except:
        message_text = f"Что то пошло не так при удалении папки"

    dialog_manager.current_context().dialog_data["message_text"] = message_text
    await dialog_manager.switch_to(FolderControlStates.InfoMessage)


# async def access_confirm_ok_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     user_id = callback.from_user.id
#     data = await get_data(user_id)
#     access_folder_confirm: AccessFolder = data.get('access_folder_confirm', None)
#     if access_folder_confirm:
#         from_user_message_text, accessing_user_message_text = await get_access_confirm_ok_messages(user_id)
#         dialog_manager.current_context().dialog_data["message_text"] = from_user_message_text
#         await dialog_manager.switch_to(FolderControlStates.AccessConfirm)


# async def access_confirm_reject_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     user_id = callback.from_user.id
#     data = await get_data(user_id)
#     access_folder_confirm: AccessFolder = data.get('access_folder_confirm', None)
#     if access_folder_confirm:
#         from_user_message_text, accessing_user_message_text = await get_access_confirm_reject_messages(user_id)
#         dialog_manager.current_context().dialog_data["message_text"] = from_user_message_text
#         await dialog_manager.switch_to(FolderControlStates.AccessConfirm)


async def access_confirm_message_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.AccessMenu)


async def access_choose_users_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.AccessChooseUsers)


async def access_user_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, user_id):
    data = dialog_manager.current_context().dialog_data
    folder_id = data.get('folder_id', None)
    folder_name = data.get('folder_name', None)
    users = data.get('users')
    user = next(filter(lambda _user: _user['user_id'] == user_id, users), None)
    dialog_manager.current_context().dialog_data = {
        'user': user, 'folder_name': folder_name, 'folder_id': folder_id
    }
    await dialog_manager.switch_to(FolderControlStates.AccessUserSelected)


async def access_user_expand_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def access_user_decrease_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def access_user_stop_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    user = data.get('user')
    accessing_user_id = user.get('user_id')
    folder_id = data.get('folder_id')
    folder_name = data.get('folder_name')
    from_user_id = dialog_manager.event.from_user.id

    print(f'{accessing_user_id} {from_user_id} {folder_id}')
    folder: Folder = await get_folder(from_user_id, folder_id)
    access_from_user_deleted = await util_access_delete_from_user_folder(accessing_user_id, from_user_id, folder_id)
    if access_from_user_deleted:
        user_from_access_deleted = await h_a.delete_user_from_folder_access(accessing_user_id, folder)
    else:
        user_from_access_deleted = False
    if access_from_user_deleted and user_from_access_deleted:
        user_name = await get_user_info(accessing_user_id)
        message_text = f"Доступ к папке {smile_folder} {folder_name} приостановлен для пользователя {user_name}"
        from_user_name = await get_user_info(str(from_user_id))
        folder_full_name = await folder.get_full_name()
        accessing_user_message_text = (f"Пользователь {from_user_name} приостановил для вас доступ к его папке "
                                       f"{folder_full_name}")
        await h_a.sent_message_to_accessing_user(accessing_user_id, accessing_user_message_text)
    else:
        message_text = "Что то пошло не так."
    dialog_manager.current_context().dialog_data["message_text"] = message_text
    await dialog_manager.switch_to(FolderControlStates.InfoMessageAccessUserSelected)


async def info_message_access_user_selected_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlStates.AccessMenu)


async def on_back_click_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()
