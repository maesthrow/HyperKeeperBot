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


_live_search_buttons = [
    InlineQueryButton(
        Const(f"🔍 Глобальный поиск 🌐"),
        id="global_search",
        switch_inline_query_current_chat=Const("")
    ),
    InlineQueryButton(
        Const(f"🔍 Поиск папок {smile_folder}"),
        id="folders_search",
        switch_inline_query_current_chat=Const("folders/")
    ),
    InlineQueryButton(
        Const(f"🔍 Поиск записей {smile_item}"),
        id="items_search",
        switch_inline_query_current_chat=Const("items/")
    ),
    InlineQueryButton(
        Const(f"🔍 Поиск файлов {smile_file}"),
        id="files_search",
        switch_inline_query_current_chat=Const("files/")
    ),
]


def live_search() -> widgets:
    keyboard = [
        Column(*_live_search_buttons)
    ]
    return keyboard


