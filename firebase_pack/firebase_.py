import firebase_admin
from firebase_admin import credentials, firestore

# Инициализация Firebase Admin SDK
cred = credentials.Certificate("data\hyperkeeper-eaef4-firebase-adminsdk-stjg8-ba3ff2aea5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

