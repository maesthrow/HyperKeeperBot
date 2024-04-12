from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

from dialogs.settings.handlers import language_menu_handler

_settings_menu_buttons = [
    Button(Const("🗂️ Количество папок на странице"), id="open_storage", on_click=None),
    Button(Const("📄 Количество записей на странице"), id="accesses_menu", on_click=None),
    Button(Const("🌐 Язык интерфейса"), id="search_menu", on_click=language_menu_handler),
]


def settings_menu() -> widgets:
    keyboard = [
        Column(*_settings_menu_buttons)
    ]
    return keyboard
