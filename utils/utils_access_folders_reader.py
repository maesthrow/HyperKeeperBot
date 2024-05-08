from enums.enums import AccessType
from models.access_folder_model import AccessFolder
from models.folder_model import Folder
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.utils_data import get_accesses_from_user_collection
from utils.utils_folders import get_parent_folder_id
from utils.utils_folders_reader import get_folder


async def get_access_folder(user_id, from_user_id, folder_id) -> AccessFolder | None:
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


async def get_access_folders(user_id, from_user_id):
    try:
        user_id = int(user_id)
        from_user_id = int(from_user_id)
    except:
        return None

    access_folders = []

    accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
    if accesses_from_user_collection:
        for folder_id in accesses_from_user_collection:
            access_folder = AccessFolder(
                user_id=user_id,
                from_user_id=from_user_id,
                folder_id=folder_id,
                access_type=AccessType(accesses_from_user_collection[folder_id]['access_type']),
                pin=accesses_from_user_collection[folder_id]['pin']
            )
            access_folders.append(access_folder)

    return access_folders


async def get_current_access_type_from_user_folder(user_id, from_user_id, folder_id) -> AccessType:
    from_user_id = str(from_user_id)
    current_access_type = AccessType.ABSENSE
    # print(f'user_id = {user_id}')
    # print(f'from_user_id = {from_user_id}')
    accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
    # print(f'folder_id = {folder_id}')
    print(f'accesses_from_user_collection = {accesses_from_user_collection}')
    if not accesses_from_user_collection:
        return current_access_type
    elif folder_id in accesses_from_user_collection:
        current_access_type = AccessType(accesses_from_user_collection[folder_id].get('access_type', ''))
    if current_access_type in (AccessType.ABSENSE, AccessType.READ):
        folder: Folder = await get_folder(from_user_id, folder_id)
        if folder:
            current_access_type = folder.get_access_user(user_id)
        if current_access_type in (AccessType.ABSENSE, AccessType.READ):
            if folder_id != ROOT_FOLDER_ID:
                folder_id = get_parent_folder_id(folder_id)
                return await get_current_access_type_from_user_folder(user_id, from_user_id, folder_id)

    return current_access_type
