import operator

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from dialogs.accesses import keyboards
from dialogs.accesses.getters import get_users_menu_data
from dialogs.accesses.handlers import user_selected_handler
from handlers_pack.states import AccessesStates

users_menu_window = Window(
    Format("{message_text}"),
    #*keyboards.folder_control_main_menu(),
    ScrollingGroup(
        Select(
            Format("{item[name]}"),
            id='access_from_users_scroll',
            item_id_getter=operator.itemgetter('from_user_id'),
            items='users',
            on_click=user_selected_handler
        ),
        id='access_from_users',
        height=5,
        width=1,
        hide_on_single_page=True
    ),
    state=AccessesStates.UsersMenu,
    getter=get_users_menu_data
)

dialog_accesses = Dialog(
    users_menu_window,
)