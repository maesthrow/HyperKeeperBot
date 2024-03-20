from aiogram.types import User

from mongo_db.mongo_collection_accesses import add_user_accesses, get_user_accesses_collection
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID, get_user_folders_collection, add_user_folders
from mongo_db.mongo_collection_users import get_user_collection, set_user_collection, add_user
from utils.data_manager import get_data, set_data


async def add_user_collections(tg_user: User):
    """Добавляет пользователя и все его коллекции в базу данных, если их еще нет"""
    await add_user(tg_user)
    await add_user_folders(tg_user)
    await add_user_accesses(tg_user)


async def set_current_folder_id(user_id, folder_id=ROOT_FOLDER_ID):
    """Устанавливает новый идентификатор текущей папки для пользователя."""
    data = await get_data(user_id)
    data['current_folder_id'] = folder_id
    await set_data(user_id, data)


async def get_current_folder_id(user_id):
    """Устанавливает новый идентификатор текущей папки для пользователя."""
    data = await get_data(user_id)
    current_folder_id = data.get('current_folder_id')
    print(f'user_id = {user_id}, current_folder_id = {current_folder_id}')
    if not current_folder_id:
        current_folder_id = ROOT_FOLDER_ID
    return current_folder_id


async def get_folders_collection(user_id):
    data = await get_data(user_id)
    folders_collection = data.get('folders_collection', None)
    if not folders_collection:
        folders_collection = await get_user_folders_collection(user_id)
        await set_folders_collection(user_id, folders_collection)

    return folders_collection


async def set_folders_collection(user_id, folders_collection=None):
    if not folders_collection:
        folders_collection = await get_user_folders_collection(user_id)

    data = await get_data(user_id)
    data['dict_search_data'] = None
    data['folders_collection'] = folders_collection
    await set_data(user_id, data)


async def get_from_user_collection(user_id, collection_name: str):
    data = await get_data(user_id)
    collection = data.get(f'{collection_name}_collection', None)

    if not collection:
        collection = await get_user_collection(user_id, collection_name)
        await set_to_user_collection(user_id, collection_name, collection)

    return collection


async def set_to_user_collection(user_id, collection_name: str, collection=None):
    if not collection:
        collection = await get_user_collection(user_id, collection_name)
    else:
        await set_user_collection(user_id, collection_name, collection)

    data = await get_data(user_id)
    data[f'{collection}_collection'] = collection
    await set_data(user_id, data)


async def get_accesses_collection(user_id):
    data = await get_data(user_id)
    accesses_collection = data.get('accesses_collection', None)
    if not accesses_collection:
        accesses_collection = await get_user_accesses_collection(user_id)
        await set_accesses_collection(user_id, accesses_collection)

    return accesses_collection


async def set_accesses_collection(user_id, accesses_collection=None):
    if not accesses_collection:
        accesses_collection = await get_user_accesses_collection(user_id)

    data = await get_data(user_id)
    data['accesses_collection'] = accesses_collection
    await set_data(user_id, data)


async def get_accesses_from_user_collection(user_id, from_user_id):
    accesses_collection = await get_accesses_collection(user_id)
    print(f'accesses_collection {accesses_collection}')
    if accesses_collection:
        accesses_from_user_collection = accesses_collection.get(from_user_id, {})
    else:
        accesses_from_user_collection = await set_accesses_from_user_collection(user_id, str(from_user_id))
    return accesses_from_user_collection


async def set_accesses_from_user_collection(user_id, from_user_id, from_user_collection=None):
    accesses_collection = await get_accesses_collection(user_id)
    if not from_user_collection:
        from_user_collection = {}
    accesses_collection[from_user_id] = from_user_collection
    await set_accesses_collection(user_id, accesses_collection)
    return accesses_collection[from_user_id]


