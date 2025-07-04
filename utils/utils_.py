import math
import re

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from callbacks.callbackdata import FolderCallback, ItemShowCallback, MarkFileCallback
from enums.enums import Environment
from load_all import bot
from utils.data_manager import get_data
from utils.utils_button_manager import check_button_exists, file_mark_on, file_mark_off
from utils.utils_data import get_from_user_collection
from utils.utils_folders_reader import get_folders_in_folder
from utils.utils_items_reader import get_folder_items, get_simple_item

# folder_callback = CallbackFolder()
# folders_on_page_count = 4
# items_on_page_count = 4

invisible_char = "\u00A0"
separator = 'из'
smile_folder = '🗂️'
smile_item = '📄'
smile_file = '🗃️'


async def get_environment(user_id):
    data = await get_data(user_id)
    keyboard: ReplyKeyboardMarkup = data.get('current_keyboard', None)
    environment: Environment = Environment.FOLDERS
    for tmp_environment in Environment:
        if check_button_exists(keyboard, tmp_environment.value):
            environment = tmp_environment
    return environment


def get_inline_markup_for_accept_cancel(text_accept, text_cancel, callback_data):
    inline_markup = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=
        [
            [
                InlineKeyboardButton(text=text_accept, callback_data=f"{callback_data}_accept"),
                InlineKeyboardButton(text=text_cancel, callback_data=f"{callback_data}_cancel")
            ],
        ]
    )
    return inline_markup


async def create_folder_button(folder_id, folder_name):
    return InlineKeyboardButton(
        text=f"{smile_folder} {folder_name}",
        callback_data=FolderCallback(folder_id=folder_id).pack()  # folder_callback.new(folder_id=folder_id)
    )


async def get_folders_for_page(user_id, current_folder_id, current_page):
    user_folders: dict = await get_folders_in_folder(user_id, current_folder_id)
    sorted_folders = sorted(user_folders.items(), key=lambda item: sort_folders_func(item))  # item[1].get("name"))

    settings = await get_from_user_collection(user_id, 'settings')
    folders_on_page_count = settings.get('folders_on_page_count', 4)

    if current_page > 0:
        folders = sorted_folders[current_page * folders_on_page_count - folders_on_page_count:
                                 current_page * folders_on_page_count]
    else:
        folders = sorted_folders
    return folders


def sort_folders_func(item):
    name = item[1].get("name")
    match = re.match(r'\d+', name)
    if match:
        return False, int(match.group())
    else:
        return True, name


async def get_sorted_folders(user_id, current_folder_id):
    user_folders: dict = await get_folders_in_folder(user_id, current_folder_id)
    sorted_folders = sorted(user_folders.items(), key=sort_folders_func)
    return sorted_folders


async def get_inline_markup_folders(user_id, current_folder_id, current_page):
    sorted_folders = await get_sorted_folders(user_id, current_folder_id)

    settings = await get_from_user_collection(user_id, 'settings')
    folders_on_page_count = settings.get('folders_on_page_count', 6)

    if current_page > 0:
        folders = sorted_folders[current_page * folders_on_page_count - folders_on_page_count:
                                 current_page * folders_on_page_count]
    else:
        folders = sorted_folders

    folder_buttons = [
        await create_folder_button(folder_id, folder_data.get("name"))
        for folder_id, folder_data in folders
    ]

    folders_inline_markup = InlineKeyboardMarkup(inline_keyboard=[], row_width=3)

    buttons_row = []
    for button in folder_buttons:
        folder_name_button = button
        if len(buttons_row) < 2:
            buttons_row.append(folder_name_button)
        if len(buttons_row) == 2:
            folders_inline_markup.inline_keyboard.append(buttons_row)
            buttons_row = []
    if len(buttons_row) > 0:
        folders_inline_markup.inline_keyboard.append(buttons_row)

    max_folder_num = len(sorted_folders)
    last_page = math.ceil(max_folder_num / folders_on_page_count)
    if last_page > 1 and current_page > 0:
        folders_inline_markup = await get_inline_markup_for_pages('folders', folders_inline_markup, current_page,
                                                                  last_page, folders_on_page_count,
                                                                  max_folder_num, 'go_to_page_folders_')

    return folders_inline_markup


async def check_current_items_page(user_id, current_folder_id, current_page):
    folder_items = await get_folder_items(user_id, current_folder_id)

    settings = await get_from_user_collection(user_id, 'settings')
    items_on_page_count = settings.get('items_on_page_count', 4)

    current_page = 1 if len(folder_items) <= items_on_page_count else current_page

    return current_page, folder_items


async def get_inline_markup_items_in_folder(
        user_id, current_folder_id, current_page=1, search_text=None, folder_items=None
):
    # Получаем записи из коллекции items для текущей папки
    if not folder_items:
        folder_items = await get_folder_items(user_id, current_folder_id, search_text)
    list_items_id = [item_id for item_id in folder_items]

    settings = await get_from_user_collection(user_id, 'settings')
    items_on_page_count = settings.get('items_on_page_count', 4)

    if current_page > 0:
        current_items = list_items_id[current_page * items_on_page_count - items_on_page_count:
                                      current_page * items_on_page_count]
    else:
        current_items = list_items_id

    buttons = []
    for item_id in current_items:
        item = await get_simple_item(user_id, item_id)

        # if search_text:
        #     item.select_search_text(search_text, '[', ']')

        item_button_text = item.get_inline_title()
        if item:
            buttons.append([InlineKeyboardButton(
                text=f"{smile_item} {item_button_text}",
                callback_data=ItemShowCallback(author_user_id=user_id, item_id=item_id, with_folders=False).pack())])
            # f"item_{item_id}")])

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

    inline_markup.inline_keyboard.append([
        InlineKeyboardButton(text='◀️', callback_data=f'{callback_data_text}prev_{prev_page}'),
        InlineKeyboardButton(text=mid_btn_text, callback_data=f'storage_show_all_{instance_text}'),
        InlineKeyboardButton(text='▶️', callback_data=f'{callback_data_text}next_{next_page}')
    ])

    return inline_markup


def get_level_folders(folder_id):
    return len(folder_id.split('/')) - 1


async def get_page_info(user_id, folder_id, entities_key, current_page=None):
    data = await get_data(user_id)

    page_entities = data.get(f'page_{entities_key}')
    level = get_level_folders(folder_id)
    if page_entities:
        list_pages = page_entities.split('/')
    else:
        list_pages = []
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


async def update_message_reply_markup(user_id, delete_file_ids, file_message, mark):
    inline_markup = file_message.reply_markup
    mark_button = inline_markup.inline_keyboard[-1][0]
    call_data = MarkFileCallback.unpack(mark_button.callback_data)
    if call_data.file_id in delete_file_ids and delete_file_ids[call_data.file_id][1] != mark:
        delete_file_ids[call_data.file_id][1] = mark
        mark_button.text = file_mark_on if mark else file_mark_off
        inline_markup.inline_keyboard[-1][0] = mark_button
        return await bot.edit_message_reply_markup(
            chat_id=user_id, message_id=file_message.message_id, reply_markup=inline_markup
        )
    return None

