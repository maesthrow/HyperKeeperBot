import asyncio

import aiogram
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from button_manager import check_button_exists
from firebase_item_reader import get_folder_items, get_item
from load_all import dp
from enums import Environment

invalid_chars = r'/\:,.*?"<>|'
folder_callback = CallbackData("folder", "folder_id")


def is_valid_folder_name(name):
    return all(char not in invalid_chars for char in name)


def clean_folder_name(name):
    cleaned_name = ''.join(char if char not in invalid_chars and char not in '\n\r' else ' ' for char in name)
    return cleaned_name


async def get_environment():
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    keyboard: ReplyKeyboardMarkup = data.get('current_keyboard', None)
    environment: Environment = Environment.FOLDERS
    for tmp_environment in Environment:
        if check_button_exists(keyboard, tmp_environment.value):
            environment = tmp_environment
    return environment


async def get_inline_markup_for_accept_cancel(text_accept, text_cancel, callback_data):
    inline_markup = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text=text_accept, callback_data=f"{callback_data}_accept"),
            ],
            [
                InlineKeyboardButton(text=text_cancel, callback_data=f"{callback_data}_cancel")
            ],
        ]
    )
    return inline_markup


async def create_folder_button(folder_id, folder_name):
    return InlineKeyboardButton(
        f"📁 {folder_name}",
        callback_data=folder_callback.new(folder_id=folder_id)
    )


def get_inline_markup_folders(folder_buttons):
    inline_markup = InlineKeyboardMarkup(row_width=3)

    sorted_buttons = sorted(folder_buttons, key=lambda x: x.text)
    for button in sorted_buttons:
        folder_name_button = button

        # Добавляем кнопки на одну строку
        inline_markup.row(folder_name_button, InlineKeyboardButton(text='', callback_data='empty'),
                          InlineKeyboardButton(text='', callback_data='empty'))

    return inline_markup


async def get_inline_markup_items_in_folder(current_folder_id):
    tg_user = aiogram.types.User.get_current()

    # Получаем записи из коллекции items для текущей папки
    folder_items = await get_folder_items(tg_user.id, current_folder_id)

    buttons = []
    # Создаем список кнопок для каждой записи
    for item_id in folder_items:
        item = await get_item(tg_user.id, item_id)

        item_button_text = item.title or item.get_short_title()
        if item:
            buttons.append([InlineKeyboardButton(f"📄 {item_button_text}", callback_data=f"item_{item_id}")])

    # Создаем разметку и отправляем сообщение с кнопками для каждой item
    items_inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    return items_inline_markup
