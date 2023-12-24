from firebase import db, get_user_data, set_user_data
from firebase_folder_reader import get_folder_name


async def add_new_folder(tg_user_id, new_folder_name, parent_folder_id):
    """Добавляет новую папку в указанную родительскую папку."""
    # Получаем данные о пользователе
    user_data = await get_user_data(tg_user_id)

    # Получаем коллекцию папок пользователя
    folders_collection = user_data.get("folders", {})

    # Разбиваем идентификатор родительской папки на части
    parent_folder_ids = parent_folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности родительской папки
    for parent_id in parent_folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{parent_id}" if folder_id_with_path else parent_id
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Находим максимальный номер среди дочерних папок текущей родительской папки
    max_child_number = max([int(child_id.split('-')[-1]) for child_id in target_folders.keys()] + [0])

    # Генерируем новый идентификатор для новой папки, учитывая текущий уровень вложенности
    new_folder_id = f"{parent_folder_id}/{str(int(parent_folder_ids[-1].split('-')[0]) + 1)}-{max_child_number + 1}"

    # Создаем данные для новой папки
    new_folder_data = {"name": new_folder_name, "folders": {}, "items": {}}

    # Добавляем новую папку в родительскую папку
    target_folders[new_folder_id] = new_folder_data

    # Обновляем данные пользователя
    await set_user_data(tg_user_id, {"folders": folders_collection})

    # Возвращаем новый идентификатор папки с учетом уровня вложенности
    return new_folder_id


async def delete_folder(tg_user_id, folder_id):
    """Удаляет папку из базы данных."""
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

    # Удаляем папку из родительской папки
    folder_to_delete = folder_ids[-1]
    if folder_id in target_folders:
        del target_folders[folder_id]

        # Обновляем данные пользователя
        await set_user_data(tg_user_id, {"folders": folders_collection})

        return True  # Успешно удалено
    else:
        return False  # Папка не найдена


async def set_current_folder(tg_user_id, folder_id):
    """Устанавливает новый идентификатор текущей папки для пользователя."""
    await set_user_data(tg_user_id, {"current_folder": folder_id})


async def rename_folder(tg_user_id, folder_id, folder_new_name):
    """Переименовывает указанную папку."""
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

    # Получаем данные о папке, которую нужно переименовать
    folder_to_rename = target_folders.get(folder_id, None)

    if folder_to_rename:
        # Обновляем название папки
        folder_to_rename["name"] = folder_new_name

        # Обновляем данные пользователя
        await set_user_data(tg_user_id, {"folders": folders_collection})

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена


async def get_sub_folder_names(tg_user_id, folder_id):
    """Возвращает список всех folder_id внутри указанной папки."""
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
    for folder_part in folder_ids:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})

    # Получаем все folder_id внутри указанной папки
    sub_folder_ids = list(target_folders.keys())
    sub_folder_names = [await get_folder_name(tg_user_id, sub_folder_id) for sub_folder_id in sub_folder_ids]

    # Выводим названия подпапок на печать
    print("Названия подпапок:", sub_folder_names)

    return sub_folder_names
