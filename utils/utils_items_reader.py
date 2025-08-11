from models.item_model import Item
from utils.utils_folders_reader import get_folder_data


def get_last_number(key):
    return int(key.split('/')[-1])


def get_folder_id(item_id):
    # Разделение строки по '/' справа налево и взятие первой части
    return item_id.rsplit('/', 1)[0] if item_id else None


async def get_folder_items(user_id, folder_id, text_search=None):
    """Возвращает элементы папки по её идентификатору с учетом текстового поиска."""
    folder_data = await get_folder_data(user_id, folder_id)
    items = folder_data.get("items", {}) if folder_data else {}
    if text_search:
        # Фильтрация элементов по текстовому поиску в title или text
        filtered_items = {key: value for key, value in items.items()
                          if (text_search.lower() in str(value.get("title", "")).lower()) or
                          (text_search.lower() in " ".join(value.get("text", [])).lower())}
    else:
        filtered_items = items

    # Сортировка по title или text
    sorted_items = dict(sorted(filtered_items.items(),
                               key=lambda x: x[1]["title"] if x[1]["title"] is not None else x[1]["text"][0]))

    return sorted_items


async def get_item_dict(user_id, item_id):
    folder_id = get_folder_id(item_id)
    """Возвращает словарь элемента в папке."""
    items = await get_folder_items(user_id, folder_id)
    # Ищем элемент с заданным item_id
    if item_id in items:
        item = items.get(item_id, {})
        # Если элемент найден, возвращаем весь словарь item
        return item

    return None


async def get_item(user_id, item_id) -> Item | None:
    item_dict = await get_item_dict(user_id, item_id)
    if "media" in item_dict:
        media = item_dict["media"]
    else:
        media = None
    if item_dict:
        item = Item(id=item_id, text=item_dict["text"], title=item_dict["title"],
                    media=media, date_created=item_dict["date_created"])
        return item

    return None


async def get_simple_item(user_id, item_id):
    print(f'get_simple_item -> item_id={item_id}')
    item_dict = await get_item_dict(user_id, item_id)
    if item_dict:
        item = Item(id=item_id, text=item_dict["text"], title=item_dict["title"], date_created=item_dict["date_created"])
        return item

    return None


async def get_item_property(user_id, item_id, key):
    item_dict = await get_item_dict(user_id, item_id)
    if item_dict:
        # Если элемент найден, возвращаем значение ключа
        return item_dict.get(key, None)
        # return folder_data.get(item_id, {}).get(key, None)

    # Если элемент не найден, возвращаем None
    return None