from aiogram.types import User

from firebase_item_writer import add_item_to_folder, delete_item, delete_all_items_in_folder, edit_item
from models import Item
from utils_folders_db import set_folders_collection


async def util_add_item_to_folder(folder_id, item: Item):
    tg_user = User.get_current()
    result = await add_item_to_folder(tg_user.id, folder_id, item)
    if result:
        await set_folders_collection()
    return result


async def util_delete_item(item_id):
    tg_user = User.get_current()
    result = await delete_item(tg_user.id, item_id)
    if result:
        await set_folders_collection()
    return result


async def util_delete_all_items_in_folder(folder_id):
    tg_user = User.get_current()
    result = await delete_all_items_in_folder(tg_user.id, folder_id)
    if result:
        await set_folders_collection()
    return result


async def util_edit_item(item_id, item: Item):
    tg_user = User.get_current()
    result = await edit_item(tg_user.id, item_id, item)
    if result:
        await set_folders_collection()
    return result