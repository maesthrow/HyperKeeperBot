from models.folder_model import Folder
from mongo_db.mongo_collection_folders import set_user_folders_data
from utils.utils_data import get_folders_collection
from utils.utils_folders_reader import get_folder


async def add_new_folder(user_id, new_folder_name, parent_folder_id):
    """Добавляет новую папку в указанную родительскую папку."""
    folders_collection = await get_folders_collection(user_id)

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
    new_folder_data = {
        "name": new_folder_name,
        "access": {
            "pin": None,
            "users": {}
        },
        "folders": {},
        "items": {}}

    # Добавляем новую папку в родительскую папку
    target_folders[new_folder_id] = new_folder_data

    # Обновляем данные пользователя
    await set_user_folders_data(user_id, {"folders": folders_collection})

    # Возвращаем новый идентификатор папки с учетом уровня вложенности
    return new_folder_id


async def delete_folder(user_id, folder_id):
    """Удаляет папку из базы данных."""
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

    # Удаляем папку из родительской папки
    #folder_to_delete = folder_ids[-1]
    if folder_id in target_folders:
        del target_folders[folder_id]

        # Обновляем данные пользователя
        await set_user_folders_data(user_id, {"folders": folders_collection})

        return True  # Успешно удалено
    else:
        return False  # Папка не найдена


async def rename_folder(user_id, folder_id, folder_new_name):
    """Переименовывает указанную папку."""
    return await set_folder_data(user_id, folder_id, 'name', folder_new_name)


async def set_pin_folder(user_id, folder_id, folder_new_pin):
    """Устанавливает новый PIN-код для указанной папку."""
    folder: Folder = await get_folder(user_id, folder_id)
    if folder:
        if folder.access:
            folder.access['pin'] = folder_new_pin
        else:
            folder.access = {'pin': folder_new_pin}
    return await edit_folder(user_id, folder)


async def edit_folder(user_id, folder: str | Folder):
    folders_collection = await get_folders_collection(user_id)

    # Разбиваем идентификатор папки на части
    folder_ids = folder.folder_id.split('/')

    # Инициализируем переменные для навигации по папкам
    target_folders = folders_collection
    folder_id_with_path = None

    # Проходим по уровням вложенности папки
    for folder_part in folder_ids[:-1]:
        folder_id_with_path = f"{folder_id_with_path}/{folder_part}" if folder_id_with_path else folder_part
        target_folder = target_folders.get(folder_id_with_path, {})
        target_folders = target_folder.get("folders", {})
    # Получаем данные о папке, которую нужно изменить
    folder_to_edit = target_folders.get(folder.folder_id, None)

    if folder_to_edit:
        # Обновляем папку
        target_folders[folder.folder_id] = folder.to_dict()
        # Обновляем данные пользователя
        await set_user_folders_data(user_id, {"folders": folders_collection})

        return True  # Успешно сохранено
    else:
        return False  # Папка не найдена


async def set_folder_data(user_id, folder_id, field_name, field_value):
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

    # Получаем данные о папке, которую нужно переименовать
    edit_folder = target_folders.get(folder_id, None)

    if edit_folder:
        # Обновляем название папки
        edit_folder[field_name] = field_value

        # Обновляем данные пользователя
        await set_user_folders_data(user_id, {"folders": folders_collection})

        return True  # Успешно сохранено
    else:
        return False  # Папка не найдена