from aiogram.types import User, Chat

from firebase import ROOT_FOLDER_ID
from firebase_folder_reader import get_user_folders_collection
from firebase_folder_writer import add_new_folder, delete_folder, rename_folder
from load_all import dp


async def get_folders_collection():
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    folders_collection = data.get('folders_collection', None)

    if not folders_collection:
        folders_collection = await get_user_folders_collection(tg_user.id)
        await set_folders_collection(folders_collection)

    return folders_collection


async def set_folders_collection(folders_collection=None):
    tg_user = User.get_current()
    chat = Chat.get_current()
    if not folders_collection:
        folders_collection = await get_user_folders_collection(tg_user.id)
    await dp.storage.update_data(user=tg_user, chat=chat,
                                 data={'folders_collection': folders_collection})


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