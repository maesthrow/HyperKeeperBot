from load_all import bot


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