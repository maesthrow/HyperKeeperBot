from firebase import get_user_data, set_user_data
from firebase_folder_reader import get_folder_data
from firebase_item_reader import get_folder_id
from models import Item


async def add_item_to_folder(tg_user_id, folder_id, item: Item):
    """Добавляет элемент (item) в указанную папку."""
    # Получаем данные о пользователе
    user_data = await get_user_data(tg_user_id)

    # Получаем коллекцию папок пользователя
    folders_collection = user_data.get("folders", {})

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

        max_child_number = max([int(child_item_id.split('/')[-1]) for child_item_id in target_folder["items"].keys()] + [0])
        # Добавляем элемент в папку
        target_folder["items"][f"{folder_id}/{max_child_number + 1}"] = item_dict

        # Обновляем данные пользователя
        await set_user_data(tg_user_id, {"folders": folders_collection})

        return True  # Успешно добавлено
    else:
        return False  # Папка не найдена


async def delete_item(tg_user_id, item_id):
    user_data = await get_user_data(tg_user_id)
    # Получаем коллекцию папок пользователя
    folders_collection = user_data.get("folders", {})

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
        await set_user_data(tg_user_id, {"folders": folders_collection})

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена


async def delete_all_items_in_folder(tg_user_id, folder_id):
    user_data = await get_user_data(tg_user_id)
    # Получаем коллекцию папок пользователя
    folders_collection = user_data.get("folders", {})

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
        await set_user_data(tg_user_id, {"folders": folders_collection})

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена


async def edit_item(tg_user_id, item_id, item: Item):
    user_data = await get_user_data(tg_user_id)
    # Получаем коллекцию папок пользователя
    folders_collection = user_data.get("folders", {})

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
        await set_user_data(tg_user_id, {"folders": folders_collection})

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена

