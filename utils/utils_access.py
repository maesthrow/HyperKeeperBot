from enums.enums import AccessType
from load_all import bot
from models.folder_model import Folder
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.utils_folders import get_parent_folder_id
from utils.utils_folders_reader import get_folder


async def get_user_info(tg_user_id: str):
    chat = await bot.get_chat(chat_id=tg_user_id)
    info = []
    if chat.username:
        info.append(f'@{chat.username}')
    info.append(chat.full_name)
    user_info = ' '.join(info)
    return user_info


def get_access_str_by_type(access_type: AccessType):
    access_str = 'к просмотру'
    if access_type == AccessType.READ:
        access_str += ' содержимого'
    elif access_type == AccessType.WRITE:
        access_str += ' и изменению содержимого'
    return access_str


async def get_folder_users_accesses(folder: Folder, users_accesses: dict) -> dict:
    users = folder.get_access_users()
    if users:
        for user_id, access_user in users.items():
            if access_user['access_type'] == AccessType.WRITE.value or user_id not in users_accesses:
                users_accesses[user_id] = access_user['access_type']
    if folder.folder_id != ROOT_FOLDER_ID:
        folder_id = get_parent_folder_id(folder.folder_id)
        folder: Folder = await get_folder(folder.author_user_id, folder_id)
        if folder:
            users_accesses = await get_folder_users_accesses(folder, users_accesses)
    return users_accesses


async def get_access_users_info(folder: Folder) -> str:
    users_access_info = []
    folder_users_accesses = await get_folder_users_accesses(folder, {})
    if folder_users_accesses:
        for user_id, access_type in folder_users_accesses.items():
            access_str = ''
            if folder_users_accesses[user_id] == AccessType.READ.value:
                access_str = '👓 просмотр содержимого'
            elif folder_users_accesses[user_id] == AccessType.WRITE.value:
                access_str = '👓🖊️ просмотр и изменение содержимого'
            user_info = await get_user_info(user_id)
            if access_str:
                users_access_info.append(f'{user_info} - {access_str}')

    return '\n\n'.join(users_access_info)
