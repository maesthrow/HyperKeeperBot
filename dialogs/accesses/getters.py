import copy

from aiogram_dialog import DialogManager

from models.item_model import Item
from utils.utils_ import get_sorted_folders, smile_folder, smile_item
from utils.utils_access import get_user_name_from_user_info, get_user_info
from utils.utils_access_folders_reader import get_access_folders
from utils.utils_data import get_accesses_collection
from utils.utils_items_reader import get_folder_items


async def get_users_menu_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    accesses_collection = await get_accesses_collection(user_id)
    users_ids = accesses_collection.keys()
    users = [await get_from_user_dict(from_user_id) for from_user_id in users_ids]
    data['users'] = users
    data['message_text'] = '🔐 <b>Доступы от других пользователей</b>' # 🔐
    data['back_data'] = dialog_manager.current_context().dialog_data
    dialog_manager.current_context().dialog_data = data
    return data


async def get_from_user_dict(from_user_id) -> dict:
    name = get_user_name_from_user_info(await get_user_info(from_user_id))
    return {
        'from_user_id': from_user_id,
        'name': f'👤 {name}'
    }


async def get_from_user_folders_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    data = {}
    dialog_data = dialog_manager.current_context().dialog_data
    from_user = dialog_data.get('user', None)
    user_folders = await get_access_folders(user_id, from_user.get('from_user_id', None))
    user_folders = [await folder.to_dict_with_folder_name_and_smile_folder() for folder in user_folders]
    user_name = await get_user_info(from_user.get('from_user_id', None))

    message_text = (f'🔐 <b>Доступы от других пользователей</b>'
                    f'\n\n👤 {user_name}')

    data['user'] = from_user
    data['user_folders'] = user_folders
    data['message_text'] = message_text
    data['back_data'] = copy.deepcopy(dialog_data)
    dialog_manager.current_context().dialog_data = data
    return data


async def get_from_user_folder_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    data = {}
    dialog_data = dialog_manager.current_context().dialog_data
    print(f'dialog_data {dialog_data}')
    access_folder_dict = dialog_data.get('access_folder_dict', None)
    if access_folder_dict:
        from_user_id = access_folder_dict['from_user_id']
        folder_id = access_folder_dict['folder_id']
    else:
        folder_dict = dialog_data.get('folder_dict', None)
        if not folder_dict:
            back_data = dialog_data.get('back_data', None)
            if back_data:
                folder_dict = back_data.get('folder_dict', None)
        from_user_id = folder_dict['from_user_id']
        folder_id = folder_dict['folder_id']

    user_sorted_folders = await get_sorted_folders(from_user_id, folder_id)
    user_folders = []
    for folder in user_sorted_folders:
        user_folders.append(
            {
                'from_user_id': from_user_id,
                'folder_id': folder[0],
                'folder_name': f'{smile_folder} {folder[1]['name']}',
            }
        )

    folder_items = await get_folder_items(from_user_id, folder_id)
    user_folder_items = []
    for folder_item_id in folder_items:
        item: Item = Item(
            folder_item_id, folder_items[folder_item_id]['text'],
            folder_items[folder_item_id]['title']
        )
        user_folder_items.append(
            {
                'from_user_id': from_user_id,
                'item_id': item.id,
                'item_title': f'{smile_item} {item.get_inline_title()}',
            }
        )

    message_text = f'🔐 <b>Доступы от других пользователей</b>'
                     #f'\n\n👤 {user_name}')
    #
    from_user = dialog_data.get('user', None)
    data['user'] = from_user
    data['user_folders'] = user_folders
    data['user_folder_items'] = user_folder_items
    data['message_text'] = message_text
    data['back_data'] = copy.deepcopy(dialog_data)
    dialog_manager.current_context().dialog_data = data
    return data



