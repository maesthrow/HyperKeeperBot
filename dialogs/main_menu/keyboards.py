from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Button, Column, Row
from aiogram_dialog.widgets.text import Const

from dialogs.main_menu.handlers import *
from dialogs.widgets import InlineQueryButton
from utils.utils_ import smile_folder, smile_item, smile_file

_main_menu_buttons = [
    Button(Const("🗂️ Открыть хранилище"), id="open_storage", on_click=open_storage_handler),
    Button(Const("🔐 Доступы от других пользователей"), id="accesses_menu", on_click=accesses_menu_handler),
    Button(Const("🔍️ Live-поиск"), id="search_menu", on_click=search_menu_handler),
    Button(Const("👤 Мой профиль"), id="user_profile", on_click=user_profile_handler),
    Button(Const("⚙️ Настройки"), id="settings_menu", on_click=settings_menu_handler),
    Button(Const("❔ Помощь"), id="help_menu", on_click=help_menu_handler),
    #Button(Const("✖️ Закрыть меню"), id="close_main_menu", on_click=close_main_menu_handler),
]

_live_search_buttons = [
    InlineQueryButton(
        Const(f"🔍 Глобальный поиск 🌐"),
        id="global_search",
        switch_inline_query_current_chat=Const("")
    ),
    InlineQueryButton(
        Const(f"🔍 Поиск папок {smile_folder}"),
        id="folders_search",
        switch_inline_query_current_chat=Const("folders/")
    ),
    InlineQueryButton(
        Const(f"🔍 Поиск записей {smile_item}"),
        id="items_search",
        switch_inline_query_current_chat=Const("items/")
    ),
    InlineQueryButton(
        Const(f"🔍 Поиск файлов {smile_file}"),
        id="files_search",
        switch_inline_query_current_chat=Const("files/")
    ),
]


def main_menu() -> widgets:
    keyboard = [
        Column(*_main_menu_buttons)
    ]
    return keyboard


def live_search() -> widgets:
    keyboard = [
        Column(*_live_search_buttons)
    ]
    return keyboard


# def to_main_menu_button() -> widgets:
#     keyboard = [
#         Row(Button(text=Const("☰ Меню"), id="main_menu", on_click=open_main_menu_handler))
#     ]
#     return keyboard


def to_main_menu_button():
    return Button(text=Const("☰ Меню"), id="main_menu", on_click=open_main_menu_handler)

