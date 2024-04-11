from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.text import Const

from dialogs import general_keyboards
from dialogs.settings import keyboards
from handlers_pack.states import SettingsMenuState

settings_menu_window = Window(
    Const("⚙️ <b>Настройки</b>"),
    *keyboards.settings_menu(),
    general_keyboards.to_main_menu_button(),
    state=SettingsMenuState.Menu,
    #getter=get_main_menu_data
)


dialog_settings_menu = Dialog(
    settings_menu_window,
)
