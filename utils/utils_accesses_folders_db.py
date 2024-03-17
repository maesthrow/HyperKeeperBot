from models.access_folder_model import AccessFolder
from utils.utils_accesses_folders_writer import add_access_folder_from_user, delete_access_folder_from_user, \
    edit_access_folder_from_user
from utils.utils_data import set_accesses_from_user_collection, get_accesses_from_user_collection


async def util_access_add_from_user_folder(user_id, from_user_id, folder_id, access_type):
    result = await add_access_folder_from_user(user_id, from_user_id, folder_id, access_type)
    if result:
        value = AccessFolder.get_dict_by_properties(access_type)
        await update_data(user_id, from_user_id, folder_id, value)
    return result


async def util_access_delete_from_user_folder(user_id, from_user_id, folder_id):
    result = await delete_access_folder_from_user(user_id, from_user_id, folder_id)
    if result:
        await update_data(user_id, from_user_id, folder_id, value={})
    return result


async def util_access_edit_from_user_folder(access_folder: AccessFolder):
    result = await edit_access_folder_from_user(access_folder)
    if result:
        value = access_folder.to_dict()
        await update_data(access_folder.user_id, access_folder.from_user_id, access_folder.folder_id, value)
    return result


async def update_data(user_id, from_user_id, folder_id, value):
    access_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
    if access_from_user_collection:
        access_from_user_collection[folder_id] = value
    else:
        access_from_user_collection = {
            folder_id: value
        }
    await set_accesses_from_user_collection(user_id, from_user_id, access_from_user_collection)
