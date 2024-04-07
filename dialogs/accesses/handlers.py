from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Button

from handlers_pack.handlers_folder import show_folders
from handlers_pack.states import AccessesStates


async def user_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, user_id):
    data = dialog_manager.current_context().dialog_data
    users = data.get('users')
    user = next(filter(lambda _user: _user['from_user_id'] == user_id, users), None)
    dialog_manager.current_context().dialog_data = {
        'user': user,
    }
    await dialog_manager.switch_to(AccessesStates.ShowUserFolders)


async def close_users_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.delete()


async def access_folder_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, folder_id):
    data = dialog_manager.current_context().dialog_data
    folders = data.get('user_folders')
    print(f'folders {folders}')
    folder_dict = next(filter(lambda _folder: _folder['folder_id'] == folder_id, folders), None)
    dialog_manager.current_context().dialog_data = {
        'user': data['user'],
        'access_folder_dict': folder_dict,
    }
    await dialog_manager.switch_to(AccessesStates.ShowSelectedUserFolder)


async def folder_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, folder_id):
    data = dialog_manager.current_context().dialog_data
    folders = data.get('user_folders')
    print(f'folders {folders}')
    folder_dict = next(filter(lambda _folder: _folder['folder_id'] == folder_id, folders), None)
    dialog_manager.current_context().dialog_data = {
        'user': data['user'],
        'folder_dict': folder_dict,
    }
    await dialog_manager.switch_to(AccessesStates.ShowSelectedUserFolder)
