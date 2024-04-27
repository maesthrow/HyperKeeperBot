import logging
import os

from pymongo.mongo_client import MongoClient

mongo_username = os.getenv("MONGO_ROOT_USERNAME")
mongo_password = os.getenv("MONGO_ROOT_PASSWORD")

# docker-local
# uri = f"mongodb://{mongo_username}:{mongo_password}@mongo:27017"

# amvera
uri = f"mongodb://{mongo_username}:{mongo_password}@amvera-maesthrow-run-hk-mongo-db:27017"
# mongo-express:
# https://hk-mongo-express-maesthrow.amvera.io/

# local:
# uri = "mongodb://localhost:27017"

client = MongoClient(uri)


try:
    client.admin.command('ping')
    logging.info("Pinged database. You successfully connected to MongoDB!")
except Exception as e:
    logging.error(e)

db = client["hk_storage_db"]


async def close_client():
    try:
        client.close()
    except Exception as e:
        logging.error(e)


