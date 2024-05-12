import operator

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back, Button
from aiogram_dialog.widgets.text import Format, Const

from dialogs.accesses.getters import *
from dialogs.accesses.handlers import *
from handlers_pack.states import AccessesState

users_menu_window = Window(
    Format("{message_text}"),
    ScrollingGroup(
        Select(
            Format("{item[name]}"),
            id='access_from_users_scroll',
            item_id_getter=operator.itemgetter('from_user_id'),
            items='users',
            on_click=user_selected_handler,
        ),
        id='access_from_users',
        height=5,
        width=1,
        hide_on_single_page=True
    ),
    Button(
        text=Format("{btn_menu}"),
        id="main_menu",
        on_click=to_main_menu_handler,
    ),
    state=AccessesState.UsersMenu,
    getter=get_users_menu_data
)

user_folders_window = Window(
    Format("{message_text}"),
    ScrollingGroup(
        Select(
            Format("{item[folder_name]}"),
            id='access_user_folders_scroll',
            item_id_getter=operator.itemgetter('folder_id'),
            items='user_folders',
            on_click=access_folder_selected_handler
        ),
        id='access_from_user_folders',
        height=5,
        width=2,
        hide_on_single_page=True
    ),
    Back(text=Format("{btn_back}")),
    state=AccessesState.ShowUserFolders,
    getter=get_from_user_folders_data
)

show_selected_user_folder_window = Window(
    Format("{message_text}"),
    ScrollingGroup(
        Select(
            Format("{item[folder_name]}"),
            id='user_folders_scroll',
            item_id_getter=operator.itemgetter('folder_id'),
            items='user_folders',
            on_click=folder_selected_handler,
        ),
        id='folders_in_selected_user_folder',
        height=5,
        width=2,
        on_page_changed=None,
        hide_on_single_page=True
    ),
    ScrollingGroup(
        Select(
            Format("{item[item_title]}"),
            id='user_items_in_folder_scroll',
            item_id_getter=operator.itemgetter('item_id'),
            items='user_folder_items',
            on_click=item_selected_handler
        ),
        id='items_in_selected_user_folder',
        height=5,
        width=1,
        hide_on_single_page=True
    ),
    Button(Format("{btn_back}"), id='back_folder', on_click=on_back_folder_click_handler),
    state=AccessesState.ShowSelectedUserFolder,
    getter=get_from_user_folder_data
)

dialog_accesses = Dialog(
    users_menu_window,
    user_folders_window,
    show_selected_user_folder_window
)
