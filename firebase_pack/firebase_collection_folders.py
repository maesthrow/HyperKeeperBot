from firebase_pack.firebase_ import db

ROOT_FOLDER_ID = "0"


async def add_user_folders(tg_user):
    """Добавляет пользователя в базу данных, если его не существует."""
    user_folders_ref = db.collection("folders").document(str(tg_user.id))
    if not user_folders_ref.get().exists:
        user_data = {
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
            },
        }
        user_folders_ref.set(user_data)


async def get_user_folders_data(tg_user_id):
    """Возвращает данные пользователя по его идентификатору."""
    return db.collection("folders").document(str(tg_user_id)).get().to_dict()


async def set_user_folders_data(tg_user_id, data):
    """Обновляет данные пользователя."""
    db.collection("folders").document(str(tg_user_id)).update(data)


async def get_user_folders_collection(tg_user_id):
    """Возвращает папки пользователя по идентификатору."""
    folders_data = await get_user_folders_data(tg_user_id)
    folders_collection = folders_data.get("folders", {})
    return folders_collection
