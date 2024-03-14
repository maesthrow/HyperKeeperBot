from aiogram.types import User

from mongo_db.mongo import db
from utils.utils_user import get_user_full_str

ROOT_FOLDER_ID = "0"


async def add_user_folders(tg_user: User):
    """Добавляет коллекцию папок folders пользователя в базу данных, если ее не существует."""
    user_folders_collection = db["folders"]  # Получаем коллекцию "folders" из базы данных

    # Проверяем, существует ли коллекция folders для данного пользователя в базе данных
    user_folders_document = user_folders_collection.find_one({"_id": tg_user.id})

    if not user_folders_document:
        # Создаем структуру коллекции папок folders для пользователя
        user_data = {
            "_id": tg_user.id,
            "folders": {
                "0": {
                    "name": "Хранилище",
                    "folders": {
                        "0/1-1": {
                            "name": "Заметки 📒",
                            "access": {
                                "pin": None,
                                "users": {}
                            },
                            "folders": {},
                            "items": {}
                        },
                        "0/1-2": {
                            "name": "Полезные ссылки 🔗",
                            "access": {
                                "pin": None,
                                "users": {}
                            },
                            "folders": {},
                            "items": {}
                        },
                    },
                    "items": {}
                }
            }
        }
        user_full_str = get_user_full_str(tg_user)
        try:
            print(f"Создание хранилища (folders) для пользователя {user_full_str} в базе данных:")
            user_folders_collection.insert_one(user_data)
            print("Успешно")
        except Exception as e:
            print(f"Ошибка при создании хранилища для пользователя {user_full_str} в базе данных:", e)


async def get_user_folders_data(tg_user_id):
    """Возвращает данные пользователя по его идентификатору."""
    user_folders_collection = db["folders"]
    user_document = user_folders_collection.find_one({"_id": tg_user_id})
    return user_document


async def set_user_folders_data(tg_user_id, data):
    """Обновляет данные пользователя."""
    user_folders_collection = db["folders"]
    try:
        user_folders_collection.update_one({"_id": tg_user_id}, {"$set": data}, upsert=True)
    except Exception as e:
        print(f"Ошибка записи в бд -> set_user_folders_data:\n{e}")


async def get_user_folders_collection(tg_user_id):
    """Возвращает папки пользователя по идентификатору."""
    user_document = await get_user_folders_data(tg_user_id)
    if user_document:
        return user_document.get("folders", {})
    return {}
