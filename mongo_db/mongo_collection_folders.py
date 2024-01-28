from mongo_db.mongo import db


ROOT_FOLDER_ID = "0"


async def add_user_folders(tg_user):
    """Добавляет пользователя в базу данных, если его не существует."""
    user_folders_collection = db["folders"]  # Получаем коллекцию "folders" из базы данных

    # Проверяем, существует ли пользователь в коллекции
    user_document = user_folders_collection.find_one({"_id": tg_user.id})

    if not user_document:
        # Создаем структуру данных для нового пользователя
        user_data = {
            "_id": tg_user.id,
            "folders": {
                "0": {
                    "name": "Хранилище",
                    "folders": {
                        "0/1-1": {
                            "name": "Заметки 📒",
                            "folders": {},
                            "items": {}
                        },
                        "0/1-2": {
                            "name": "Полезные ссылки 🔗",
                            "folders": {},
                            "items": {}
                        },
                    },
                    "items": {}
                }
            }
        }
        try:
            print("Запись хранилища в базу данных:")
            user_folders_collection.insert_one(user_data)
            print("Успешно")
        except Exception as e:
            print("Ошибка при добавлении хранилища пользователя в базу данных:", e)



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
