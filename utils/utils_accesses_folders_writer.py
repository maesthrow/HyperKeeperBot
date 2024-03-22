from enums.enums import AccessType
from models.access_folder_model import AccessFolder
from mongo_db.mongo_collection_accesses import set_user_accesses_from_user_collection
from utils.utils_data import get_accesses_from_user_collection


async def add_access_folder_from_user(user_id, from_user_id, folder_id, access_type: AccessType):
    """Добавляет в доступы пользователя папку другого пользователя."""
    try:
        accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
        print(f'test accesses_from_user_collection {accesses_from_user_collection}')
        must_remove_folders = []
        must_add = True
        for has_folder_id in accesses_from_user_collection.keys():
            if len(has_folder_id) > len(folder_id) and has_folder_id[:len(folder_id)] == folder_id:
                must_remove_folders.append(has_folder_id)
            if len(folder_id) > len(has_folder_id) and folder_id[:len(has_folder_id)] == has_folder_id:
                must_add = False
        for remove_folder_id in must_remove_folders:
            accesses_from_user_collection.pop(remove_folder_id)
        if must_add:
            accesses_from_user_collection[folder_id] = AccessFolder.get_dict_by_properties(access_type)

        await set_user_accesses_from_user_collection(user_id, from_user_id, accesses_from_user_collection)
        return True
    except Exception as e:
        print(f"Ошибка при добавлении доступа {e}")
        return False


async def delete_access_folder_from_user(user_id, from_user_id, folder_id):
    """Удаляет из доступов пользователя папку другого пользователя."""
    accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
    if accesses_from_user_collection:
        if folder_id in accesses_from_user_collection:
            del accesses_from_user_collection[folder_id]
            await set_user_accesses_from_user_collection(user_id, from_user_id, accesses_from_user_collection)
            return True
    return False


async def edit_access_folder_from_user(access_folder: AccessFolder):
    """Редактирует папку другого пользователя в доступов пользователя."""
    user_id = int(access_folder.user_id)
    from_user_id = int(access_folder.from_user_id)
    accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)

    if access_folder:
        accesses_from_user_collection[access_folder.folder_id] = access_folder.to_dict()
        await set_user_accesses_from_user_collection(user_id, from_user_id, accesses_from_user_collection)
        return True

    return False

