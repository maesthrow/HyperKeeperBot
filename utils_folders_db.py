from aiogram.types import User, Chat

from firebase import ROOT_FOLDER_ID
from firebase_folder_reader import get_user_folders_collection
from firebase_folder_writer import add_new_folder, delete_folder, rename_folder, get_folders_collection, \
    set_folders_collection
from load_all import dp





async def util_get_user_folders(folder_id=ROOT_FOLDER_ID):
    """Возвращает папки пользователя по идентификатору."""
    folders_collection = await get_folders_collection()

    folder_ids = folder_id.split('/')
    target_folders = folders_collection
    folder_id_with_path = None
    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})
    return target_folders


async def util_add_new_folder(new_folder_name, parent_folder_id):
    tg_user = User.get_current()
    result = await add_new_folder(tg_user.id, new_folder_name, parent_folder_id)
    if result:
        await set_folders_collection()
    return result


async def util_delete_folder(folder_id):
    tg_user = User.get_current()
    result = await delete_folder(tg_user.id, folder_id)
    if result:
        await set_folders_collection()
    return result


async def util_rename_folder(folder_id, folder_new_name):
    tg_user = User.get_current()
    result = await rename_folder(tg_user.id, folder_id, folder_new_name)
    if result:
        await set_folders_collection()
    return result


async def get_folder_name(folder_id=ROOT_FOLDER_ID):
    """Возвращает имя папки по её идентификатору."""
    folder_data = await get_folder_data(folder_id)
    return folder_data.get("name", "")


async def get_folder_path_names(folder_id=ROOT_FOLDER_ID):
    """Возвращает имена папок по пути к папке."""
    folders_collection = await get_folders_collection()
    folder_ids = folder_id.split('/')
    target_folders = folders_collection
    folder_id_with_path = None
    path_names = None
    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folder_name = target_folder.get("name", "")
        path_names = f"{path_names} > {target_folder_name}" if path_names else target_folder_name
        target_folders = target_folder.get("folders", {})
    return f"{path_names}:"


async def get_folder_data(folder_id):
    folders_collection = await get_folders_collection()
    folder_ids = folder_id.split('/')
    target_folders = folders_collection
    folder_id_with_path = None
    target_folder = None
    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})
    return target_folder


async def get_sub_folder_names(folder_id):
    """Возвращает список всех folder_id внутри указанной папки."""
    folders_collection = await get_folders_collection()

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
    sub_folder_names = [await get_folder_name(sub_folder_id) for sub_folder_id in sub_folder_ids]

    return sub_folder_names
