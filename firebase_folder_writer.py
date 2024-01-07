from aiogram.types import User, Chat

from firebase import get_user_data, set_user_data
from firebase_folder_reader import get_user_folders_collection
from load_all import dp


async def get_folders_collection():
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    folders_collection = data.get('folders_collection', None)

    if not folders_collection:
        folders_collection = await get_user_folders_collection(tg_user.id)
        await set_folders_collection(folders_collection)

    return folders_collection


async def set_folders_collection(folders_collection=None):
    tg_user = User.get_current()
    chat = Chat.get_current()
    if not folders_collection:
        folders_collection = await get_user_folders_collection(tg_user.id)

    data = await dp.storage.get_data(chat=chat, user=tg_user)
    data['dict_search_data'] = None
    data['folders_collection'] = folders_collection

    await dp.storage.update_data(user=tg_user, chat=chat, data=data)


async def add_new_folder(tg_user_id, new_folder_name, parent_folder_id):
    """Добавляет новую папку в указанную родительскую папку."""
    folders_collection = await get_folders_collection()

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
    folders_collection = await get_folders_collection()

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
    folders_collection = await get_folders_collection()

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
