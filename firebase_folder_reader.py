from firebase import get_user_data, ROOT_FOLDER_ID


async def get_current_folder_id(tg_user_id):
    """Возвращает текущий идентификатор папки для пользователя."""
    return (await get_user_data(tg_user_id)).get("current_folder", "")





async def get_user_folders_collection(tg_user_id):
    """Возвращает папки пользователя по идентификатору."""
    user_data = await get_user_data(tg_user_id)
    folders_collection = user_data.get("folders", {})
    return folders_collection





