from firebase_pack.firebase_collection_folders import ROOT_FOLDER_ID
from models.folder_model import Folder
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


async def get_folder(user_id, folder_id: str = ROOT_FOLDER_ID):
    try:
        user_id = int(user_id)
    except:
        return None
    folder_data = await get_folder_data(user_id, folder_id)

    if "access" in folder_data:
        if "pin" not in folder_data["access"]:
            folder_data["access"]["pin"] = ''
        if "tokens" not in folder_data["access"]:
            folder_data["access"]["tokens"] = []
        if "users" not in folder_data["access"]:
            folder_data["access"]["users"] = {}
        access = folder_data["access"]
    else:
        access = {
            "pin": '',
            "tokens": [],
            "users": {}
        }

    if folder_data:
        folder = Folder(
            author_user_id=user_id,
            folder_id=folder_id,
            name=folder_data['name'],
            access=access,
            folders=folder_data['folders'],
            items=folder_data['items']
        )
        return folder

    return None


async def get_sub_folders(user_id, folder_id):
    folders = await get_folder_data(user_id, folder_id)
    return folders.get("folders", {})


async def get_sub_folder_names(user_id, folder_id):
    """Возвращает список всех folder_id внутри указанной папки."""
    folders_collection = await get_folders_collection(user_id)

    # Разбиваем идентификатор папки на части
    folder_ids = folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности папки
    for folder_part in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Получаем все folder_id внутри указанной папки
    sub_folder_ids = list(target_folders.keys())
    sub_folder_names = [await get_folder_name(user_id, sub_folder_id) for sub_folder_id in sub_folder_ids]

    return sub_folder_names


async def get_folder_name(user_id, folder_id=ROOT_FOLDER_ID):
    """Возвращает имя папки по её идентификатору."""
    folder_data = await get_folder_data(user_id, folder_id)
    return folder_data.get("name", "")


async def get_folder_pin(user_id, folder_id=ROOT_FOLDER_ID):
    """Возвращает PIN-код для папки по её идентификатору."""
    folder = await get_folder(user_id, folder_id)
    return folder.get_pin()




