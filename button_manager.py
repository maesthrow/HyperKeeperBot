from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

general_buttons_folder = [
        [KeyboardButton("➕ Новая папка"), KeyboardButton("🔍 Поиск")],
        [KeyboardButton("️📊 Статистика"), KeyboardButton("️🧹 Удалить все записи в папке")],
    ]

general_buttons_folder_show_all = [
        [KeyboardButton("➕ Новая папка"), KeyboardButton("️📊 Статистика")],
    ]

general_buttons_items_show_all = [
        [KeyboardButton("️🔍 Поиск"), KeyboardButton("️📊 Статистика")],
        [KeyboardButton("️🧹 Удалить все записи в папке")],
        [KeyboardButton("️↩️ Назад к общему виду папки")]
    ]

general_buttons_item = [
        [KeyboardButton("️✏️ Редактировать заголовок"), KeyboardButton("️📝 Редактировать текст")],
        [KeyboardButton("️🔀 Переместить"), KeyboardButton("🗑 Удалить")],
        [KeyboardButton("️↩️ Назад к папке")],
    ]

skip_enter_item_title_button = InlineKeyboardButton("Без заголовка", callback_data="skip_enter_item_title")
cancel_add_new_item_button = InlineKeyboardButton("Не добавлять запись", callback_data="cancel_add_new_item")


# Определяем функцию для создания разметки ответа для общего использования
def create_general_reply_markup(buttons):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for sub_buttons in buttons:
        markup.add(*sub_buttons)
    return markup


def check_button_exists(keyboard: ReplyKeyboardMarkup, button_text: str) -> bool:
    if not keyboard:
        return False
    for row in keyboard.keyboard:
        for button in row:
            if button.text == button_text:
                return True
    return False
