from typing import List

from enums.enums import GPTModel
from models.chat_model import Chat
from mongo_db.mongo_collection_chats import set_user_chats_data
from utils.utils_data import get_chats_collection


async def add_new_chat(user_id, chat_title: str, chat_messages: List[dict] | str, gpt_model: GPTModel):
    """Добавляет новый чат в коллекцию пользователя папку."""
    chats_collection = await get_chats_collection(user_id)

    # Находим максимальный номер среди id чатов пользователя
    if chats_collection:
        max_chat_id_number = max([int(chat_id) for chat_id in chats_collection.keys()])
    else:
        max_chat_id_number = 0
    # Генерируем новый идентификатор для нового чата
    new_chat_id = f"{max_chat_id_number + 1}"

    new_chat = Chat(new_chat_id, title=chat_title, messages=chat_messages, gpt_model=gpt_model)
    new_chat_data = new_chat.to_dict()

    chats_collection[new_chat_id] = new_chat_data

    # Обновляем данные пользователя
    await set_user_chats_data(user_id, {"chats": chats_collection})

    return new_chat_id


async def update_chat(user_id, chat: Chat):
    """Обновляет чат в базе данных."""
    chats_collection = await get_chats_collection(user_id)
    if chat.id in chats_collection:
        chats_collection[chat.id] = chat.to_dict()
        await set_user_chats_data(user_id, {"chats": chats_collection})
        return True
    return False


async def delete_chat(user_id, chat_id):
    """Удаляет чат из базы данных."""
    chats_collection = await get_chats_collection(user_id)
    if chat_id in chats_collection:
        del chats_collection[chat_id]
        await set_user_chats_data(user_id, {"chats": chats_collection})
        return True
    return False


