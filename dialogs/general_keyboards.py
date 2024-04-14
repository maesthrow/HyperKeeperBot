from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from dialogs.general_handlers import open_main_menu_handler
from enums.enums import Language

BUTTONS = {
    'menu': {
        Language.RUSSIAN: "☰ Меню",
        Language.ENGLISH: "☰ Menu",
    },
}


def to_main_menu_button():
    return Button(text=Const("☰ Меню"), id="main_menu", on_click=open_main_menu_handler)
