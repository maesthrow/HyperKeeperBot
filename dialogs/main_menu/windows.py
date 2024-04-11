from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format

from dialogs import general_keyboards
from dialogs.main_menu import keyboards
from dialogs.main_menu.getters import get_start_data, get_main_menu_data, get_live_search_data
from dialogs.main_menu.handlers import *
from handlers_pack.states import MainMenuState

start_window = Window(
    Format("{start_text}"),
    general_keyboards.to_main_menu_button(),
    state=MainMenuState.Start,
    getter=get_start_data
)

main_menu_window = Window(
    Format("{message_text}"),
    *keyboards.main_menu(),
    state=MainMenuState.Menu,
    getter=get_main_menu_data
)

live_search_window = Window(
    Format("{message_text}"),
    *keyboards.live_search(),
    general_keyboards.to_main_menu_button(),
    state=MainMenuState.LiveSearch,
    getter=get_live_search_data
)

dialog_main_menu = Dialog(
    start_window,
    main_menu_window,
    live_search_window
)
