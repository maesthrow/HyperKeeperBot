from models.item_model import Item
from utils.utils_folders_db import set_folders_collection
from utils.utils_items_writer import add_item_to_folder, delete_item, delete_all_items_in_folder, edit_item, move_item


async def util_add_item_to_folder(user_id, folder_id, item: Item):
    new_item_id = await add_item_to_folder(user_id, folder_id, item)
    if new_item_id:
        await set_folders_collection(user_id)
        return new_item_id
    else:
        return None


async def util_delete_item(user_id, item_id):
    result = await delete_item(user_id, item_id)
    if result:
        await set_folders_collection(user_id)
    return result


async def util_delete_all_items_in_folder(user_id, folder_id):
    result = await delete_all_items_in_folder(user_id, folder_id)
    if result:
        await set_folders_collection(user_id)
    return result


async def util_edit_item(user_id, item_id, item: Item):
    result = await edit_item(user_id, item_id, item)
    if result:
        await set_folders_collection(user_id)
    return result


async def util_move_item(user_id, item_id, dest_folder_id):
    new_movement_item_id = await move_item(user_id, item_id, dest_folder_id)
    if new_movement_item_id:
        await set_folders_collection(user_id)
    return new_movement_item_id

