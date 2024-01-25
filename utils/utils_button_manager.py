import asyncio
import concurrent.futures
import functools

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

general_buttons_folder = [
        [KeyboardButton(text="➕ Новая папка"), KeyboardButton(text="🔍 Поиск")],
        [KeyboardButton(text="️📊 Статистика"), KeyboardButton(text="️🧹 Удалить все записи в папке")],
    ]

general_buttons_folder_show_all = [
        [KeyboardButton(text="➕ Новая папка"), KeyboardButton(text="️📊 Статистика")],
    ]

general_buttons_items_show_all = [
        [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="️📊 Статистика")],
        [KeyboardButton(text="️🧹 Удалить все записи в папке")],
        [KeyboardButton(text="↪️ Перейти к общему виду папки 🗂️📄")]
    ]

general_buttons_item = [
        [KeyboardButton(text="️✏️ Заголовок"), KeyboardButton(text="️📝 Текст"), KeyboardButton(text="️🗃️ Файлы и медиа")],
        [KeyboardButton(text="️🔀 Переместить"), KeyboardButton(text="🗑 Удалить")],
        [KeyboardButton(text="️↩️ Назад к папке")],
    ]

general_buttons_movement_item = [
        [KeyboardButton(text="🔀 Переместить в текущую папку")],
        [KeyboardButton(text="️🚫 Отменить перемещение")],
    ]

general_buttons_search_items = [
        [KeyboardButton(text="🔄 Новый поиск 🔍️")],
        [KeyboardButton(text="🫡 Завершить режим поиска 🔍️")],
    ]

general_buttons_statistic_folder = [
        [KeyboardButton(text="️↩️ Назад к папке")],
    ]


ok_info_button = InlineKeyboardButton(text="👌 Понятно", callback_data="ok_info")
skip_enter_item_title_button = InlineKeyboardButton(text="Без заголовка", callback_data="skip_enter_item_title")
cancel_add_new_item_button = InlineKeyboardButton(text="Не добавлять запись", callback_data="cancel_add_new_item")



item_inline_buttons = [
        [
            InlineKeyboardButton(text="Поделиться", switch_inline_query="none"),
            InlineKeyboardButton(text="🔀 Переместить", callback_data="move_item"),
        ],
        [
            InlineKeyboardButton(text="📝 Редактировать", callback_data="edit_item"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_item"),
        ],

        [
            InlineKeyboardButton(text="❌ Закрыть", callback_data="close_item"),
        ]
]

#repost_item_button = InlineKeyboardButton("Поделиться", switch_inline_query="none")
show_item_files_button = InlineKeyboardButton(text="Показать файлы »", callback_data="show_item_files")
hide_item_files_button = InlineKeyboardButton(text="« Скрыть файлы", callback_data="hide_item_files")
item_inline_buttons_with_files = [
        [
            InlineKeyboardButton(text="Поделиться", switch_inline_query="none"),
            InlineKeyboardButton(text="🔀 Переместить", callback_data="move_item"),
        ],
        [
            InlineKeyboardButton(text="📝 Редактировать", callback_data="edit_item"),
            InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_item"),
        ],

        [
            InlineKeyboardButton(text="❌ Закрыть", callback_data="close_item"),
            hide_item_files_button,
        ]
]

item_edit_buttons = [
        [
            InlineKeyboardButton(text="✏️ Заголовок", callback_data="edit_item_title"),
            InlineKeyboardButton(text="📝 Текст", callback_data="edit_item_text"),
            InlineKeyboardButton(text="🗃️ Файлы", callback_data="edit_item_files"),
        ],
        [
            InlineKeyboardButton(text="↩️ Назад", callback_data="edit_item_back")
        ]
]


# Определяем функцию для создания разметки ответа для общего использования
def create_general_reply_markup(buttons):
    markup = ReplyKeyboardMarkup(keyboard=[*buttons], resize_keyboard=True, row_width=3)
    return markup


def check_button_exists(keyboard: ReplyKeyboardMarkup, button_text: str) -> bool:
    if not keyboard:
        return False
    for row in keyboard.keyboard:
        for button in row:
            if button.text.lower() == button_text.lower():
                return True
    return False


def check_button_exists_part_of_text(keyboard: ReplyKeyboardMarkup, button_text: str) -> bool:
    if not keyboard:
        return False
    for row in keyboard.keyboard:
        for button in row:
            if button_text.lower() in button.text.lower():
                return True
    return False


def get_folders_with_items_inline_markup(folders_inline_markup, items_inline_markup):
    # loop = asyncio.get_event_loop()
    # result = await loop.run_in_executor(
    #     concurrent.futures.ProcessPoolExecutor(max_workers=2),
    #     functools.partial(merge_keyboards, folders_inline_markup, items_inline_markup))
    return merge_keyboards(folders_inline_markup, items_inline_markup)


# async def get_folders_with_items_inline_markup(folders_inline_markup, items_inline_markup):
#     with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
#         future = executor.submit(functools.partial(merge_keyboards, folders_inline_markup, items_inline_markup))
#         result = await future.result(timeout=3)


def merge_keyboards(*markups):
    keyboard_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for markup in markups:
        keyboard_builder.attach(InlineKeyboardBuilder.from_markup(markup))
    return keyboard_builder.as_markup()
