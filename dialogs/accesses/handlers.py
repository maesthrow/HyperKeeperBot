from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select

from handlers_pack.states import AccessesStates


async def user_selected_handler(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, user_id):
    data = dialog_manager.current_context().dialog_data
    users = data.get('users')
    user = next(filter(lambda _user: _user['from_user_id'] == user_id, users), None)
    dialog_manager.current_context().dialog_data = {
        'user': user,
    }
    await dialog_manager.switch_to(AccessesStates.ShowUserFolders)
