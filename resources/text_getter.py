from aiogram.types import User

from enums.enums import Language
from resources.strings import *
from utils.utils_data import get_current_lang


def _get_text(
        param: str = "empty_param",
        language: Language = Language.ENGLISH
) -> str:
    text: str = STRINGS.get(param, param).get(language, param)
    return text


async def get_text(
        user_id,
        param: str
) -> str:
    language: Language = await get_current_lang(user_id)
    text = _get_text(param=param, language=language)
    return text


async def get_start_first_text(user: User):
    language: Language = await get_current_lang(user.id)
    hello = _get_text(param='Hello', language=language)
    lets_get_started = _get_text(param='lets_get_started', language=language)
    start_first = _get_text(param='start_first', language=language)
    start_first_text = f"👋 {hello}, {user.first_name}, {lets_get_started}! 🚀️{start_first}"
    return start_first_text


async def get_start_text(user: User):
    language: Language = await get_current_lang(user.id)
    hello = _get_text(param='Hello', language=language)
    lets_get_started = _get_text(param='lets_get_started', language=language)
    start = _get_text(param='start', language=language)
    start_text = (f"👋 {hello}, {user.first_name}, {lets_get_started}! 🚀️"
                  f"{start}")
    return start_text
