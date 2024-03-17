# async def get_accesses_data(user_id, folder_id):
#     accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
#
#     folders_collection = await get_folders_collection(user_id)
#     folder_ids = folder_id.split('/')
#     target_folders = folders_collection
#     folder_id_with_path = None
#     target_folder = None
#     for folder_id in folder_ids:
#         folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
#         target_folder = target_folders.get(folder_id_with_path, {})
#         target_folders = target_folder.get("folders", {})
#     return target_folder
from models.access_folder_model import AccessFolder
from utils.utils_data import get_accesses_from_user_collection


async def get_access_folder(user_id, from_user_id, folder_id):
    try:
        user_id = int(user_id)
        from_user_id = int(from_user_id)
    except:
        return None

    accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
    if accesses_from_user_collection:
        access_folder = AccessFolder(
            user_id=user_id,
            from_user_id=from_user_id,
            folder_id=folder_id,
            access_type=accesses_from_user_collection[folder_id]['access_type'],
            pin=accesses_from_user_collection[folder_id]['pin']
        )
        return access_folder

    return None
