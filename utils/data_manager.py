from aiogram.fsm.storage.base import StorageKey

from load_all import bot, dp


async def get_data(user_id):
    storage_key = StorageKey(bot.id, user_id, user_id)
    data = await dp.storage.get_data(storage_key)
    return data


async def set_data(user_id, data):
    storage_key = StorageKey(bot.id, user_id, user_id)
    await dp.storage.update_data(storage_key, data)

