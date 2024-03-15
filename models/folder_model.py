from utils.utils_access import get_user_info
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

    def get_pin(self):
        return self.access.get('pin', '') if self.access else ''

    def set_pin(self, new_pin):
        if self.access:
            self.access['pin'] = new_pin
        else:
            self.access = {'pin': new_pin}

    def remove_pin(self):
        self.set_pin('')

    def has_users(self):
        return len(self.get_access_users()) > 0

    def get_access_users(self) -> dict:
        users = {}
        if self.access:
            users = self.access.get('users', {})
        return users

    async def get_users_info(self):
        users_access_info = ''
        users = self.get_access_users()
        if users:
            for tg_user_id, access_user in users.items():
                access_for_user = str(access_user)
                access_info = []
                if int(access_for_user[0]):
                    access_info.append('чтение')
                if int(access_for_user[1]):
                    access_info.append('запись')
                access_str = ', '.join(access_info)
                user_info = await get_user_info(tg_user_id)
                users_access_info = f'{user_info} - {access_str}'
        return users_access_info

    async def get_full_name(self):
        full_name = await get_folders_message_text(self.author_user_id, self.folder_id)
        return full_name

