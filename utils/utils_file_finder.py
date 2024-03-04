from aiogram.enums import ContentType

from models.item_model import Item
from utils.utils_items_reader import get_item


class FileFinder:
    @staticmethod
    async def get_file_id_in_item(user_id, item_id, file_type: ContentType, short_file_id):
        item: Item = await get_item(user_id, item_id)
        file_id = await get_file_id_by_short_file_id(item, file_type, short_file_id)
        return file_id

    @staticmethod
    async def get_file_info_in_item_by_short_file_id(user_id, item_id, file_type: ContentType, short_file_id):
        item: Item = await get_item(user_id, item_id)
        file_info = await get_file_info_by_short_file_id(item, file_type, short_file_id)
        return file_info

    @staticmethod
    async def get_file_info_in_item_by_file_id(user_id, item_id, file_type: ContentType, file_id):
        item: Item = await get_item(user_id, item_id)
        file_info = await get_file_info_by_file_id(item, file_type, file_id)
        return file_info

    @staticmethod
    def get_file_id(file_info: dict):
        file_id = file_info['file_id']
        file_id = file_info['fields']['file_id'] if not file_id and 'file_id' in file_info['fields'] else file_id
        return file_id


async def get_file_id_by_short_file_id(item: Item, file_type: ContentType, short_file_id):
    if not item.media:
        return None
    return next((file_id for file_info in item.media[file_type] if
                 (file_id := FileFinder.get_file_id(file_info)) and file_id[16:24] == short_file_id), None)


async def get_file_info_by_short_file_id(item: Item, file_type: ContentType, short_file_id):
    if not item.media:
        return None
    return next((file_info for file_info in item.media[file_type] if
                 (file_id := FileFinder.get_file_id(file_info)) and file_id[16:24] == short_file_id), None)


async def get_file_info_by_file_id(item: Item, file_type: ContentType, search_file_id):
    if not item.media:
        return None
    return next((file_info for file_info in item.media[file_type] if
                 (file_id := FileFinder.get_file_id(file_info)) and file_id == search_file_id), None)




