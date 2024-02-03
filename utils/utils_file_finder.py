from aiogram.enums import ContentType

from models.item_model import Item
from utils.utils_items_reader import get_item


class FileFinder():
    @staticmethod
    async def get_file_id_in_item(user_id, item_id, file_type: ContentType, short_file_id):
        item: Item = await get_item(user_id, item_id)
        file_id = await get_file_id(item, file_type, short_file_id)
        return file_id


async def get_file_id(item: Item, file_type: ContentType, short_file_id):
    media = item.media
    if not media:
        return None

    for file_id in media[file_type]:
        if file_id[16:24] == short_file_id:
            return file_id

    return None