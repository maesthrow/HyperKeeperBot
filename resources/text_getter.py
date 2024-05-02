from aiogram.types import User

from enums.enums import Language
from resources.strings import *
from utils.utils_data import get_current_lang


def _get_text(
        param: str = "empty_param",
        language: Language = Language.ENGLISH
) -> str:
    text: str = STRINGS.get(param, STRINGS['empty_param']).get(language, param)
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
    start_first = _get_text(param='start_first', language=language)
    start_hello = _get_text('start_hello', language).format(user_first_name=user.first_name)
    start_first_text = f"{start_hello}️{start_first}"
    return start_first_text


async def get_start_text(user: User):
    language: Language = await get_current_lang(user.id)
    start = _get_text(param='start', language=language)
    start_hello = _get_text('start_hello', language).format(user_first_name=user.first_name)
    start_text = f"{start_hello}️{start}"
    return start_text
