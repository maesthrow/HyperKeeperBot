from aiogram.types import User

from mongo_db.mongo import db
from utils.utils_user import get_user_full_str


async def add_user_chats(tg_user: User):
    """Добавляет коллекцию папок chats пользователя в базу данных, если ее не существует."""
    user_chats_collection = db["chats"]  # Получаем коллекцию "chats" из базы данных

    # Проверяем, существует ли коллекция chats для данного пользователя в базе данных
    user_chats_document = user_chats_collection.find_one({"_id": tg_user.id})

    if not user_chats_document:
        # Создаем структуру коллекции папок chats для пользователя
        user_data = {
            "_id": tg_user.id,
            "chats": {}
        }
        user_full_str = get_user_full_str(tg_user)
        try:
            print(f"Создание коллекции чатов с GPT-моделями (chats) для пользователя {user_full_str} в базе данных:")
            user_chats_collection.insert_one(user_data)
            print("Успешно")
        except Exception as e:
            print(f"Ошибка при создании коллекции чатов с GPT-моделями (chats) "
                  f"для пользователя {user_full_str} в базе данных:", e)


async def get_user_chats_data(tg_user_id):
    """Возвращает данные пользователя по его идентификатору."""
    user_chats_collection = db["chats"]
    user_document = user_chats_collection.find_one({"_id": tg_user_id})
    return user_document


async def set_user_chats_data(tg_user_id, data) -> bool:
    """Обновляет данные пользователя."""
    tg_user_id = int(tg_user_id)
    user_chats_collection = db["chats"]
    try:
        user_chats_collection.update_one({"_id": tg_user_id}, {"$set": data}, upsert=True)
        return True
    except Exception as e:
        print(f"Ошибка записи в бд -> set_user_chats_data:\n{e}")
        return False


async def get_user_chats_collection(tg_user_id):
    """Возвращает чаты пользователя по идентификатору."""
    user_document = await get_user_chats_data(tg_user_id)
    if user_document:
        return user_document.get("chats", {})
    return {}
