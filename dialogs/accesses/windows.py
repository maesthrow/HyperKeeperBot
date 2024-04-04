import operator

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back
from aiogram_dialog.widgets.text import Format, Const

from dialogs.accesses.getters import get_users_menu_data, get_from_user_folders_data, get_from_user_id
from dialogs.accesses.handlers import user_selected_handler
from handlers_pack.states import AccessesStates

users_menu_window = Window(
    Format("{message_text}"),
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


user_folders_window = Window(
    Format("{message_text}"),
        ScrollingGroup(
        Select(
            #Format("{item[name]}"),
            Const("Folder"),
            id='access_from_user_scroll',
            item_id_getter=get_from_user_id,
            items='user_folders',
            on_click=None #user_selected_handler
        ),
        id='access_from_user',
        height=5,
        width=1,
        hide_on_single_page=True
    ),
    Back(Const("↩️ Назад"), on_click=None), #on_back_click_handler),
    state=AccessesStates.ShowUserFolders,
    getter=get_from_user_folders_data
)



dialog_accesses = Dialog(
    users_menu_window,
    user_folders_window,
)
