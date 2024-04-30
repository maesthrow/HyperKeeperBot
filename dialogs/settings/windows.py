from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from dialogs import general_keyboards
from dialogs.general_handlers import open_main_menu_handler
from dialogs.settings import keyboards
from dialogs.settings.getters import get_language_data, get_folders_on_page_count_data, get_items_on_page_count_data, \
    get_settings_menu_data
from dialogs.settings.handlers import folders_on_page_count_menu_handler, items_on_page_count_menu_handler, \
    language_menu_handler, on_back_settings_click_handler
from handlers_pack.states import SettingsMenuState

settings_menu_window = Window(
    Format("{message_text}"),
    Button(Format('{btn_folders_on_page_count}'), id="open_storage", on_click=folders_on_page_count_menu_handler),
    Button(Format('{btn_items_on_page_count}'), id="accesses_menu", on_click=items_on_page_count_menu_handler),
    Button(Format('{btn_language_menu}'), id="search_menu", on_click=language_menu_handler),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=SettingsMenuState.Menu,
    getter=get_settings_menu_data
)

language_menu_window = Window(
    Format("{language_menu_text}"),
    keyboards.languages_buttons(),
    Button(text=Format("{btn_back}"), id='back', on_click=on_back_settings_click_handler),
    state=SettingsMenuState.Language,
    getter=get_language_data
)


folders_on_page_count_menu_window = Window(
    Format("{folders_on_page_count_menu_text}"),
    *keyboards.folders_count_buttons(),
    Button(text=Format("{btn_back}"), id='back', on_click=on_back_settings_click_handler),
    state=SettingsMenuState.FoldersOnPageCount,
    getter=get_folders_on_page_count_data
)


items_on_page_count_menu_window = Window(
    Format("{items_on_page_count_menu_text}"),
    *keyboards.items_count_buttons(),
    Button(text=Format("{btn_back}"), id='back', on_click=on_back_settings_click_handler),
    state=SettingsMenuState.ItemsOnPagesCount,
    getter=get_items_on_page_count_data
)

dialog_settings_menu = Dialog(
    settings_menu_window,
    language_menu_window,
    folders_on_page_count_menu_window,
    items_on_page_count_menu_window,
)
