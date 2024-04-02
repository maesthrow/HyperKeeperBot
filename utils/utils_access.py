import re

from enums.enums import AccessType
from load_all import bot
from models.folder_model import Folder
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.utils_folders import get_parent_folder_id
from utils.utils_folders_reader import get_folder


async def get_user_info(tg_user_id: str):
    chat = await bot.get_chat(chat_id=tg_user_id)
    info = [chat.full_name]
    if chat.username:
        info.append(f'@{chat.username}')
    user_info = ' '.join(info)
    return user_info


def get_access_str_by_type(access_type: AccessType):
    access_str = ''
    if access_type == AccessType.READ:
        access_str += 'к просмотру'
    elif access_type == AccessType.WRITE:
        access_str += 'к редактированию'
    access_str += ' содержимого'
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


async def get_access_users_info(folder: Folder) -> tuple:
    access_users_info_str = []
    access_users_info_entities = []
    folder_users_accesses = await get_folder_users_accesses(folder, {})
    if folder_users_accesses:
        number = 0
        for user_id, access_type in folder_users_accesses.items():
            access_str = ''
            if folder_users_accesses[user_id] == AccessType.READ.value:
                access_str = '👁️ просмотр содержимого' # 👓
            elif folder_users_accesses[user_id] == AccessType.WRITE.value:
                access_str = '✏️ редактирование содержимого' # 👓 🖊️
            user_info = await get_user_info(user_id)
            if access_str:
                number += 1
                access_users_info_str.append(f'👤 {number}. {user_info} - {access_str}')
                access_users_info_entities.append(
                    {
                        "user_id": user_id,
                        "number": number,
                        "user_name": get_user_name_from_user_info(user_info),
                        "access_type": access_type,
                    }
                )

    return '\n\n'.join(access_users_info_str), access_users_info_entities


def get_user_name_from_user_info(user_info: str):
    pattern = r'(.*?)( @\S+)'
    replaced = re.sub(pattern, r'\1', user_info, count=1, flags=re.DOTALL)
    return replaced
