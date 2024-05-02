import asyncio

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select, Button

from dialogs.general_handlers import try_delete_message
from handlers_pack.states import AccessesState, MainMenuState
from utils.utils_ import get_level_folders, smile_folder
from utils.utils_folders_reader import get_folder_name


async def user_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, user_id):
    data = dialog_manager.current_context().dialog_data
    users = data.get('users')
    user = next(filter(lambda _user: _user['from_user_id'] == user_id, users), None)
    dialog_manager.current_context().dialog_data = {
        'user': user,
    }
    await dialog_manager.switch_to(AccessesState.ShowUserFolders)


async def back_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    start_data = dialog_manager.current_context().start_data
    start_message: Message = start_data.get('start_message', None)
    await dialog_manager.start(MainMenuState.Menu)
    await try_delete_message(start_message)


async def to_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    start_data = dialog_manager.current_context().start_data
    start_message: Message = start_data.get('start_message', None)
    tasks = [
        dialog_manager.start(MainMenuState.Menu),
        #try_delete_message(callback.message),
    ]
    if start_message:
        tasks.append(try_delete_message(start_message))
    await asyncio.gather(*tasks)


async def access_folder_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, folder_id):
    data = dialog_manager.current_context().dialog_data
    folders = data.get('user_folders')
    folder_dict = next(filter(lambda _folder: _folder['folder_id'] == folder_id, folders), None)
    folder_name = await get_folder_name(folder_dict['from_user_id'], folder_id)
    folder_path = f'{smile_folder} {folder_name} /'
    if get_level_folders(folder_id) > 0:
        folder_path = f'.. / {folder_path}'
    dialog_data = {
        'user': data['user'],
        'folder_dict': folder_dict,
        'folder_path': folder_path,
    }
    dialog_manager.current_context().dialog_data = dialog_data
    await dialog_manager.switch_to(AccessesState.ShowSelectedUserFolder)


async def folder_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, folder_id):
    data = dialog_manager.current_context().dialog_data
    folders = data.get('user_folders')
    folder_dict = next(filter(lambda _folder: _folder['folder_id'] == folder_id, folders), None)
    folder_name = await get_folder_name(folder_dict['from_user_id'], folder_id)
    folder_path = data['folder_path']
    folder_path += f' {smile_folder} {folder_name} /'
    dialog_data = {
        'user': data['user'],
        'folder_dict': folder_dict,
        'folder_path': folder_path,
        'back_data': data.get('back_data', None)
    }
    dialog_manager.current_context().dialog_data = dialog_data
    await dialog_manager.switch_to(AccessesState.ShowSelectedUserFolder)


async def on_back_folder_click_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    back_data = data.get('back_data', None)
    if back_data:
        back_data = back_data.get('back_data', None)
        if back_data:
            dialog_manager.current_context().dialog_data = back_data
            await dialog_manager.switch_to(AccessesState.ShowSelectedUserFolder)
        else:
            await dialog_manager.back()
    else:
        await dialog_manager.back()
