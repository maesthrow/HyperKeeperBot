from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format

from dialogs.main_menu import keyboards
from dialogs.main_menu.getters import get_start_data, get_main_menu_data
from dialogs.main_menu.handlers import *
from handlers_pack.states import MainMenuState

start_window = Window(
    Format("{start_text}"),
    Button(text=Const("☰ Меню"), id="main_menu", on_click=open_main_menu_handler),
    state=MainMenuState.Start,
    getter=get_start_data
)

main_menu_window = Window(
    Format("{message_text}"),
    *keyboards.main_menu(),
    state=MainMenuState.Menu,
    getter=get_main_menu_data
)

dialog_main_menu = Dialog(
    start_window,
    main_menu_window
)
