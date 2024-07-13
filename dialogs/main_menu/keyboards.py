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
    'chatgpt': {
        Language.RUSSIAN: "🧠 ChatGPT",
        Language.ENGLISH: "🧠 ChatGPT",
    },
    'search': {
        Language.RUSSIAN: "🔍️ Быстрый поиск",
        Language.ENGLISH: "🔍️ Quick search",
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
    'general': {
        Language.RUSSIAN: "🌐 Общий поиск",
        Language.ENGLISH: "🌐 General Search",
    },
    'folders': {
        Language.RUSSIAN: f"{smile_folder} Поиск папок",
        Language.ENGLISH: f"{smile_folder} Folder Search",
    },
    'items': {
        Language.RUSSIAN: f"{smile_item} Поиск записей",
        Language.ENGLISH: f"{smile_item} Record Search",
    },
    'files': {
        Language.RUSSIAN: f"{smile_file} Поиск файлов",
        Language.ENGLISH: f"{smile_file} File Search",
    },
}


HELP_BUTTONS = {
    'contact_support': {
        Language.RUSSIAN: "💬 Написать в поддержку",
        Language.ENGLISH: "💬 Contact Support",
    },
}