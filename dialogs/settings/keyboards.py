from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Button, Column, Checkbox, Row
from aiogram_dialog.widgets.text import Const

from dialogs.settings.handlers import language_menu_handler, folders_on_page_count_menu_handler, \
    on_back_settings_click_handler, language_changed, folders_on_page_count_changed, items_on_page_count_changed, \
    items_on_page_count_menu_handler

_settings_menu_buttons = [
    Button(Const("🗂️ Количество папок на странице"), id="open_storage", on_click=folders_on_page_count_menu_handler),
    Button(Const("📄 Количество записей на странице"), id="accesses_menu", on_click=items_on_page_count_menu_handler),
    Button(Const("🌐 Язык интерфейса"), id="search_menu", on_click=language_menu_handler),
]


def settings_menu() -> widgets:
    keyboard = [
        Column(*_settings_menu_buttons)
    ]
    return keyboard


def back_to_settings_menu_button():
    return Button(text=Const("↩️ Назад"), id='back', on_click=on_back_settings_click_handler)


def languages_buttons():
    return Column(
        Checkbox(Const("✓ 🇷🇺 Русский"), Const("🇷🇺 Русский"),
                 id='russian', on_state_changed=language_changed),
        Checkbox(Const("✓ 🇺🇸 English"), Const("🇺🇸 English"),
                 id='english', on_state_changed=language_changed),
        Checkbox(Const("✓ 🇪🇸 Español"), Const("🇪🇸 Español"),
                 id='spain', on_state_changed=language_changed),
        Checkbox(Const("✓ 🇫🇷 Français"), Const("🇫🇷 Français"),
                 id='french', on_state_changed=language_changed),
        back_to_settings_menu_button()
    )


def folders_count_buttons():
    return (
        Row(
            Checkbox(Const("✓ 6"), Const("6"), id='f_6', on_state_changed=folders_on_page_count_changed),
            Checkbox(Const("✓ 8"), Const("8"), id='f_8', on_state_changed=folders_on_page_count_changed),
            Checkbox(Const("✓ 10"), Const("10"), id='f_10', on_state_changed=folders_on_page_count_changed),
            Checkbox(Const("✓ 12"), Const("12"), id='f_12', on_state_changed=folders_on_page_count_changed),
        ),
        Row(
            Checkbox(Const("✓ 14"), Const("14"), id='f_14', on_state_changed=folders_on_page_count_changed),
            Checkbox(Const("✓ 16"), Const("16"), id='f_16', on_state_changed=folders_on_page_count_changed),
            Checkbox(Const("✓ 18"), Const("18"), id='f_18', on_state_changed=folders_on_page_count_changed),
            Checkbox(Const("✓ 20"), Const("20"), id='f_20', on_state_changed=folders_on_page_count_changed),
        ),
        back_to_settings_menu_button()
    )


def items_count_buttons():
    return (
        Row(
            Checkbox(Const("✓ 6"), Const("6"), id='i_6', on_state_changed=items_on_page_count_changed),
            Checkbox(Const("✓ 8"), Const("8"), id='i_8', on_state_changed=items_on_page_count_changed),
            Checkbox(Const("✓ 10"), Const("10"), id='i_10', on_state_changed=items_on_page_count_changed),
            Checkbox(Const("✓ 12"), Const("12"), id='i_12', on_state_changed=items_on_page_count_changed),
        ),
        Row(
            Checkbox(Const("✓ 14"), Const("14"), id='i_14', on_state_changed=items_on_page_count_changed),
            Checkbox(Const("✓ 16"), Const("16"), id='i_16', on_state_changed=items_on_page_count_changed),
            Checkbox(Const("✓ 18"), Const("18"), id='i_18', on_state_changed=items_on_page_count_changed),
            Checkbox(Const("✓ 20"), Const("20"), id='i_20', on_state_changed=items_on_page_count_changed),
        ),
        back_to_settings_menu_button()
    )
