from firebase import get_user_data, ROOT_FOLDER_ID


async def get_user_folders_collection(tg_user_id):
    """Возвращает папки пользователя по идентификатору."""
    user_data = await get_user_data(tg_user_id)
    folders_collection = user_data.get("folders", {})
    return folders_collection





