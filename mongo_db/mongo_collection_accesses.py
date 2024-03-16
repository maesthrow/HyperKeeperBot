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


async def get_user_accesses_data(tg_user_id):
    """Возвращает данные доступов пользователя по его идентификатору."""
    user_accesses_collection = db["accesses"]
    user_accesses_document = user_accesses_collection.find_one({"_id": tg_user_id})
    return user_accesses_document


async def set_user_accesses_data(tg_user_id, data):
    """Обновляет данные доступов пользователя."""
    user_accesses_collection = db["accesses"]
    user_accesses_collection.update_one({"_id": tg_user_id}, {"$set": data})


async def get_user_accesses_collection(tg_user_id):
    user_accesses_document = await get_user_accesses_data(tg_user_id)
    if user_accesses_document:
        return user_accesses_document.get("accesses", {})
    return {}


async def set_user_accesses_collection(tg_user_id, collection):
    """Обновляет коллекцию пользователя по наименованию."""
    user_accesses_data = await get_user_accesses_data(tg_user_id)
    user_accesses_data["accesses"] = collection
    await set_user_accesses_data(tg_user_id, user_accesses_data)


async def get_user_accesses_from_user_collection(tg_user_id, from_user_id):
    """Возвращает доступы пользователя от другого пользователя по идентификатору."""
    user_accesses_collection = await get_user_accesses_collection(tg_user_id)
    if user_accesses_collection:
        return user_accesses_collection.get(from_user_id, {})
    return {}


async def set_user_accesses_from_user_collection(tg_user_id, from_user_id, collection):
    """Обновляет доступы пользователя от другого пользователя по идентификатору."""
    user_accesses_collection = await get_user_accesses_collection(tg_user_id)
    user_accesses_collection[from_user_id] = collection
    await set_user_accesses_collection(tg_user_id, user_accesses_collection)
