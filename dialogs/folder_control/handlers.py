import asyncio

from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select

from callbacks.callbackdata import FolderCallback
from enums.enums import AccessType
from handlers_pack.handlers_folder import show_folders, to_folder
from handlers_pack.states import FolderControlState
from load_all import bot
from models.access_folder_model import AccessFolder
from models.folder_model import Folder
from utils.data_manager import get_data, set_data
from utils.utils_ import smile_folder
from utils.utils_access import get_user_info
from utils.utils_accesses_folders_db import util_access_delete_from_user_folder, util_access_edit_from_user_folder
from utils.utils_button_manager import get_pin_control_inline_markup, get_folder_pin_inline_markup
from utils.utils_data import get_current_folder_id
from utils.utils_folders import invalid_chars, get_parent_folder_id
from utils.utils_folders_db import util_rename_folder, util_delete_folder
from utils.utils_folders_reader import get_folder_name, get_folder
from utils.utils_items_db import util_delete_all_items_in_folder

### НЕЛЬЗЯ УБИРАТЬ! ###
import handlers_pack.handlers_access
h_a = handlers_pack.handlers_access
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
    await dialog_manager.switch_to(FolderControlState.AccessMenu)


async def statistic_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlState.StatisticMenu)


async def delete_all_items_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlState.DeleteAllItemsQuestion)


async def rename_folder_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    data = await get_data(user_id)
    data['any_message_ignore'] = True
    await set_data(user_id, data)
    await dialog_manager.switch_to(FolderControlState.Rename)


async def delete_folder_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlState.Delete)


async def search_in_folder_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def close_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.delete()


async def confirm_delete_all_items_handler(
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
    await dialog_manager.switch_to(FolderControlState.InfoMessage)


async def info_message_ok_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlState.MainMenu)


async def cancel_delete_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    data = await get_data(user_id)
    data['any_message_ignore'] = False
    await set_data(user_id, data)
    await dialog_manager.switch_to(FolderControlState.MainMenu)


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
    data = await get_data(user_id)
    data['any_message_ignore'] = False
    await set_data(user_id, data)
    await show_folders(user_id, need_to_resend=True)
    await dialog_manager.switch_to(FolderControlState.InfoMessage)


async def on_error_rename_folder(data, widget, dialog_manager):
    new_folder_name = data.get_value()
    invalid_chars_list = ' '.join([char for char in invalid_chars if char in new_folder_name])
    invalid_chars_message = f"❗Название папки содержит недопустимые символы:" \
                            f"\n{invalid_chars_list}" \
                            f"\n\n<i>Придумайте другое название:</i>"
    await dialog_manager.dialog().bot.send_message(
        dialog_manager.event.from_user.id, invalid_chars_message, parse_mode="HTML"
    )


async def confirm_delete_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    try:
        # Вызываем метод для удаления папки
        result = await util_delete_folder(user_id, folder_id)
        if result:
            message_text = f"Папка {smile_folder} '{folder_name}' удалена ☑️"
            parent_folder_id = get_parent_folder_id(folder_id)
            dialog_manager.current_context().dialog_data["message_text"] = message_text
            await dialog_manager.switch_to(FolderControlState.AfterDelete)
            await to_folder(user_id=user_id, callback_data=FolderCallback(folder_id=parent_folder_id))
            return
        else:
            message_text = f"Не получилось удалить папку {smile_folder} '{folder_name}'"
    except:
        message_text = f"Что то пошло не так при удалении папки"

    dialog_manager.current_context().dialog_data["message_text"] = message_text
    await dialog_manager.switch_to(FolderControlState.InfoMessage)


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
    await dialog_manager.switch_to(FolderControlState.AccessMenu)


async def access_user_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, user_id):
    data = dialog_manager.current_context().dialog_data
    folder_id = data.get('folder_id', None)
    folder_name = data.get('folder_name', None)
    users = data.get('users')
    user = next(filter(lambda _user: _user['user_id'] == user_id, users), None)
    dialog_manager.current_context().dialog_data = {
        'user': user, 'folder_name': folder_name, 'folder_id': folder_id
    }
    await dialog_manager.switch_to(FolderControlState.AccessUserSelected)


async def access_user_expand_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await edit_access_for_user(dialog_manager, AccessType.WRITE)


async def access_user_decrease_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await edit_access_for_user(dialog_manager, AccessType.READ)


async def access_user_stop_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await edit_access_for_user(dialog_manager, AccessType.ABSENSE)


async def info_message_access_user_selected_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlState.AccessMenu)


async def edit_access_for_user(dialog_manager: DialogManager, access_type: AccessType):
    data = dialog_manager.current_context().dialog_data
    user = data.get('user')
    accessing_user_id = user.get('user_id')
    folder_id = data.get('folder_id')
    folder_name = data.get('folder_name')
    from_user_id = dialog_manager.event.from_user.id
    folder: Folder = await get_folder(from_user_id, folder_id)

    if access_type == AccessType.ABSENSE:
        result_change = await get_result_delete_access(from_user_id, accessing_user_id, folder)
    else:
        result_change = await get_result_edit_access(from_user_id, accessing_user_id, folder, access_type)

    if result_change:
        user_name = await get_user_info(accessing_user_id)
        from_user_name = await get_user_info(str(from_user_id))
        folder_full_name = await folder.get_full_name()
        if access_type == AccessType.ABSENSE:
            message_text = f'Доступ к папке {smile_folder} {folder_name} приостановлен для пользователя {user_name}'
            accessing_user_message_text = (f'Пользователь {from_user_name} приостановил для вас доступ к его папке'
                                           f'\n\n{folder_full_name}')
        else:
            access_str = 'Только просмотр 👁️' if access_type == AccessType.READ else 'Просмотр и редактирование ✏️'
            message_text = (f'Для пользователя {user_name} изменен доступ к содержимому вашей папки:'
                            f'\n\n{smile_folder} {folder_name}\n\n<i><b>{access_str}</b></i>')
            accessing_user_message_text = (f'Пользователь {from_user_name} изменил для вас доступ к содержимому '
                                           f'его папки\n\n{folder_full_name}\n\n<i><b>{access_str}</b></i>')

        await h_a.sent_message_to_accessing_user(accessing_user_id, accessing_user_message_text)
    else:
        message_text = "Что то пошло не так."
    dialog_manager.current_context().dialog_data["message_text"] = message_text
    await dialog_manager.switch_to(FolderControlState.InfoMessageAccessUserSelected)


async def get_result_full_delete_access(from_user_id, accessing_users: list, folder):
    result_accessing_users = []
    for user in accessing_users:
        user_id = user.get('user_id', None)
        access_from_user_changed = await util_access_delete_from_user_folder(user_id, from_user_id, folder.folder_id)
        if access_from_user_changed:
            result_accessing_users.append(user)

    if len(result_accessing_users) == len(accessing_users):
        user_from_access_changed = await h_a.delete_all_users_from_folder_access(folder)
    else:
        for user in result_accessing_users:
            user_id = user.get('user_id', None)
            await h_a.delete_user_from_folder_access(user_id, folder)
    return result_accessing_users


async def get_result_delete_access(from_user_id, accessing_user_id, folder):
    access_from_user_changed = await util_access_delete_from_user_folder(
        accessing_user_id, from_user_id, folder.folder_id
    )
    if access_from_user_changed:
        user_from_access_changed = await h_a.delete_user_from_folder_access(accessing_user_id, folder)
    else:
        user_from_access_changed = False
    return access_from_user_changed and user_from_access_changed


async def get_result_edit_access(from_user_id, accessing_user_id, folder, access_type: AccessType):
    access_folder = AccessFolder(accessing_user_id, from_user_id, folder.folder_id, access_type)
    access_from_user_changed = await util_access_edit_from_user_folder(access_folder)
    if access_from_user_changed:
        user_from_access_changed = await h_a.edit_user_to_folder_access(accessing_user_id, folder, access_type)
    else:
        user_from_access_changed = False
    return access_from_user_changed and user_from_access_changed


async def stop_all_users_access_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    folder_id = data.get('folder_id', None)
    folder_name = data.get('folder_name', None)
    users = data.get('users')
    dialog_manager.current_context().dialog_data = {
        'users': users, 'folder_name': folder_name, 'folder_id': folder_id
    }
    await dialog_manager.switch_to(FolderControlState.StopAllUsersAccess)


async def confirm_stop_all_users_access_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    from_user_id = dialog_manager.event.from_user.id
    data = dialog_manager.current_context().dialog_data
    users = data.get('users')
    folder_id = data.get('folder_id')
    folder: Folder = await get_folder(from_user_id, folder_id)
    result_accessing_users = await get_result_full_delete_access(from_user_id, users, folder)

    from_user_name = await get_user_info(str(from_user_id))
    folder_full_name = await folder.get_full_name()
    tasks = []
    for user in result_accessing_users:
        accessing_user_message_text = f'Пользователь {from_user_name} приостановил для вас доступ к его папке:'\
                                      f'\n\n{folder_full_name}'
        tasks.append(h_a.sent_message_to_accessing_user(user['user_id'], accessing_user_message_text))
    await asyncio.gather(*tasks)

    if len(result_accessing_users) == len(users):
        message_text = f'Доступ к папке {smile_folder} {folder.name}\nприостановлен для всех пользователей.'
    else:
        message_text = (f'Что то пошло не так при попытке приостановить доступ к папке '
                        f'{smile_folder} {folder.name} для некоторых пользователей.\nПопробуйте повторить еще раз.')
    dialog_manager.current_context().dialog_data["message_text"] = message_text
    await dialog_manager.switch_to(FolderControlState.AfterStopAllUsersAccess)


async def cancel_stop_all_users_access_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FolderControlState.AccessMenu)


async def on_back_click_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()
