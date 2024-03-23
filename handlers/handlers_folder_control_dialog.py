from aiogram_dialog import Window, Dialog
from aiogram_dialog.setup import DialogRegistry
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const

from handlers.states import FolderControlStates
from load_all import dp




buttons = [
    Button(Const("🔑 PIN-код"), id="pin_code", on_click=pin_code_handler),
    Button(Const("🔐 Настроить доступ"), id="access_settings", on_click=access_settings_handler),
    Button(Const("📊 Статистика"), id="statistic", on_click=access_settings_handler),
    Button(Const("🧹Удалить все записи"), id="delete_all_items", on_click=access_settings_handler),
    Button(Const("✏️ Переименовать"), id="rename_folder", on_click=access_settings_handler),
    Button(Const("🗑 Удалить папку"), id="delete_folder", on_click=access_settings_handler),
    Button(Const("🔍 Поиск в папке и вложенных папках"), id="search_in_folder", on_click=access_settings_handler),
    Button(Const("✖️ Закрыть меню"), id="close_menu", on_click=access_settings_handler),
]

folder_control_menu_window = Window(
    Row(*buttons[:2]),
    Row(*buttons[2:4]),
    Row(*buttons[4:6]),
    Row(buttons[6]),
    Row(buttons[7]),
    state=FolderControlStates.MainMenu,
    # Можно добавить обработчики событий, если нужно
)

dialog = Dialog(folder_control_menu_window)
registry = DialogRegistry(dp)  # dp - ваш Dispatcher
