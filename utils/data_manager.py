from aiogram.fsm.storage.base import StorageKey

from load_all import bot, dp


async def get_data(user_id):
    storage_key = StorageKey(bot.id, user_id, user_id)
    data = await dp.storage.get_data(storage_key)
    return data


async def set_data(user_id, data):
    storage_key = StorageKey(bot.id, user_id, user_id)
    await dp.storage.update_data(storage_key, data)


async def set_any_message_ignore(user_id, value: bool):
    data = await get_data(user_id)
    data['any_message_ignore'] = value
    await set_data(user_id, data)
