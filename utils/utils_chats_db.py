from typing import List

from aiogram.types import DateTime

from enums.enums import GPTModel
from models.chat_model import Chat
from utils.utils_chats_writer import add_new_chat, delete_chat, update_chat, delete_all_chats
from utils.utils_data import set_chats_collection, get_chats_collection


async def util_add_new_chat(user_id, chat_title: str, chat_messages: List[dict] | str, gpt_model: GPTModel):
    result = await add_new_chat(user_id, chat_title, chat_messages, gpt_model, DateTime.now())
    if result:
        await set_chats_collection(user_id)
    return result


async def util_update_chat(user_id, chat: Chat):
    chat.date_modified = DateTime.now()
    result = await update_chat(user_id, chat)
    if result:
        await set_chats_collection(user_id)
    return result


async def util_delete_chat(user_id, chat_id):
    result = await delete_chat(user_id, chat_id)
    if result:
        await set_chats_collection(user_id)
    return result


async def util_delete_all_chats(user_id):
    result = await delete_all_chats(user_id)
    if result:
        await set_chats_collection(user_id)
    return result
