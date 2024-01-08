import aiogram.types

from firebase.firebase_folder_writer import add_new_folder, delete_folder, rename_folder
from utils.utils_data import set_folders_collection


async def util_add_new_folder(new_folder_name, parent_folder_id):
    tg_user = aiogram.types.User.get_current()
    result = await add_new_folder(tg_user.id, new_folder_name, parent_folder_id)
    if result:
        await set_folders_collection()
    return result


async def util_delete_folder(folder_id):
    tg_user = aiogram.types.User.get_current()
    result = await delete_folder(tg_user.id, folder_id)
    if result:
        await set_folders_collection()
    return result


async def util_rename_folder(folder_id, folder_new_name):
    tg_user = aiogram.types.User.get_current()
    result = await rename_folder(tg_user.id, folder_id, folder_new_name)
    if result:
        await set_folders_collection()
    return result

