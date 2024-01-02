from firebase import get_user_data, ROOT_FOLDER_ID


async def get_current_folder_id(tg_user_id):
    """Возвращает текущий идентификатор папки для пользователя."""
    return (await get_user_data(tg_user_id)).get("current_folder", "")


def get_parent_folder_id(folder_id):
    return folder_id.rsplit('/', 1)[0]


async def get_user_folders_collection(tg_user_id):
    """Возвращает папки пользователя по идентификатору."""
    user_data = await get_user_data(tg_user_id)
    folders_collection = user_data.get("folders", {})
    return folders_collection


async def get_folder_data(tg_user_id, folder_id):
    """Возвращает данные папки по её идентификатору."""
    user_data = await get_user_data(tg_user_id)
    folders_collection = user_data.get("folders", {})
    folder_ids = folder_id.split('/')
    target_folders = folders_collection
    folder_id_with_path = None
    target_folder = None
    for folder_id in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_id}" if folder_id_with_path else folder_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})
    return target_folder


async def get_folder_name(tg_user_id, folder_id=ROOT_FOLDER_ID):
    """Возвращает имя папки по её идентификатору."""
    folder_data = await get_folder_data(tg_user_id, folder_id)
    return folder_data.get("name", "")


async def get_folder_path_names(tg_user_id, folder_id=ROOT_FOLDER_ID):
    """Возвращает имена папок по пути к папке."""
    user_data = await get_user_data(tg_user_id)
    folders_collection = user_data.get("folders", {})
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
