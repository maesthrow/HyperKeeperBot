from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format

from dialogs.widgets import InlineQueryButton
from handlers.dialog.folder_control_handler import pin_code_handler, access_menu_handler, statistic_handler, \
    delete_all_items_handler, rename_folder_handler, delete_folder_handler, search_in_folder_handler, \
    close_menu_handler, access_delete_all_items_handler, info_message_ok_handler, cancel_delete_handler, \
    access_delete_handler, access_confirm_ok_handler, access_confirm_reject_handler
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID


def _search_mode_is_visible(data: dict, widget, context) -> bool:
    return False


def _is_not_root_folder(data: dict, widget, context) -> bool:
    return data.get('folder_id', '') != ROOT_FOLDER_ID


def _has_access_users(data: dict, widget, context) -> bool:
    result = data.get('folder_has_access_users', False)
    return result


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
    Button(Const("👥 Выбрать пользователя"), id="access_choose_user", on_click=access_menu_handler,
           when=_has_access_users),  # 👤
    Button(Const("🚫 Приостановить доступ для всех"), id="access_stop_all", on_click=statistic_handler,
           when=_has_access_users),
    Button(Const("↩️ Назад"), id="access_menu_back", on_click=info_message_ok_handler),
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
    Button(Const("✔️ Да, удалить"), id="delete_all_items", on_click=access_delete_all_items_handler,
           when=_folder_has_items),
    Button(Const("✖️ Не удалять"), id="not_delete_all_items", on_click=cancel_delete_handler,
           when=_folder_has_items),
    Button(Const("✖️ Закрыть"), id="ok_has_not_items", on_click=cancel_delete_handler, when=_folder_has_not_items),
]

_folder_control_delete_buttons = [
    Button(Const("✔️ Да, удалить"), id="delete_all_items", on_click=access_delete_handler),
    Button(Const("✖️ Не удалять"), id="not_delete_all_items", on_click=cancel_delete_handler),
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


def folder_control_info_message() -> widgets:
    keyboard = [Row(Button(Const("OK"), id="info_ok", on_click=info_message_ok_handler))]
    return keyboard


def folder_control_after_delete_message() -> widgets:
    keyboard = [Row(Button(Const("OK"), id="after_delete_ok", on_click=close_menu_handler))]
    return keyboard


def folder_control_access_menu() -> widgets:
    keyboard = [
        Row(_folder_control_access_menu_buttons[0]),
        Row(_folder_control_access_menu_buttons[1]),
        Row(_folder_control_access_menu_buttons[2]),
        Row(_folder_control_access_menu_buttons[3]),
    ]
    return keyboard


def folder_control_access_confirm() -> widgets:
    keyboard = [
        Row(
            Button(text=Const("✔️ Подтвердить"), id="access_confirm_ok", on_click=access_confirm_ok_handler),
            Button(text=Const("✖️ Отклонить"), id="access_confirm_reject", on_click=access_confirm_reject_handler)
        ),
    ]
    return keyboard
