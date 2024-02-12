import logging

from pymongo.mongo_client import MongoClient


uri = "mongodb://localhost:27017"
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


