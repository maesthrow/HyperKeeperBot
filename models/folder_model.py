import uuid

from enums.enums import AccessType
from models.base_db_model import BaseDbModel
from utils.utils_handlers import get_folders_message_text


class Folder(BaseDbModel):
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

    # async def get_access_users_info(self) -> str:
    #     #return await get_users_info(self.folder_id)
    #     users_access_info = []
    #     users = self.get_access_users()
    #     if users:
    #         for tg_user_id, access_user in users.items():
    #             access_info = []
    #             if access_user['access_type'] == AccessType.READ.value:
    #                 access_info.append('просмотр содержимого 👓')
    #             elif access_user['access_type'][0] == AccessType.WRITE.value:
    #                 access_info.append('просмотр и изменение содержимого 👓🖊️')
    #             access_str = ', '.join(access_info)
    #             user_info = await get_user_info(tg_user_id)
    #             users_access_info.append(f'{user_info} - {access_str}')
    #     # else:
    #     #     if self.folder_id != ROOT_FOLDER_ID:
    #     #         folder_id = get_parent_folder_id(self.folder_id)
    #     #         folder: Folder = await get_folder(self.author_user_id, folder_id)
    #     #         if folder:
    #     #             users_access_info = await folder.get_access_users_info()
    #
    #     return '\n\n'.join(users_access_info)

    def get_access_user(self, user_id) -> AccessType:
        user_id = str(user_id)
        users = self.get_access_users()
        if users and user_id in users:
            return AccessType(users[user_id].get('access_type', ''))
        else:
            return AccessType.ABSENSE

    def set_access_user(self, user_id, access_type: AccessType):
        user_id = str(user_id)
        users = self.get_access_users()
        users[user_id] = {
            "access_type": access_type.value
        }
        self.set_access_user_recursive(user_id, access_type, self.folders)

    def set_access_user_recursive(self, user_id, access_type: AccessType, folders: dict):
        if not folders:
            return

        for folder in folders.values():
            # Устанавливаем или обновляем доступ для пользователя
            folder.setdefault('access', {}).setdefault('users', {})[user_id] = {
                "access_type": access_type.value
            }

            # Рекурсивно обрабатываем вложенные папки
            sub_folders = folder.get('folders')
            if sub_folders:
                self.set_access_user_recursive(user_id, access_type, sub_folders)

    def delete_access_user(self, user_id):
        user_id = str(user_id)
        users = self.get_access_users()
        users.pop(user_id)
        self.delete_access_user_recursive(user_id, self.folders)

    def delete_access_user_recursive(self, user_id, folders: dict):
        if not folders:
            return

        for folder in folders.values():
            # Удаляем доступ для пользователя, если он существует
            users = folder.get('access', {}).get('users', {})
            users.pop(user_id, None)

            # Рекурсивно обрабатываем вложенные папки
            sub_folders = folder.get('folders')
            if sub_folders:
                self.delete_access_user_recursive(user_id, sub_folders)

    def delete_access_all_users(self):
        self.access['users'] = {}
        self.delete_access_all_users_recursive(self.folders)

    def delete_access_all_users_recursive(self, folders: dict):
        if not folders:
            return

        for folder in folders.values():
            # Удаляем доступ для пользователя, если он существует
            access = folder.get('access', {})
            access['users'] = {}

            # Рекурсивно обрабатываем вложенные папки
            sub_folders = folder.get('folders')
            if sub_folders:
                self.delete_access_all_users_recursive(sub_folders)

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
