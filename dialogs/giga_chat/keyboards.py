from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram_dialog.widgets.kbd import Keyboard

from enums.enums import Language

BUTTONS = {
    'new_chat': {
        Language.RUSSIAN: "💬 Новый чат",
        Language.ENGLISH: "💬 New Chat",
    },
    'save_and_close_chat': {
        Language.RUSSIAN: "✅ Сохранить и закрыть чат",
        Language.ENGLISH: "✅ Save & Close Chat",
    },
    'close_chat': {
        Language.RUSSIAN: "✖️ Закрыть чат без сохранения",
        Language.ENGLISH: "✖️ Close Chat Without Saving",
    },
    'delete_chat': {
        Language.RUSSIAN: "🗑️ Удалить чат",
        Language.ENGLISH: "🗑️ Delete Chat",
    },
}

# KEYBOARD_BUTTONS = {
#     'stop_chat': {
#         Language.RUSSIAN: KeyboardButton(text="👋 Завершить диалог"),
#         Language.ENGLISH: KeyboardButton(text="👋 End Dialogue"),
#     }
# }


def get_chat_reply_keyboard(language: Language):
    save_and_close_chat_btn_text = BUTTONS.get('save_and_close_chat').get(language)
    close_chat_btn_text = BUTTONS.get('close_chat').get(language)
    delete_chat_btn_text = BUTTONS.get('delete_chat').get(language)
    keyboard = [
        [KeyboardButton(text=save_and_close_chat_btn_text)],
        [
            KeyboardButton(text=close_chat_btn_text),
            #KeyboardButton(text=delete_chat_btn_text),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

