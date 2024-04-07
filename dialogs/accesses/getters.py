from aiogram_dialog import DialogManager

from models.access_folder_model import AccessFolder
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

    # folder_id = await get_current_folder_id(user_id)
    # folder: Folder = await get_folder(user_id, folder_id)
    # switch_inline_query = f'access_{user_id}_{folder_id}'
    # users_access_info_str, users_access_info_entities = await get_access_users_info(folder)
    # users_access_info = users_access_info_str or 'Ничего не найдено.'
    # # users_access_info = escape_markdown(users_access_info)
    # message_text = f'🔐 <b>Управление доступом к папке</b>' \
    #                f'\n\n{smile_folder} {folder.name}' \
    #                f'\n\n<i>Пользователи, которым вы предоставили доступ:</i>' \
    #                f'\n\n{users_access_info}'
    #
    # users_data = []
    # if users_access_info_entities:
    #     for i in range(1):
    #         for user_data in users_access_info_entities:
    #             access_icon = '✏️' if user_data['access_type'] == AccessType.WRITE.value else '👁️'
    #             users_data.append(
    #                 {
    #                     "user_id": user_data['user_id'],
    #                     "number": user_data['number'],
    #                     "name": f"👤 {user_data['number']}. {user_data['user_name']} {access_icon}",
    #                     "access_type": user_data['access_type'],
    #                     # "name": f"👤 {i + 1}. {user_data['user_name']} {access_icon}"
    #                 }
    #             )
    #
    # data['users'] = users_data
    # data['folder_id'] = folder_id
    # data['folder_name'] = folder.name
    # data['folder_has_access_users'] = len(users_data) > 0
    # data['switch_inline_query'] = switch_inline_query
    # data['message_text'] = message_text
    # dialog_manager.current_context().dialog_data = data
    data['message_text'] = '🔐 <b>Доступы от других пользователей</b>' # 🔐
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
    print(f'from_user {from_user}')
    user_folders = await get_access_folders(user_id, from_user.get('from_user_id', None))
    user_folders = [await folder.to_dict_with_folder_name_and_smile_folder() for folder in user_folders]
    user_name = await get_user_info(from_user.get('from_user_id', None))

    message_text = (f'🔐 <b>Доступы от других пользователей</b>'
                    f'\n\n👤 {user_name}')

    data['user'] = from_user
    data['user_folders'] = user_folders
    data['message_text'] = message_text
    dialog_manager.current_context().dialog_data = data
    return data


async def get_from_user_folder_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    data = {}
    dialog_data = dialog_manager.current_context().dialog_data
    access_folder_dict = dialog_data.get('access_folder_dict', None)
    print(f'access_folder_dict {access_folder_dict}')
    if access_folder_dict:
        from_user_id = access_folder_dict['from_user_id']
        folder_id = access_folder_dict['folder_id']
    else:
        folder_dict = dialog_data.get('folder_dict', None)
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
    print(f'folder_items {folder_items}')
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
    dialog_manager.current_context().dialog_data = data
    return data



