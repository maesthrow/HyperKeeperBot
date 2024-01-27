from models.item_model import Item
from mongo_db.mongo_collection_folders import set_user_folders_data
from utils.utils_data import get_folders_collection, set_folders_collection
from utils.utils_items_reader import get_folder_id, get_item


async def add_item_to_folder(user_id, folder_id, item: Item):
    """Добавляет элемент (item) в указанную папку."""
    folders_collection = await get_folders_collection(user_id)

    # Разбиваем идентификатор папки на части
    folder_ids = folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности папки
    for folder_part in folder_ids[:-1]:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Получаем данные о папке, в которую нужно добавить элемент
    target_folder = target_folders.get(folder_id, None)

    if target_folder:
        # Преобразуем объект Item в словарь перед добавлением
        item_dict = item.to_dict()

        max_child_number = max(
            [int(child_item_id.split('/')[-1]) for child_item_id in target_folder["items"].keys()] + [0])
        new_item_id = f"{folder_id}/{max_child_number + 1}"
        # Добавляем элемент в папку
        target_folder["items"][new_item_id] = item_dict

        # Обновляем данные пользователя
        await set_user_folders_data(user_id, {"folders": folders_collection})
        return new_item_id  # Успешно добавлено
    else:
        return None  # Папка не найдена


async def delete_item(user_id, item_id):
    folders_collection = await get_folders_collection(user_id)

    folder_id = get_folder_id(item_id)
    # Разбиваем идентификатор папки на части
    folder_ids = folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности папки
    for folder_part in folder_ids[:-1]:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Получаем данные о папке, в которой нужно удалить запись
    target_folder = target_folders.get(folder_id, None)
    if item_id in target_folder["items"]:
        del target_folder["items"][item_id]
        # Обновляем данные пользователя
        await set_user_folders_data(user_id, {"folders": folders_collection})

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена


async def delete_all_items_in_folder(user_id, folder_id):
    folders_collection = await get_folders_collection(user_id)

    # Разбиваем идентификатор папки на части
    folder_ids = folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности папки
    for folder_part in folder_ids[:-1]:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Получаем данные о папке, в которой нужно удалить запись
    target_folder = target_folders.get(folder_id, None)
    if target_folder:
        target_folder["items"].clear()
        # Обновляем данные пользователя
        await set_user_folders_data(user_id, {"folders": folders_collection})

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена


async def edit_item(user_id, item_id, item: Item):
    folders_collection = await get_folders_collection(user_id)

    folder_id = get_folder_id(item_id)
    # Разбиваем идентификатор папки на части
    folder_ids = folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности папки
    for folder_part in folder_ids[:-1]:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Получаем данные о папке, в которой нужно удалить запись
    target_folder = target_folders.get(folder_id, None)
    if item_id in target_folder["items"]:
        item_dict = item.to_dict()
        target_folder["items"][item_id] = item_dict
        # Обновляем данные пользователя
        await set_user_folders_data(user_id, {"folders": folders_collection})

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена


async def move_item(user_id, item_id, dest_folder_id):
    item: Item = await get_item(user_id, item_id)

    result_del = await delete_item(user_id, item_id)
    if result_del:
        await set_folders_collection(user_id)
        new_movement_item_id = await add_item_to_folder(user_id, dest_folder_id, item)
        return new_movement_item_id

    return None