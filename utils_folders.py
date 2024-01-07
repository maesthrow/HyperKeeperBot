from utils_folders_db import util_get_user_folders_count, util_get_user_folders_deep_count
from utils_items_db import util_get_items_count, util_get_items_deep_count


async def get_folder_statistic(folder_id) -> dict:
    dict_statistic = {}
    folders_count = await util_get_user_folders_count(folder_id)
    items_count = await util_get_items_count(folder_id)
    deep_folders_count = await util_get_user_folders_deep_count(folder_id)
    deep_items_count = await util_get_items_deep_count(folder_id)
    dict_statistic["folders_count"] = folders_count
    dict_statistic["items_count"] = items_count
    dict_statistic["deep_folders_count"] = deep_folders_count
    dict_statistic["deep_items_count"] = deep_items_count
    return dict_statistic
