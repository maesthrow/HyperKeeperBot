from enum import Enum


class Environment(Enum):
    FOLDERS = "➕ Новая папка"
    ITEM_CONTENT = "️📝 Редактировать текст"


class Language(Enum):
    RUSSIAN = "russian"
    GERMAN = "german"
    ENGLISH = "english"
    SPAIN = "spain"
    FRENCH = "french"
    ITALIAN = "italian"
    KAZAKH = "kazakh"
    CHINESE = "chinese"


class AccessType(Enum):
    ABSENSE = ''
    READ = 'r'
    WRITE = 'w'
