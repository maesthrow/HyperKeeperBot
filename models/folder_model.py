from load_all import bot


class Folder:
    def __init__(
            self,
            folder_id: str,
            name: str,
            access: {} = None,
            folders: {} = None,
            items: {} = None
    ):
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

    def get_access_users(self) -> dict:
        return self.access.get('users', {})

    async def get_users_info(self):
        users_info = ''
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
                chat = await bot.get_chat(chat_id=tg_user_id)
                user_info = []
                if chat.username:
                    user_info.append(f'@{chat.username}')
                user_info.append(chat.full_name)
                # if chat.first_name:
                #     user_info.append(chat.first_name)
                # if chat.last_name:
                #     user_info.append(chat.last_name)
                users_info = f'{' '.join(user_info)} - {access_str}'
        return users_info
