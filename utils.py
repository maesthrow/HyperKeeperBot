import math

import aiogram
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, User
from aiogram.utils.callback_data import CallbackData

from button_manager import check_button_exists
from enums import Environment
from firebase_item_reader import get_folder_items, get_item
from load_all import dp

invalid_chars = r'/\:,.*?"<>|'
folder_callback = CallbackData("folder", "folder_id")
folders_on_page_count = 4
items_on_page_count = 4
separator = 'из'


def is_valid_folder_name(name):
    return all(char not in invalid_chars for char in name)


def clean_folder_name(name):
    cleaned_name = ''.join(char if char not in invalid_chars and char not in '\n\r' else ' ' for char in name)
    return cleaned_name


def get_parent_folder_id(folder_id):
    return folder_id.rsplit('/', 1)[0]


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
        f"🗂️ {folder_name}",
        callback_data=folder_callback.new(folder_id=folder_id)
    )


async def get_inline_markup_folders(folder_buttons, current_page):
    inline_markup = InlineKeyboardMarkup(row_width=3)

    sorted_buttons = sorted(folder_buttons, key=lambda x: x.text)
    buttons = sorted_buttons[current_page * folders_on_page_count - folders_on_page_count:
                             current_page * folders_on_page_count]
    for button in buttons:
        folder_name_button = button

        # Добавляем кнопки на одну строку
        inline_markup.row(folder_name_button, InlineKeyboardButton(text='', callback_data='empty'),
                          InlineKeyboardButton(text='', callback_data='empty'))

    max_folder_num = len(sorted_buttons)
    last_page = math.ceil(max_folder_num / folders_on_page_count)
    if last_page > 1:
        inline_markup = await get_inline_markup_for_pages('folders', inline_markup, current_page,
                                                          last_page, folders_on_page_count,
                                                          max_folder_num, 'go_to_page_folders_')

    return inline_markup


async def get_inline_markup_items_in_folder(current_folder_id, current_page=1):
    tg_user = User.get_current()

    # Получаем записи из коллекции items для текущей папки
    folder_items = await get_folder_items(current_folder_id)
    list_items_id = []
    for item_id in folder_items:
        list_items_id.append(item_id)

    current_items = list_items_id[current_page * items_on_page_count - items_on_page_count:
                                  current_page * items_on_page_count]

    buttons = []
    for item_id in current_items:
        item = await get_item(tg_user.id, item_id)

        item_button_text = item.title or item.get_short_title()
        if item:
            buttons.append([InlineKeyboardButton(f"📄 {item_button_text}", callback_data=f"item_{item_id}")])

    # Создаем разметку и отправляем сообщение с кнопками для каждой item
    items_inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=buttons)
    max_items_num = len(folder_items)
    last_page = math.ceil(max_items_num / items_on_page_count)
    if last_page > 1:
        items_inline_markup = await get_inline_markup_for_pages('items', items_inline_markup, current_page,
                                                                last_page, items_on_page_count,
                                                                max_items_num, 'go_to_page_items_')
    return items_inline_markup


async def get_inline_markup_for_pages(instance_text, inline_markup, current_page, last_page, on_page_count, max_num,
                                      callback_data_text):
    instance_smile = '🗂️' if instance_text == 'folders' else '📄'

    prev_page = current_page - 1 if current_page - 1 > 0 else last_page
    next_page = current_page + 1 if current_page < last_page else 1

    first_on_page = (current_page - 1) * on_page_count + 1
    last_on_page = current_page * on_page_count
    if last_on_page > max_num:
        last_on_page = max_num
    current_nums = f"{first_on_page}..{last_on_page}" if first_on_page != last_on_page else f"{first_on_page}"
    mid_btn_text = f"{current_nums} {separator} {max_num} {instance_smile}"

    inline_markup.add(InlineKeyboardButton(text='⬅️', callback_data=f'{callback_data_text}{prev_page}'),
                      InlineKeyboardButton(text=mid_btn_text, callback_data=f'all_{instance_text}'),
                      InlineKeyboardButton(text='➡️', callback_data=f'{callback_data_text}{next_page}'))

    return inline_markup


async def get_level_folders(folder_id):
    return len(folder_id.split('/')) - 1


async def get_folders_page_info(folder_id, current_page=None):
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)

    page_folders = data.get('page_folders')
    level = await get_level_folders(folder_id)
    list_pages = page_folders.split('/')
    if not current_page:
        current_page = list_pages[level] if level < len(list_pages) else '1'
    else:
        current_page = str(current_page)
    new_page_folders = list_pages[:level + 1] if level + 1 < len(list_pages) else list_pages
    if level + 1 > len(new_page_folders):
        new_page_folders.append(current_page)
    else:
        new_page_folders[-1] = current_page
    new_page_folders = '/'.join(new_page_folders)

    folders_page_info = {'current_page': int(current_page), 'page_folders': new_page_folders}
    return folders_page_info


async def get_page_info(folder_id, entities_key, current_page=None):
    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)

    page_entities = data.get(f'page_{entities_key}')
    level = await get_level_folders(folder_id)
    list_pages = page_entities.split('/')
    if not current_page:
        current_page = list_pages[level] if level < len(list_pages) else '1'
    else:
        current_page = str(current_page)
    new_page_entities = list_pages[:level + 1] if level + 1 < len(list_pages) else list_pages
    if level + 1 > len(new_page_entities):
        new_page_entities.append(current_page)
    else:
        new_page_entities[-1] = current_page
    new_page_entities = '/'.join(new_page_entities)

    page_info = {f'current_page_{entities_key}': int(current_page), f'page_{entities_key}': new_page_entities}
    return page_info
