from load_all import bot
from utils.utils_data import get_accesses_from_user_collection


async def get_user_info(tg_user_id: str):
    chat = await bot.get_chat(chat_id=tg_user_id)
    info = []
    if chat.username:
        info.append(f'@{chat.username}')
    info.append(chat.full_name)
    user_info = ' '.join(info)
    return user_info


def get_access_str_by_type(access_type: str):
    access_str = 'к просмотру'
    if access_type[0] == 'r':
        access_str += ' содержимого'
    elif access_type[0] == 'w':
        access_str += ' и изменению содержимого'
    return access_str


async def check_access_folder_from_user(user_id, from_user_id, folder_id, access_type):
    accesses_from_user_collection = await get_accesses_from_user_collection(user_id, from_user_id)
    access_folder_collection = accesses_from_user_collection.get(folder_id, {})
    #временный return
    return access_folder_collection is False
