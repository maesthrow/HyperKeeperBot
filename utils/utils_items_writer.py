from load_all import RAG_ON
from models.item_model import Item
from mongo_db.mongo_collection_folders import set_user_folders_data
if RAG_ON:
    from rag.crud import add_or_update_item_embeddings, remove_user_item_embeddings
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
        print(f'item_dict = {item_dict}')
        if not item_dict:
            return None

        max_child_number = max(
            [int(child_item_id.split('/')[-1]) for child_item_id in target_folder["items"].keys()] + [0])
        new_item_id = f"{folder_id}/{max_child_number + 1}"
        # Добавляем элемент в папку
        target_folder["items"][new_item_id] = item_dict

        # Обновляем данные пользователя
        result = await set_user_folders_data(user_id, {"folders": folders_collection})
        if RAG_ON and result:
            add_or_update_item_embeddings(
                user_id=int(user_id),
                item_id=new_item_id,
                title=item.title,
                text='\n'.join(item.text)
            )
        return new_item_id  # Успешно добавлена запись
    return None  # Не удалось добавить запись


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

        if RAG_ON:
            remove_user_item_embeddings(user_id=int(user_id), item_id=item_id)

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
        for item in target_folder["items"]:
            if RAG_ON:
                remove_user_item_embeddings(user_id=int(user_id), item_id=item["id"])
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

        if RAG_ON:
            add_or_update_item_embeddings(
                user_id=int(user_id),
                item_id=item.id,
                title=item.title,
                text='\n'.join(item.text)
            )

        return True  # Успешно переименовано
    else:
        return False  # Папка не найдена


async def move_item(user_id, item_id, dest_folder_id):
    item: Item = await get_item(user_id, item_id)

    result_del = await delete_item(user_id, item_id)
    if result_del:
        if RAG_ON:
            remove_user_item_embeddings(user_id, item_id)
        await set_folders_collection(user_id)
        new_movement_item_id = await add_item_to_folder(user_id, dest_folder_id, item)

        if RAG_ON:
            add_or_update_item_embeddings(
                user_id=int(user_id),
                item_id=new_movement_item_id,
                title=item.title,
                text='\n'.join(item.text)
            )

        return new_movement_item_id

    return None
