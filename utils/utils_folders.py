import aiogram

from utils.utils_folders_reader import get_folders_count_in_folder, get_user_folders_deep_count
from utils.utils_statistic import util_get_items_count, util_get_items_deep_count

invalid_chars = r'/\:,.*?"<>|'


def is_valid_folder_name(name):
    return all(char not in invalid_chars for char in name)


def clean_folder_name(name):
    cleaned_name = ''.join(char if char not in invalid_chars and char not in '\n\r' else ' ' for char in name)
    return cleaned_name


def get_parent_folder_id(folder_id):
    return folder_id.rsplit('/', 1)[0]


def is_storage_message(message: aiogram.types.Message):
    return message.text.startswith("🗂️ Хранилище")


async def get_folder_statistic(user_id, folder_id) -> dict:
    dict_statistic = {}
    folders_count = await get_folders_count_in_folder(user_id, folder_id)
    items_count = await util_get_items_count(user_id, folder_id)
    deep_folders_count = await get_user_folders_deep_count(user_id, folder_id)
    deep_items_count = await util_get_items_deep_count(user_id, folder_id)
    dict_statistic["folders_count"] = folders_count
    dict_statistic["items_count"] = items_count
    dict_statistic["deep_folders_count"] = deep_folders_count
    dict_statistic["deep_items_count"] = deep_items_count
    return dict_statistic

