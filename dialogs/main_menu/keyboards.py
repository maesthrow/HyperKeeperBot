from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Button, Column
from aiogram_dialog.widgets.text import Const

from dialogs.main_menu.handlers import *

_main_menu_buttons = [
    Button(Const("🗂️ Открыть хранилище"), id="open_storage", on_click=open_storage_handler),
    Button(Const("🔐 Доступы от других пользователей"), id="accesses_menu", on_click=accesses_menu_handler),
    Button(Const("🔍️ Live-поиск"), id="search_menu", on_click=search_menu_handler),
    Button(Const("👤 Мой профиль"), id="user_profile", on_click=user_profile_handler),
    Button(Const("⚙️ Настройки"), id="settings_menu", on_click=settings_menu_handler),
    Button(Const("❔ Помощь"), id="help_menu", on_click=help_menu_handler),
    #Button(Const("✖️ Закрыть меню"), id="close_main_menu", on_click=close_main_menu_handler),
]


def main_menu() -> widgets:
    keyboard = [
        Column(*_main_menu_buttons)
    ]
    return keyboard
