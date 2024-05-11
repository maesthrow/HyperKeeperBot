from typing import List

from aiogram.types import DateTime

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
            title=chat_data.get('title'),
            messages=chat_data.get('messages'),
            gpt_model=chat_data.get('gpt_model'),
            date_modified=chat_data.get('date_modified', DateTime.now())
        )
        if chat.is_valid():
            return chat

    return None


async def get_chat_from_chat_data(chat_data: dict) -> Chat | None:
    chat_id = chat_data.get('id')
    if chat_id:
        chat = Chat(
            id=chat_id,
            title=chat_data.get('title'),
            messages=chat_data.get('messages'),
            gpt_model=chat_data.get('gpt_model'),
            date_modified=chat_data.get('date_modified', DateTime.now())
        )
        if chat.is_valid():
            return chat

    return None


async def get_simple_chats(user_id) -> List[SimpleChat]:
    chats: dict = await get_chats_collection(user_id)
    if chats:
        return [
            SimpleChat(
                id=chat_id,
                title=chats.get(chat_id).get('title'),
                date_modified=chats.get(chat_id).get('date_modified', DateTime.now()),
            ) for chat_id in chats]
    return []

