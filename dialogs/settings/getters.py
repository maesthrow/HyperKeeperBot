from enum import Enum

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Checkbox, ManagedCheckbox

from dialogs import general_keyboards
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
    settings_text = await get_text(user_id, 'Settings')
    return {
        'message_text': f'<b>⚙️ {settings_text}</b>',
        'btn_menu': (general_keyboards.BUTTONS['menu'].get(language))
    }


async def get_language_data(dialog_manager: DialogManager, **kwargs):
    language = await get_current_lang(dialog_manager.event.from_user.id)

    for lang in languages:
        checkbox: ManagedCheckbox = dialog_manager.find(lang.value)
        if checkbox:
            await checkbox.set_checked(lang == language)

    return {'language': language}


async def get_folders_on_page_count_data(dialog_manager: DialogManager, **kwargs):
    settings = await get_from_user_collection(dialog_manager.event.from_user.id, 'settings')
    folders_on_page_count = settings.get('folders_on_page_count', 6)

    print(folders_on_page_count)

    for count in counts:
        checkbox: ManagedCheckbox = dialog_manager.find(f'f_{str(count)}')
        if checkbox:
            await checkbox.set_checked(count == folders_on_page_count)

    return {'folders_on_page_count': folders_on_page_count}


async def get_items_on_page_count_data(dialog_manager: DialogManager, **kwargs):
    settings = await get_from_user_collection(dialog_manager.event.from_user.id, 'settings')
    items_on_page_count = settings.get('items_on_page_count', 6)

    print(items_on_page_count)

    for count in counts:
        checkbox: ManagedCheckbox = dialog_manager.find(f'i_{str(count)}')
        if checkbox:
            await checkbox.set_checked(count == items_on_page_count)

    return {'items_on_page_count': items_on_page_count}
