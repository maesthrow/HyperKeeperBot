from enum import Enum

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Checkbox, ManagedCheckbox

from enums.enums import Language
from utils.utils_data import get_from_user_collection


async def get_language_data(dialog_manager: DialogManager, **kwargs):
    settings = await get_from_user_collection(dialog_manager.event.from_user.id, 'settings')
    language = Language(settings.get('language', "russian"))

    print(language)

    cb_rus: ManagedCheckbox = dialog_manager.find(Language.RUSSIAN.value)
    cb_eng: ManagedCheckbox = dialog_manager.find(Language.ENGLISH.value)
    cb_spa: ManagedCheckbox = dialog_manager.find(Language.SPAIN.value)
    cb_fre: ManagedCheckbox = dialog_manager.find(Language.FRENCH.value)

    await cb_rus.set_checked(checked=(language == Language.RUSSIAN))
    await cb_eng.set_checked(checked=(language == Language.ENGLISH))
    await cb_spa.set_checked(checked=(language == Language.SPAIN))
    await cb_fre.set_checked(checked=(language == Language.FRENCH))

    return {'language': language}

