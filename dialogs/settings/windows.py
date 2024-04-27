from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from dialogs import general_keyboards
from dialogs.general_handlers import open_main_menu_handler
from dialogs.settings import keyboards
from dialogs.settings.getters import get_language_data, get_folders_on_page_count_data, get_items_on_page_count_data, \
    get_settings_menu_data
from handlers_pack.states import SettingsMenuState

settings_menu_window = Window(
    Format("{message_text}"),
    *keyboards.settings_menu(),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=SettingsMenuState.Menu,
    getter=get_settings_menu_data
)

language_menu_window = Window(
    Const("<b>⚙️ Настройки > 🌐 Язык интерфейса</b>"),
    keyboards.languages_buttons(),
    state=SettingsMenuState.Language,
    getter=get_language_data
)


folders_on_page_count_menu_window = Window(
    Const("<b>⚙️ Настройки > 🗂️ Количество папок на странице</b>"),
    *keyboards.folders_count_buttons(),
    state=SettingsMenuState.FoldersOnPageCount,
    getter=get_folders_on_page_count_data
)


items_on_page_count_menu_window = Window(
    Const("<b>⚙️ Настройки > 📄 Количество записей на странице</b>"),
    *keyboards.items_count_buttons(),
    state=SettingsMenuState.ItemsOnPagesCount,
    getter=get_items_on_page_count_data
)

dialog_settings_menu = Dialog(
    settings_menu_window,
    language_menu_window,
    folders_on_page_count_menu_window,
    items_on_page_count_menu_window,
)
