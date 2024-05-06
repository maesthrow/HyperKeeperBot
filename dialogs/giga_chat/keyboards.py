from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram_dialog.widgets.kbd import Keyboard

from enums.enums import Language

BUTTONS = {
    'stop_chat': {
        Language.RUSSIAN: "👋 Завершить диалог",
        Language.ENGLISH: "👋 End Dialogue",
    },
}

# KEYBOARD_BUTTONS = {
#     'stop_chat': {
#         Language.RUSSIAN: KeyboardButton(text="👋 Завершить диалог"),
#         Language.ENGLISH: KeyboardButton(text="👋 End Dialogue"),
#     }
# }


def get_chat_reply_keyboard(language: Language):
    stop_chat_btn_text = BUTTONS.get('stop_chat').get(language)
    keyboard = [[KeyboardButton(text=stop_chat_btn_text)]]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

