from typing import List

from models.chat_model import Chat, SimpleChat
from utils.utils_data import get_chats_collection


async def get_chat_data(user_id, chat_id):
    chats_collection = await get_chats_collection(user_id)
    chat_data = chats_collection.get(chat_id, {})
    return chat_data


async def get_chat(user_id, chat_id: str) -> Chat | None:
    try:
        user_id = int(user_id)
    except:
        return None
    chat_data = await get_chat_data(user_id, chat_id)

    if chat_data:
        chat = Chat(
            id=chat_id,
            title=chat_data['title'],
            text=chat_data['text'],
            gpt_model=chat_data['gpt_model']
        )
        return chat

    return None


async def get_simple_chats(user_id) -> List[SimpleChat]:
    chats: dict = await get_chats_collection(user_id)
    if chats:
        return [SimpleChat(id=chat_id, title=chats.get(chat_id).get('title')) for chat_id in chats]
    return []

