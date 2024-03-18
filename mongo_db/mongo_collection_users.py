from aiogram.types import User

from mongo_db.mongo import db
from utils.utils_user import get_user_full_str


async def add_user(tg_user: User):
    """Добавляет пользователя в базу данных, если его не существует."""
    user_collection = db["users"]
    user_document = user_collection.find_one({"_id": tg_user.id})
    if not user_document:
        user_data = {
            "_id": tg_user.id,
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name,
            "username": tg_user.username,
            "subscription": {
                "subscription_code": 0,
                "is_paid": False,
            },
            "settings": {
                "folders_on_page_count": 6,
                "items_on_page_count": 4,
                "language": "russian"
            },
            "code_word": None
        }
        user_full_str = get_user_full_str(tg_user)
        try:
            print(f"Запись пользователя {user_full_str} в базу данных:")
            user_collection.insert_one(user_data)
            print("Успешно")
        except Exception as e:
            print(f"Ошибка при добавлении пользователя {user_full_str} в базу данных:", e)


async def get_user_data(tg_user_id):
    """Возвращает данные пользователя по его идентификатору."""
    user_collection = db["users"]
    user_document = user_collection.find_one({"_id": tg_user_id})
    return user_document


async def set_user_data(tg_user_id, data):
    """Обновляет данные пользователя."""
    user_collection = db["users"]
    user_collection.update_one({"_id": tg_user_id}, {"$set": data})


async def get_user_collection(tg_user_id, collection_name: str):
    """Возвращает коллекцию пользователя по наименованию."""
    user_document = await get_user_data(tg_user_id)
    if user_document:
        return user_document.get(collection_name, {})
    return {}


async def set_user_collection(tg_user_id, collection_name: str, collection):
    """Обновляет коллекцию пользователя по наименованию."""
    user_data = await get_user_data(tg_user_id)
    user_data[collection_name] = collection
    await set_user_data(tg_user_id, user_data)
