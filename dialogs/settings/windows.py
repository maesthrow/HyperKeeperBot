from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Back, Checkbox, Column, Button
from aiogram_dialog.widgets.text import Const

from dialogs import general_keyboards
from dialogs.settings import keyboards
from dialogs.settings.getters import get_language_data
from dialogs.settings.handlers import language_changed, on_back_settings_click_handler
from handlers_pack.states import SettingsMenuState

settings_menu_window = Window(
    Const("⚙️ <b>Настройки</b>"),
    *keyboards.settings_menu(),
    general_keyboards.to_main_menu_button(),
    state=SettingsMenuState.Menu,
    # getter=get_main_menu_data
)

language_menu_window = Window(
    Const("<b>⚙️ Настройки > 🌐 Язык интерфейса</b>"),
    keyboards.languages_buttons(),
    state=SettingsMenuState.Language,
    getter=get_language_data
)


folders_count_menu_window = Window(
    Const("<b>⚙️ Настройки > 🗂️ Количество папок на странице</b>"),
    *keyboards.folders_count_buttons(),
    state=SettingsMenuState.FoldersOnPageCount,
    getter=get_language_data
)

dialog_settings_menu = Dialog(
    settings_menu_window,
    language_menu_window,
    folders_count_menu_window
)
