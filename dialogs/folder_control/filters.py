from typing import Optional

from aiogram.types import Message

from utils.utils_folders import is_valid_folder_name


def filter_invalid_chars(message: Message) -> Optional[str]:
    input_text = message.text
    if is_valid_folder_name(input_text):
        return input_text
    return None
