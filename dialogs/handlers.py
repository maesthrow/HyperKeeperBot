from aiogram.types import Message

from load_all import bot


async def try_delete_message(delete_message: Message):
    if delete_message:
        try:
            await bot.delete_message(delete_message.chat.id, delete_message.message_id)
        except:
            pass