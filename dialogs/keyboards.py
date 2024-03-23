from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Button, Row, Back
from aiogram_dialog.widgets.text import Const

from handlers.dialog.folder_control_handler import pin_code_handler, access_settings_handler, statistic_handler, \
    delete_all_items_handler, rename_folder_handler, delete_folder_handler, search_in_folder_handler, \
    close_menu_handler
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID


def is_not_root_folder(data: dict, widget, context) -> bool:
    return data.get("folder_id", '') != ROOT_FOLDER_ID


_folder_control_main_menu_buttons = [
    Button(Const("🔑 PIN-код"), id="pin_code", on_click=pin_code_handler),
    Button(Const("🔐 Настроить доступ"), id="access_settings", on_click=access_settings_handler),
    Button(Const("📊 Статистика"), id="statistic", on_click=statistic_handler),
    Button(Const("🧹Удалить все записи"), id="delete_all_items", on_click=delete_all_items_handler),
    Button(Const("✏️ Переименовать"), id="rename_folder", on_click=rename_folder_handler, when=is_not_root_folder),
    Button(Const("🗑 Удалить папку"), id="delete_folder", on_click=delete_folder_handler, when=is_not_root_folder),
    Button(Const("🔍 Поиск в папке и вложенных папках"), id="search_in_folder", on_click=search_in_folder_handler),
    Button(Const("✖️ Закрыть меню"), id="close_main_menu", on_click=close_menu_handler),
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
            Back(text=Const('↩️ Назад')),
            Button(text=Const('☑️ OK'), id="close_main_menu", on_click=close_menu_handler) # ✅ ✔️ ☑️
        ),
    ]
    return keyboard
