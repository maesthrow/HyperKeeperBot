from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Row, Column
from aiogram_dialog.widgets.text import Const, Format

from dialogs.folder_control.handlers import *
from dialogs.widgets.inline_query_button import InlineQueryButton
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID


def _search_mode_is_visible(data: dict, widget, context) -> bool:
    return False


def _is_not_root_folder(data: dict, widget, context) -> bool:
    return data.get('folder_id', '') != ROOT_FOLDER_ID


def _has_access_users(data: dict, widget, context) -> bool:
    result = data.get('folder_has_access_users', False)
    return result


def _is_read_access_type(data: dict, widget, context) -> bool:
    user = data.get('user', None)
    access_type = AccessType(user.get('access_type', 'r')) if user else AccessType.READ
    return access_type == AccessType.READ


def _is_write_access_type(data: dict, widget, context) -> bool:
    user = data.get('user', None)
    access_type = AccessType(user.get('access_type', 'w')) if user else AccessType.READ
    return access_type == AccessType.WRITE


def _is_visible_always_false(data: dict, widget, context) -> bool:
    return False


_folder_control_main_menu_buttons = [
    Button(Const("🔑 PIN-код"), id="pin_code", on_click=pin_code_handler),
    Button(Const("🔐 Настроить доступ"), id="access_menu", on_click=access_menu_handler),
    Button(Const("📊 Статистика"), id="statistic", on_click=statistic_handler),
    Button(Const("🧹Удалить все записи"), id="delete_all_items", on_click=delete_all_items_handler),
    Button(Const("✏️ Переименовать"), id="rename_folder", on_click=rename_folder_handler, when=_is_not_root_folder),
    Button(Const("🗑 Удалить папку"), id="delete_folder", on_click=delete_folder_handler, when=_is_not_root_folder),
    Button(Const("🔍 Поиск в папке и вложенных папках"), id="search_in_folder", on_click=search_in_folder_handler,
           when=_search_mode_is_visible),
    Button(Const("✖️ Закрыть меню"), id="close_main_menu", on_click=close_menu_handler),
]

_folder_control_access_menu_buttons = [
    InlineQueryButton(Const("➕ Добавить пользователя"), id="access_add_user",
                      switch_inline_query=Format("{switch_inline_query}")),
    Button(Const("🚫 Приостановить доступ для всех"), id="access_stop_all", on_click=stop_all_users_access_handler,
           when=_has_access_users),
    Button(Const("↩️ Назад"), id="access_menu_back", on_click=info_message_ok_handler),
]

_folder_control_access_user_selected_buttons = [
    Button(Const("Расширить доступ до редактирования ✏️"), id="access_user_expand", on_click=access_user_expand_handler,
           when=_is_read_access_type),
    Button(Const("Понизить доступ только до просмотра 👁️"), id="access_user_decrease", on_click=access_user_decrease_handler,
           when=_is_write_access_type),
    Button(Const("🚫 Приостановить доступ"), id="access_user_stop", on_click=access_user_stop_handler),
]


def folder_control_main_menu() -> widgets:
    keyboard = [
        Row(*_folder_control_main_menu_buttons[:2]),
        Row(*_folder_control_main_menu_buttons[2:4]),
        Row(*_folder_control_main_menu_buttons[4:6]),
        Row(_folder_control_main_menu_buttons[6]),
        Row(_folder_control_main_menu_buttons[7]),
    ]
    return keyboard


def folder_control_statistic() -> widgets:
    keyboard = [
        Row(
            # Back(text=Const("↩️ Назад")),
            Button(text=Const("☑️ OK"), id="close_main_menu", on_click=info_message_ok_handler)  # ✅ ✔️ ☑️
            # on_click=close_menu_handler
        ),
    ]
    return keyboard


def _folder_has_items(data: dict, widget, context) -> bool:
    return data.get('items_count', 0) > 0


def _folder_has_not_items(data: dict, widget, context) -> bool:
    return not _folder_has_items(data, widget, context)


_folder_control_delete_all_items_buttons = [
    Button(Const("✔️ Да, удалить"), id="confirm_delete_all_items", on_click=confirm_delete_all_items_handler,
           when=_folder_has_items),
    Button(Const("✖️ Не удалять"), id="cancel_delete_all_items", on_click=cancel_delete_handler,
           when=_folder_has_items),
    Button(Const("Ясно"), id="ok_has_not_items", on_click=cancel_delete_handler, when=_folder_has_not_items),
]

_folder_control_delete_buttons = [
    Button(Const("✔️ Да, удалить"), id="confirm_delete_folder", on_click=confirm_delete_handler),
    Button(Const("✖️ Не удалять"), id="cancel_delete_folder", on_click=cancel_delete_handler),
]

_folder_control_stop_all_users_access_buttons = [
    Button(Const("✔️ Да"), id="yes_stop_all_users_access", on_click=confirm_stop_all_users_access_handler),
    Button(Const("✖️ Нет"), id="no_stop_all_users_access", on_click=cancel_stop_all_users_access_handler),
]


def folder_control_delete_all_items() -> widgets:
    keyboard = [
        Row(*_folder_control_delete_all_items_buttons[:2]),
        Row(_folder_control_delete_all_items_buttons[2]),
    ]
    return keyboard


def folder_control_delete() -> widgets:
    keyboard = [Row(*_folder_control_delete_buttons)]
    return keyboard


def stop_all_users_access() -> widgets:
    keyboard = [Row(*_folder_control_stop_all_users_access_buttons)]
    return keyboard


def folder_control_info_message() -> widgets:
    keyboard = [Row(Button(Const("Ok"), id="info_ok", on_click=info_message_ok_handler))]
    return keyboard


def folder_control_info_message_access_user_selected() -> widgets:
    keyboard = [Row(Button(Const("Ok"), id="info_ok", on_click=info_message_access_user_selected_handler))]
    return keyboard


def folder_control_after_delete_message() -> widgets:
    keyboard = [Row(Button(Const("Ok"), id="after_delete_ok", on_click=close_menu_handler))]
    return keyboard


def folder_control_access_menu(*args) -> widgets:
    keyboard = []
    for index in args:
        if -1 < index < len(_folder_control_access_menu_buttons):
            keyboard.append(_folder_control_access_menu_buttons[index])

    return keyboard


def folder_control_user_selected() -> widgets:
    keyboard = [Column(*_folder_control_access_user_selected_buttons)]
    return keyboard


def folder_control_access_users() -> widgets:
    return None

