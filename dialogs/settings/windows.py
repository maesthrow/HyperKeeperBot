from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Back, Checkbox, Column
from aiogram_dialog.widgets.text import Const

from dialogs import general_keyboards
from dialogs.settings import keyboards
from dialogs.settings.getters import get_language_data
from dialogs.settings.handlers import language_changed
from handlers_pack.states import SettingsMenuState

settings_menu_window = Window(
    Const("⚙️ <b>Настройки</b>"),
    *keyboards.settings_menu(),
    general_keyboards.to_main_menu_button(),
    state=SettingsMenuState.Menu,
    # getter=get_main_menu_data
)

language_menu_window = Window(
    Const("<b>🌐 Выберите язык интерфейса</b>"),
    Column(
        Checkbox(Const("✓ 🇷🇺 Русский"), Const("🇷🇺 Русский"),
                 id='ru', on_state_changed=language_changed),  # , on_click=language_selected_handler),
        Checkbox(Const("✓ 🇺🇸 English"), Const("🇺🇸 English"),
                 id='en', on_state_changed=language_changed),  # , on_click=language_selected_handler),
        Checkbox(Const("✓ 🇪🇸 Español"), Const("🇪🇸 Español"),
                 id='es', on_state_changed=language_changed),  # , on_click=language_selected_handler),
        Checkbox(Const("✓ 🇫🇷 Français"), Const("🇫🇷 Français"),
                 id='fr', on_state_changed=language_changed),  # , on_click=language_selected_handler),
        Back(Const("↩️ Назад")),
    ),
    state=SettingsMenuState.Language,
    getter=get_language_data
)

dialog_settings_menu = Dialog(
    settings_menu_window,
    language_menu_window,
)
