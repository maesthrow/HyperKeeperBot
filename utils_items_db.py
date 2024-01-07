from aiogram.types import User

from firebase import ROOT_FOLDER_ID
from firebase_item_reader import get_folder_items
from firebase_item_writer import add_item_to_folder, delete_item, delete_all_items_in_folder, edit_item, move_item
from models import Item
from utils_folders_db import set_folders_collection, util_get_user_folders


async def util_add_item_to_folder(folder_id, item: Item):
    tg_user = User.get_current()
    new_item_id = await add_item_to_folder(tg_user.id, folder_id, item)
    if new_item_id:
        await set_folders_collection()
    return new_item_id is not None


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


async def util_move_item(item_id, dest_folder_id):
    tg_user = User.get_current()
    new_movement_item_id = await move_item(tg_user.id, item_id, dest_folder_id)
    if new_movement_item_id:
        await set_folders_collection()
    return new_movement_item_id


async def util_get_items_count(folder_id=ROOT_FOLDER_ID):
    items_in_folder = await get_folder_items(folder_id)
    return len(items_in_folder)


async def util_get_items_deep_count(folder_id=ROOT_FOLDER_ID):
    items_in_folder = await get_folder_items(folder_id)
    deep_count = len(items_in_folder)
    folders_in_folder = await util_get_user_folders(folder_id)
    for sub_folder_id in folders_in_folder:
        deep_count += await util_get_items_deep_count(sub_folder_id)
    return deep_count
