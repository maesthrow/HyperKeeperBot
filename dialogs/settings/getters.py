from enum import Enum

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Checkbox, ManagedCheckbox

from dialogs import general_keyboards
from dialogs.settings import keyboards
from enums.enums import Language
from resources.text_getter import get_text
from utils.utils_data import get_from_user_collection, get_current_lang

languages = (
    Language.RUSSIAN,
    Language.ENGLISH,
    Language.SPAIN,
    Language.FRENCH
)

counts = (6, 8, 10, 12, 14, 16, 18, 20)


async def get_settings_menu_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    settings_text = await get_text(user_id, 'settings')
    return {
        'message_text': f'<b>⚙️ {settings_text}</b>',
        'btn_folders_on_page_count': keyboards.SETTINGS_MENU_BUTTONS['folders_on_page_count'].get(language),
        'btn_items_on_page_count': keyboards.SETTINGS_MENU_BUTTONS['items_on_page_count'].get(language),
        'btn_language_menu': keyboards.SETTINGS_MENU_BUTTONS['language_menu'].get(language),
        'btn_menu': (general_keyboards.BUTTONS['menu'].get(language))
    }


async def get_language_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)

    for lang in languages:
        checkbox: ManagedCheckbox = dialog_manager.find(lang.value)
        if checkbox:
            await checkbox.set_checked(lang == language)

    settings_text = await get_text(user_id, 'settings')
    language_title_text = await get_text(user_id, 'language_title_text')
    language_menu_text = f'<b>⚙️ {settings_text} > {language_title_text}</b>'

    return {
        'language': language,
        'language_menu_text': language_menu_text,
        'btn_back': general_keyboards.BUTTONS['back'].get(language)
    }


async def get_folders_on_page_count_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    settings = await get_from_user_collection(user_id, 'settings')
    folders_on_page_count = settings.get('folders_on_page_count', 6)

    for count in counts:
        checkbox: ManagedCheckbox = dialog_manager.find(f'f_{str(count)}')
        if checkbox:
            await checkbox.set_checked(count == folders_on_page_count)

    settings_text = await get_text(user_id, 'settings')
    folders_on_page_count_title_text = await get_text(user_id, 'folders_on_page_count_title_text')
    folders_on_page_count_menu_text = f'<b>⚙️ {settings_text} > {folders_on_page_count_title_text}</b>'

    return {
        'folders_on_page_count': folders_on_page_count,
        'folders_on_page_count_menu_text': folders_on_page_count_menu_text,
        'btn_back': general_keyboards.BUTTONS['back'].get(language)
    }


async def get_items_on_page_count_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    settings = await get_from_user_collection(dialog_manager.event.from_user.id, 'settings')
    items_on_page_count = settings.get('items_on_page_count', 6)

    for count in counts:
        checkbox: ManagedCheckbox = dialog_manager.find(f'i_{str(count)}')
        if checkbox:
            await checkbox.set_checked(count == items_on_page_count)

    settings_text = await get_text(user_id, 'settings')
    items_on_page_count_title_text = await get_text(user_id, 'items_on_page_count_title_text')
    items_on_page_count_menu_text = f'<b>⚙️ {settings_text} > {items_on_page_count_title_text}</b>'

    return {
        'items_on_page_count': items_on_page_count,
        'items_on_page_count_menu_text': items_on_page_count_menu_text,
        'btn_back': general_keyboards.BUTTONS['back'].get(language)
    }
