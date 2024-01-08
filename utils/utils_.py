import math

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, User, Chat
from aiogram.utils.callback_data import CallbackData

from firebase.firebase_collection_folders import ROOT_FOLDER_ID
from utils.utils_button_manager import check_button_exists
from enums.enums import Environment
from firebase.firebase_folder_reader import get_folder_data
from firebase.firebase_item_reader import get_folder_items, get_item
from load_all import dp
from utils.utils_data import get_folders_collection, get_from_user_collection

folder_callback = CallbackData("folder", "folder_id")
#folders_on_page_count = 4
#items_on_page_count = 4
separator = 'из'
smile_folder = '🗂️'
smile_item = '📄'


async def get_sub_folders(folder_id):
    folders = await get_folder_data(folder_id)
    return folders.get("folders", {})


async def get_sub_folder_names(folder_id):
    """Возвращает список всех folder_id внутри указанной папки."""
    folders_collection = await get_folders_collection()

    # Разбиваем идентификатор папки на части
    folder_ids = folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности папки
    for folder_part in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Получаем все folder_id внутри указанной папки
    sub_folder_ids = list(target_folders.keys())
    sub_folder_names = [await get_folder_name(sub_folder_id) for sub_folder_id in sub_folder_ids]

    return sub_folder_names


async def get_folder_name(folder_id=ROOT_FOLDER_ID):
    """Возвращает имя папки по её идентификатору."""
    folder_data = await get_folder_data(folder_id)
    return folder_data.get("name", "")


async def get_folder_path_names(folder_id=ROOT_FOLDER_ID):
    """Возвращает имена папок по пути к папке."""
    folders_collection = await get_folders_collection()
    folder_ids = folder_id.split('/')
    target_folders = folders_collection
    folder_id_with_path = None
    path_names = None
    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folder_name = target_folder.get("name", "")
        path_names = f"{path_names} > {target_folder_name}" if path_names else target_folder_name
        target_folders = target_folder.get("folders", {})
    return f"{path_names}:"


async def get_environment():
    tg_user = User.get_current()
    chat = Chat.get_current()
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
        f"{smile_folder} {folder_name}",
        callback_data=folder_callback.new(folder_id=folder_id)
    )


async def get_inline_markup_folders(folder_buttons, current_page):
    inline_markup = InlineKeyboardMarkup(row_width=3)

    sorted_buttons = sorted(folder_buttons, key=lambda x: x.text)

    settings = await get_from_user_collection('settings')
    folders_on_page_count = settings.get('folders_on_page_count', 4)

    if current_page > 0:
        buttons = sorted_buttons[current_page * folders_on_page_count - folders_on_page_count:
                                 current_page * folders_on_page_count]
    else:
        buttons = sorted_buttons
    for button in buttons:
        folder_name_button = button

        # Добавляем кнопки на одну строку
        inline_markup.row(folder_name_button, InlineKeyboardButton(text='', callback_data='empty'),
                          InlineKeyboardButton(text='', callback_data='empty'))

    max_folder_num = len(sorted_buttons)
    last_page = math.ceil(max_folder_num / folders_on_page_count)
    if last_page > 1 and current_page > 0:
        inline_markup = await get_inline_markup_for_pages('folders', inline_markup, current_page,
                                                          last_page, folders_on_page_count,
                                                          max_folder_num, 'go_to_page_folders_')

    return inline_markup


async def get_inline_markup_items_in_folder(current_folder_id, current_page=1, search_text=None):
    # Получаем записи из коллекции items для текущей папки
    folder_items = await get_folder_items(current_folder_id, search_text)
    list_items_id = []
    for item_id in folder_items:
        list_items_id.append(item_id)

    settings = await get_from_user_collection('settings')
    items_on_page_count = settings.get('items_on_page_count', 4)

    if current_page > 0:
        current_items = list_items_id[current_page * items_on_page_count - items_on_page_count:
                                      current_page * items_on_page_count]
    else:
        current_items = list_items_id

    buttons = []
    for item_id in current_items:
        item = await get_item(item_id)

        if search_text:
            item.select_search_text(search_text, '[', ']')

        item_button_text = item.title or item.get_short_title()
        if item:
            buttons.append([InlineKeyboardButton(f"{smile_item} {item_button_text}", callback_data=f"item_{item_id}")])

    # Создаем разметку и отправляем сообщение с кнопками для каждой item
    items_inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=buttons)
    max_items_num = len(folder_items)
    last_page = math.ceil(max_items_num / items_on_page_count)
    if last_page > 1 and current_page > 0:
        items_inline_markup = await get_inline_markup_for_pages('items', items_inline_markup, current_page,
                                                                last_page, items_on_page_count,
                                                                max_items_num, 'go_to_page_items_')
    return items_inline_markup


async def get_inline_markup_for_pages(instance_text, inline_markup, current_page, last_page, on_page_count, max_num,
                                      callback_data_text):
    instance_smile = f'{smile_folder}' if instance_text == 'folders' else f'{smile_item}'

    prev_page = current_page - 1 if current_page - 1 > 0 else last_page
    next_page = current_page + 1 if current_page < last_page else 1

    first_on_page = (current_page - 1) * on_page_count + 1
    last_on_page = current_page * on_page_count
    if last_on_page > max_num:
        last_on_page = max_num
    current_nums = f"{first_on_page}..{last_on_page}" if first_on_page != last_on_page else f"{first_on_page}"
    mid_btn_text = f"{current_nums} {separator} {max_num} {instance_smile}"

    inline_markup.add(InlineKeyboardButton(text='⬅️', callback_data=f'{callback_data_text}prev_{prev_page}'),
                      InlineKeyboardButton(text=mid_btn_text, callback_data=f'show_all_{instance_text}'),
                      InlineKeyboardButton(text='➡️', callback_data=f'{callback_data_text}next_{next_page}'))

    return inline_markup


async def get_level_folders(folder_id):
    return len(folder_id.split('/')) - 1


async def get_page_info(folder_id, entities_key, current_page=None):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    pf = data.get('page_folders')

    page_entities = data.get(f'page_{entities_key}')
    level = await get_level_folders(folder_id)
    list_pages = page_entities.split('/')
    if current_page is None:
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
