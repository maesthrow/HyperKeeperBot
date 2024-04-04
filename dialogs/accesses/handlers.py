from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from handlers_pack.states import AccessesStates


async def user_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, user_id):
    data = dialog_manager.current_context().dialog_data
    folder_id = data.get('folder_id', None)
    folder_name = data.get('folder_name', None)
    users = data.get('users')
    user = next(filter(lambda _user: _user['user_id'] == user_id, users), None)
    dialog_manager.current_context().dialog_data = {
        'user': user, 'folder_name': folder_name, 'folder_id': folder_id
    }
    await dialog_manager.switch_to(AccessesStates.ShowUserFolders)
