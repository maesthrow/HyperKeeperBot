from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Row, Button
from aiogram_dialog.widgets.text import Const, Format

from dialogs.main_menu.getters import get_start_data, get_main_menu_data
from handlers_pack.states import MainMenuState

start_window = Window(
    Format("{start_text}"),
    Button(text=Const("Главное меню"), id="main_menu"),
    #*keyboards.folder_control_main_menu(),
    state=MainMenuState.Start,
    getter=get_start_data
)

dialog_main_menu = Dialog(
    start_window
)
