from enum import Enum


class Environment(Enum):
    FOLDERS = "➕ Новая папка"
    ITEM_CONTENT = "️📝 Редактировать текст"


class Language(Enum):
    RUSSIAN = {"russian": "🇷🇺 Русский"}
    GERMAN = {"german": "🇩🇪 Deutsch"}
    ENGLISH = {"english": "🇬🇧 English"}
    SPAIN = {"spain": "🇪🇸 Español"}
    FRENCH = {"french": "🇫🇷 Français"}
    ITALIAN = {"italian": "🇮🇹 Italiano"}
    KAZAKH = {"kazakh": "🇰🇿 қазақ"}
    CHINESE = {"chinese": "🇨🇳 中國人"}


class AccessType(Enum):
    ABSENSE = ''
    READ = 'r'
    WRITE = 'w'
