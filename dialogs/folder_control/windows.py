import operator

from aiogram.enums import ParseMode
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Back
from aiogram_dialog.widgets.text import Format, Const

from dialogs.folder_control import keyboards
from dialogs.folder_control.filters import filter_invalid_chars
from dialogs.folder_control.getters import get_main_menu_data, get_message_text, get_statistic_data, \
    get_delete_all_items_data, get_rename_data, get_delete_data, get_access_menu_data, get_start_data_message_text, \
    get_user_selected_data, get_stop_all_users_access_data
from dialogs.folder_control.handlers import on_rename_folder, on_error_rename_folder, cancel_delete_handler, \
    access_user_selected_handler, access_confirm_message_handler, on_back_click_handler
from handlers_pack.states import FolderControlState

folder_control_main_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_main_menu(),
    state=FolderControlState.MainMenu,
    getter=get_main_menu_data
)

folder_control_info_message_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_info_message(),
    state=FolderControlState.InfoMessage,
    getter=get_message_text
)

folder_control_statistic_window = Window(
    Format("{folder_statistic_text}"),
    *keyboards.folder_control_statistic(),
    state=FolderControlState.StatisticMenu,
    getter=get_statistic_data
)

folder_control_delete_all_items_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_delete_all_items(),
    state=FolderControlState.DeleteAllItemsQuestion,
    getter=get_delete_all_items_data
)

folder_control_rename_window = Window(
    Format("{message_text}"),
    TextInput(
        id="new_folder_name",
        on_success=on_rename_folder,
        on_error=on_error_rename_folder,
        filter=filter_invalid_chars),
    Button(id='cancel_rename', text=Format('{btn_cancel}'), on_click=cancel_delete_handler),
    state=FolderControlState.Rename,
    getter=get_rename_data,
    parse_mode=ParseMode.MARKDOWN_V2
)

folder_control_delete_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_delete(),
    state=FolderControlState.Delete,
    getter=get_delete_data
)

folder_control_after_delete_message_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_after_delete_message(),
    state=FolderControlState.AfterDelete,
    getter=get_message_text
)

folder_control_access_menu_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_access_menu(0),
    ScrollingGroup(
        Select(
            Format("{item[name]}"),
            id='access_choose_users_scroll',
            item_id_getter=operator.itemgetter('user_id'),
            items='users',
            on_click=access_user_selected_handler
        ),
        id='access_choose_users',
        height=5,
        width=1,
        hide_on_single_page=True
    ),
    *keyboards.folder_control_access_menu(1, 2),
    state=FolderControlState.AccessMenu,
    getter=get_access_menu_data
)

folder_control_access_confirm_window = Window(
    Format("{message_text}"),
    Button(id='access_confirm', text=Const('Ok'), on_click=access_confirm_message_handler),
    state=FolderControlState.AccessConfirm,
    getter=get_start_data_message_text
)

folder_control_access_user_selected_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_user_selected(),
    Back(Const("↩️ Назад"), on_click=on_back_click_handler),
    state=FolderControlState.AccessUserSelected,
    getter=get_user_selected_data
)

folder_control_info_message_access_user_selected_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_info_message_access_user_selected(),
    state=FolderControlState.InfoMessageAccessUserSelected,
    getter=get_message_text
)

folder_control_stop_all_users_access_window = Window(
    Format("{message_text}"),
    *keyboards.stop_all_users_access(),
    state=FolderControlState.StopAllUsersAccess,
    getter=get_stop_all_users_access_data
)

folder_control_after_stop_all_users_access_window = Window(
    Format("{message_text}"),
    Button(id='after_stop_access', text=Const('Ok'), on_click=access_confirm_message_handler),
    state=FolderControlState.AfterStopAllUsersAccess,
    getter=get_message_text
)

dialog_folder_control = Dialog(
    folder_control_main_window,
    folder_control_info_message_window,
    folder_control_statistic_window,
    folder_control_delete_all_items_window,
    folder_control_rename_window,
    folder_control_delete_window,
    folder_control_after_delete_message_window,
    folder_control_access_menu_window,
    folder_control_access_confirm_window,
    folder_control_access_user_selected_window,
    folder_control_info_message_access_user_selected_window,
    folder_control_stop_all_users_access_window,
    folder_control_after_stop_all_users_access_window
)
