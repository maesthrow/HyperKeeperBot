from aiogram_dialog import widgets
from aiogram_dialog.widgets.kbd import Column
from aiogram_dialog.widgets.text import Const

from dialogs.widgets import InlineQueryButton
from enums.enums import Language
from utils.utils_ import smile_folder, smile_item, smile_file

BUTTONS = {
    'storage': {
        Language.RUSSIAN: "🗂️ Открыть хранилище",
        Language.ENGLISH: "🗂️ Open storage",
    },
    'accesses': {
        Language.RUSSIAN: "🔐 Доступы от других пользователей",
        Language.ENGLISH: "🔐 Access from other users",
    },
    'search': {
        Language.RUSSIAN: "🔍️ Live-поиск",
        Language.ENGLISH: "🔍️ Live search",
    },
    'profile': {
        Language.RUSSIAN: "👤 Мой профиль",
        Language.ENGLISH: "👤 My profile",
    },
    'settings': {
        Language.RUSSIAN: "⚙️ Настройки",
        Language.ENGLISH: "⚙️ Settings",
    },
    'help': {
        Language.RUSSIAN: "❔ Помощь",
        Language.ENGLISH: "❔ Help",
    },
}


SEARCH_BUTTONS = {
    'global': {
        Language.RUSSIAN: "🔍 Глобальный поиск 🌐",
        Language.ENGLISH: "🔍 Global Search 🌐",
    },
    'folders': {
        Language.RUSSIAN: f"🔍 Поиск папок {smile_folder}",
        Language.ENGLISH: f"🔍 Folder Search {smile_folder}",
    },
    'items': {
        Language.RUSSIAN: f"🔍 Поиск записей {smile_item}",
        Language.ENGLISH: f"🔍 Record Search {smile_item}",
    },
    'files': {
        Language.RUSSIAN: f"🔍 Поиск файлов {smile_file}",
        Language.ENGLISH: f"🔍 File Search {smile_file}",
    },
}


HELP_BUTTONS = {
    'contact_support': {
        Language.RUSSIAN: "💬 Написать в поддержку",
        Language.ENGLISH: "💬 Contact Support",
    },
}