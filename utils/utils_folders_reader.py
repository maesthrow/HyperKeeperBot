from firebase_pack.firebase_collection_folders import ROOT_FOLDER_ID
from utils.utils_data import get_folders_collection


async def get_folder_data(user_id, folder_id):
    folders_collection = await get_folders_collection(user_id)
    folder_ids = folder_id.split('/')
    target_folders = folders_collection
    folder_id_with_path = None
    target_folder = None
    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})
    return target_folder


async def get_folders_in_folder(user_id, folder_id=ROOT_FOLDER_ID):
    """Возвращает папки пользователя по идентификатору."""
    folders_collection = await get_folders_collection(user_id)

    folder_ids = folder_id.split('/')
    target_folders = folders_collection
    folder_id_with_path = None
    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})
    return target_folders


async def get_folders_count_in_folder(user_id, folder_id=ROOT_FOLDER_ID):
    folders_in_folder = await get_folders_in_folder(user_id, folder_id)
    return len(folders_in_folder)


async def get_user_folders_deep_count(user_id, folder_id=ROOT_FOLDER_ID):
    folders_in_folder = await get_folders_in_folder(user_id, folder_id)
    deep_count = len(folders_in_folder)
    for sub_folder_id in folders_in_folder:
        deep_count += await get_user_folders_deep_count(user_id, sub_folder_id)
    return deep_count