from aiogram.types import User, Chat

from firebase.firebase_collection_folders import ROOT_FOLDER_ID, get_user_folders_collection
from firebase.firebase_collection_users import get_user_collection
from load_all import dp


async def set_current_folder_id(folder_id=ROOT_FOLDER_ID):
    """Устанавливает новый идентификатор текущей папки для пользователя."""
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    data['current_folder_id'] = folder_id
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)


async def get_current_folder_id(tg_user=None, chat=None):
    """Устанавливает новый идентификатор текущей папки для пользователя."""
    if tg_user is None and chat is None:
        tg_user = User.get_current()
        chat = Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    current_folder_id = data.get('current_folder_id')
    if not current_folder_id:
        current_folder_id = ROOT_FOLDER_ID
    return current_folder_id


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

    data = await dp.storage.get_data(chat=chat, user=tg_user)
    data['dict_search_data'] = None
    data['folders_collection'] = folders_collection

    await dp.storage.update_data(user=tg_user, chat=chat, data=data)


async def get_from_user_collection(collection_name: str):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    collection = data.get(f'{collection_name}_collection', None)

    if not collection:
        collection = await get_user_collection(tg_user.id, collection_name)
        await set_to_user_collection(collection)

    return collection


async def set_to_user_collection(collection_name: str, collection=None):
    tg_user = User.get_current()
    chat = Chat.get_current()
    if not collection:
        collection = await get_user_collection(tg_user.id, collection_name)

    data = await dp.storage.get_data(chat=chat, user=tg_user)
    data[f'{collection}_collection'] = collection

    await dp.storage.update_data(user=tg_user, chat=chat, data=data)