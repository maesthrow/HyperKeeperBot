import firebase_admin
from firebase_admin import credentials, firestore

# Инициализация Firebase Admin SDK
cred = credentials.Certificate("data/hyperkeeper-eaef4-firebase-adminsdk-stjg8-ba3ff2aea5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

ROOT_FOLDER_ID = "0"


async def add_user(tg_user):
    """Добавляет пользователя в базу данных, если его не существует."""
    user_ref = db.collection("users").document(str(tg_user.id))
    if not user_ref.get().exists:
        user_data = {"first_name": tg_user.first_name,
                     "last_name": tg_user.last_name,
                     "username": tg_user.username,
                     "subscription_code": 0,
                     "is_paid": False,
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
        user_ref.set(user_data)


async def get_user_data(tg_user_id):
    """Возвращает данные пользователя по его идентификатору."""
    return db.collection("users").document(str(tg_user_id)).get().to_dict()


async def set_user_data(tg_user_id, data):
    """Обновляет данные пользователя."""
    db.collection("users").document(str(tg_user_id)).update(data)



