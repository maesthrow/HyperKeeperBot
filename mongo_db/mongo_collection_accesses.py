from aiogram.types import User

from mongo_db.mongo import db
from utils.utils_user import get_user_full_str


async def add_user_accesses(tg_user: User):
    """Добавляет коллекцию доступов accesses для пользователя в базу данных, если ее не существует."""
    user_accesses_collection = db["accesses"]
    user_accesses_document = user_accesses_collection.find_one({"_id": tg_user.id})
    if not user_accesses_document:
        # Создаем структуру коллекции доступов accesses для пользователя
        user_data = {
            "_id": tg_user.id,
            "accesses": {}
        }
        user_full_str = get_user_full_str(tg_user)
        try:
            print(f"Создание коллекции доступов (accesses) для пользователя "
                  f"{user_full_str} в базу данных:")
            user_accesses_collection.insert_one(user_data)
            print("Успешно")
        except Exception as e:
            print(f"Ошибка при создании коллекции доступов для пользователя "
                  f"{user_full_str} в базу данных:", e)
