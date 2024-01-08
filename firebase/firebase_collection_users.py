from firebase.firebase_ import db


async def add_user(tg_user):
    """Добавляет пользователя в базу данных, если его не существует."""
    user_ref = db.collection("users").document(str(tg_user.id))
    if not user_ref.get().exists:
        user_data = {
            "first_name": tg_user.first_name,
            "last_name": tg_user.last_name,
            "username": tg_user.username,
            "subscription": {
                "subscription_code": 0,
                "is_paid": False,
            },
            "settings": {
                "folders_on_page_count": 4,
                "items_on_page_count": 4,
                "language": "russian"
            },

        }
        user_ref.set(user_data)


async def get_user_data(tg_user_id):
    """Возвращает данные пользователя по его идентификатору."""
    return db.collection("users").document(str(tg_user_id)).get().to_dict()


async def set_user_data(tg_user_id, data):
    """Обновляет данные пользователя."""
    db.collection("users").document(str(tg_user_id)).update(data)


async def get_user_collection(tg_user_id, collection_name: str):
    """Возвращает папки пользователя по идентификатору."""
    user_data = await get_user_data(tg_user_id)
    subscription_collection = user_data.get(collection_name, {})
    return subscription_collection

