from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.utils_data import get_folders_collection


async def get_folder_path_names(user_id, folder_id=ROOT_FOLDER_ID):
    """Возвращает имена папок по пути к папке."""
    folders_collection = await get_folders_collection(user_id)
    folder_ids = folder_id.split('/')
    path_names = []
    target_folders = folders_collection
    folder_id_with_path = None

    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folder_name = target_folder.get("name", "")
        path_names.append(target_folder_name)
        target_folders = target_folder.get("folders", {})

    return " / ".join(path_names) + " /"


async def get_folders_message_text(user_id, current_folder_id, current_folder_path_names=None):
    if not current_folder_path_names:
        current_folder_path_names = await get_folder_path_names(user_id, current_folder_id)
    folders_message_text = f"🗂️ {current_folder_path_names}"
    return folders_message_text
