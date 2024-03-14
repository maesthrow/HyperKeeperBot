from aiogram.types import User


def get_user_full_str(tg_user: User):
    result = str(tg_user.id)
    if tg_user.username:
        result = f'{result} {tg_user.username}'
    result = f'{result} {tg_user.full_name}'
    return result
