from firebase_folder_reader import get_folder_data
from models import Item


# Функция для извлечения последнего числа из ключа
def get_last_number(key):
    return int(key.split('/')[-1])


def get_folder_id(item_id):
    # Разделение строки по '/' справа налево и взятие первой части
    return item_id.rsplit('/', 1)[0]


async def get_folder_items(tg_user_id, folder_id):
    """Возвращает элементы папки по её идентификатору."""
    folder_data = await get_folder_data(tg_user_id, folder_id)
    items = folder_data.get("items", [])
    sorted_items = dict(sorted(items.items(), key=lambda x: get_last_number(x[0])))
    return sorted_items


async def get_item_dict(tg_user_id, item_id):
    folder_id = get_folder_id(item_id)
    """Возвращает словарь элемента в папке."""
    items = await get_folder_items(tg_user_id, folder_id)

    # Ищем элемент с заданным item_id
    if item_id in items:
        item = items.get(item_id, {})
        # Если элемент найден, возвращаем весь словарь item
        return item

    return None


async def get_item(tg_user_id, item_id):
    item_dict = await get_item_dict(tg_user_id, item_id)
    if item_dict:
        item = Item(item_dict["text"], item_dict["title"], item_dict["date_created"])
        return item

    return None


async def get_item_property(tg_user_id, folder_id, item_id, key):
    item_dict = await get_item_dict(tg_user_id, item_id)
    if item_dict:
        # Если элемент найден, возвращаем значение ключа
        return item_dict.get(key, None)
        # return folder_data.get(item_id, {}).get(key, None)

    # Если элемент не найден, возвращаем None
    return None