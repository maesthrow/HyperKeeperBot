from firebase.firebase_ import ROOT_FOLDER_ID
from firebase.firebase_folder_reader import get_folders_in_folder
from firebase.firebase_item_reader import get_folder_items


async def util_get_items_count(folder_id=ROOT_FOLDER_ID):
    items_in_folder = await get_folder_items(folder_id)
    return len(items_in_folder)


async def util_get_items_deep_count(folder_id=ROOT_FOLDER_ID):
    items_in_folder = await get_folder_items(folder_id)
    deep_count = len(items_in_folder)
    folders_in_folder = await get_folders_in_folder(folder_id)
    for sub_folder_id in folders_in_folder:
        deep_count += await util_get_items_deep_count(sub_folder_id)
    return deep_count


def get_word_items_by_count(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "запись"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return "записи"
    else:
        return "записей"
