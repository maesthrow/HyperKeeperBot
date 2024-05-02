from enum import Enum

from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Button, Column, Checkbox, Row
from aiogram_dialog.widgets.text import Const

from dialogs.settings.getters import counts
from dialogs.settings.handlers import language_menu_handler, folders_on_page_count_menu_handler, \
    on_back_settings_click_handler, language_changed, folders_on_page_count_changed, items_on_page_count_changed, \
    items_on_page_count_menu_handler
from enums.enums import Language

_settings_menu_buttons = [
    Button(Const("🗂️ Количество папок на странице"), id="open_storage", on_click=folders_on_page_count_menu_handler),
    Button(Const("📄 Количество записей на странице"), id="accesses_menu", on_click=items_on_page_count_menu_handler),
    Button(Const("🌐 Язык интерфейса"), id="search_menu", on_click=language_menu_handler),
]

SETTINGS_MENU_BUTTONS = {
    'folders_on_page_count': {
        Language.RUSSIAN: "🗂️ Количество папок на странице",
        Language.ENGLISH: "🗂️ Number of Folders per Page",
    },
    'items_on_page_count': {
        Language.RUSSIAN: "📄 Количество записей на странице",
        Language.ENGLISH: "📄 Number of Items per Page",
    },
    'language_menu': {
        Language.RUSSIAN: "🌐 Язык интерфейса",
        Language.ENGLISH: "🌐 Interface Language",
    },
}


class Entities(Enum):
    FOLDERS = 'f'
    ITEMS = 'i'


def languages_buttons():
    return Column(
        Checkbox(Const("✓ 🇷🇺 Русский"), Const("🇷🇺 Русский"),
                 id='russian', on_state_changed=language_changed),
        Checkbox(Const("✓ 🇺🇸 English"), Const("🇺🇸 English"),
                 id='english', on_state_changed=language_changed),
        # Checkbox(Const("✓ 🇪🇸 Español"), Const("🇪🇸 Español"),
        #          id='spain', on_state_changed=language_changed),
        # Checkbox(Const("✓ 🇫🇷 Français"), Const("🇫🇷 Français"),
        #          id='french', on_state_changed=language_changed),
        #back_to_settings_menu_button()
    )


def folders_count_buttons():
    return _get_count_buttons(Entities.FOLDERS)


def items_count_buttons():
    return _get_count_buttons(Entities.ITEMS)


def _get_count_buttons(entities: Entities):
    on_state_changed = folders_on_page_count_changed if entities == Entities.FOLDERS else items_on_page_count_changed
    rows = []
    row = []
    for count in counts:
        if len(row) == 4:
            rows.append(Row(*row[:]))
            row = []
        check_text_btn = f'✓ {count}'
        id_btn = f'{entities.value}_{count}'
        row.append(
            Checkbox(
                Const(check_text_btn), Const(str(count)), id=id_btn, on_state_changed=on_state_changed
            )
        )
    if len(row) > 0:
        rows.append(Row(*row))
    return (
        *rows,
        #back_to_settings_menu_button()
    )

