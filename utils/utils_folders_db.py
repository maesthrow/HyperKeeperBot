from utils.utils_data import set_folders_collection
from utils.utils_folders_writer import add_new_folder, delete_folder, rename_folder


async def util_add_new_folder(user_id, new_folder_name, parent_folder_id):
    result = await add_new_folder(user_id, new_folder_name, parent_folder_id)
    if result:
        await set_folders_collection(user_id)
    return result


async def util_delete_folder(user_id, folder_id):
    result = await delete_folder(user_id, folder_id)
    if result:
        await set_folders_collection(user_id)
    return result


async def util_rename_folder(user_id, folder_id, folder_new_name):
    result = await rename_folder(user_id, folder_id, folder_new_name)
    if result:
        await set_folders_collection(user_id)
    return result

