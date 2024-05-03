from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from dialogs.general_handlers import open_main_menu_handler
from enums.enums import Language

BUTTONS = {
    'menu': {
        Language.RUSSIAN: "☰ Меню",
        Language.ENGLISH: "☰ Menu",
    },
    'back': {
        Language.RUSSIAN: "↩️ Назад",
        Language.ENGLISH: "↩️ Back",
    },
    'cancel': {
        Language.RUSSIAN: "Отменить",
        Language.ENGLISH: "Cancel",
    },
}

