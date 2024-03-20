import uuid

from enums.enums import AccessType
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.utils_access import get_user_info
from utils.utils_folders import get_parent_folder_id
from utils.utils_folders_reader import get_folders_in_folder, get_folder
from utils.utils_handlers import get_folders_message_text


class Folder:
    def __init__(
            self,
            author_user_id: int,
            folder_id: str,
            name: str,
            access: {} = None,
            folders: {} = None,
            items: {} = None
    ):
        self.author_user_id = author_user_id
        self.folder_id = folder_id
        self.name = name
        self.access = access
        self.folders = folders
        self.items = items

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "access": self.access,
            "folders": self.folders,
            "items": self.items,
        }

    async def get_full_name(self):
        full_name = await get_folders_message_text(self.author_user_id, self.folder_id)
        return full_name

    def get_pin(self):
        return self.access.get('pin', '') if self.access else ''

    def set_pin(self, new_pin):
        if self.access:
            self.access['pin'] = new_pin
        else:
            self.access = {'pin': new_pin}

    def remove_pin(self):
        self.set_pin('')

    def has_access_users(self):
        return len(self.get_access_users()) > 0

    def get_access_users(self) -> dict:
        users = {}
        if self.access:
            users = self.access.get('users', {})
        return users

    async def get_access_users_info(self) -> str:
        users_access_info = []
        users = self.get_access_users()
        if users:
            for tg_user_id, access_user in users.items():
                access_info = []
                if access_user['access_type'] == AccessType.READ.value:
                    access_info.append('просмотр содержимого 👓')
                elif access_user['access_type'][0] == AccessType.WRITE.value:
                    access_info.append('просмотр и изменение содержимого 👓🖊️')
                access_str = ', '.join(access_info)
                user_info = await get_user_info(tg_user_id)
                users_access_info.append(f'{user_info} - {access_str}')
        # else:
        #     if self.folder_id != ROOT_FOLDER_ID:
        #         folder_id = get_parent_folder_id(self.folder_id)
        #         folder: Folder = await get_folder(self.author_user_id, folder_id)
        #         if folder:
        #             users_access_info = await folder.get_access_users_info()

        return '\n\n'.join(users_access_info)

    def add_access_user(self, user_id, access_type: AccessType):
        user_id = str(user_id)
        users = self.get_access_users()
        users[user_id] = {
            "access_type": access_type.value
        }

    def get_access_tokens(self) -> list:
        tokens = list()
        if self.access:
            tokens = self.access.get('tokens', [])
        return tokens

    def contains_token(self, token: str) -> bool:
        tokens = self.get_access_tokens()
        if tokens:
            return token in tokens
        return False

    def new_token(self):
        new_token = str(uuid.uuid4())[:8]
        self.get_access_tokens().append(new_token)
        return new_token

    def use_token(self, token: str) -> bool:
        if self.contains_token(token):
            self.get_access_tokens().remove(token)
            return True
        return False
