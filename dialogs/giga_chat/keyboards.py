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
        Language.RUSSIAN: "✖️ Закрыть чат",
        Language.ENGLISH: "✖️ Close Chat",
    },
    'delete_chat': {
        Language.RUSSIAN: "🗑️ Удалить чат",
        Language.ENGLISH: "🗑️ Delete Chat",
    },
    'clear_chats_history': {
        Language.RUSSIAN: "🧹 Очистить историю чатов",
        Language.ENGLISH: "🧹 Clear Chat History",
    },
    'confirm_delete_chat': {
        Language.RUSSIAN: "☑️ Да, удалить",
        Language.ENGLISH: "☑️ Yes, delete",
    },
    'cancel_delete_chat': {
        Language.RUSSIAN: "✖️ Нет, не удалять",
        Language.ENGLISH: "✖️ No, don't delete",
    },
    'confirm_clear_chats_history': {
        Language.RUSSIAN: "🧹 Да, очистить",
        Language.ENGLISH: "🧹 Yes, clear",
    },
    'cancel_clear_chats_history': {
        Language.RUSSIAN: "✖️ Нет, отменить",
        Language.ENGLISH: "✖️ No, cancel",
    },
}

# KEYBOARD_BUTTONS = {
#     'stop_chat': {
#         Language.RUSSIAN: KeyboardButton(text="👋 Завершить диалог"),
#         Language.ENGLISH: KeyboardButton(text="👋 End Dialogue"),
#     }
# }


def get_chat_reply_keyboard(language: Language, is_new_chat):
    save_and_close_chat_btn_text = BUTTONS.get('save_and_close_chat').get(language)
    close_chat_btn_text = BUTTONS.get('close_chat').get(language)
    delete_chat_btn_text = BUTTONS.get('delete_chat').get(language)
    keyboard = [
        [
            KeyboardButton(text=save_and_close_chat_btn_text)],
        [
            KeyboardButton(text=close_chat_btn_text),
        ],
    ]
    if not is_new_chat:
        keyboard[1].append(KeyboardButton(text=delete_chat_btn_text))
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


def user_have_chats(data: dict, widget, context) -> bool:
    chats = data.get('chats', {})
    return len(chats) > 0
