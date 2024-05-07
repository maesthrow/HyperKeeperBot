from aiogram_dialog import DialogManager

from dialogs import general_keyboards
from enums.enums import AccessType
from models.folder_model import Folder
from models.item_model import INVISIBLE_CHAR
from utils.utils_ import smile_folder, smile_item
from utils.utils_access import get_access_users_info, get_user_info, get_access_str_by_type
from utils.utils_data import get_current_folder_id, get_current_lang
from utils.utils_folders import get_folder_statistic
from utils.utils_folders_reader import get_folder_name, get_folder
from utils.utils_handlers import get_folders_message_text
from utils.utils_items_reader import get_folder_items
from utils.utils_parse_mode_converter import escape_markdown


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    message_text = await get_folders_message_text(user_id, folder_id)
    # message_text = escape_markdown(folders_message_text)
    data = {
        'folder_id': folder_id,
        'message_text': f'🛠 <b>Меню управления папкой</b>\n\n{message_text}'
    }
    return data


async def get_message_text(dialog_manager: DialogManager, **kwargs):
    return {"message_text": dialog_manager.current_context().dialog_data.get("message_text", None)}


async def get_start_data_message_text(dialog_manager: DialogManager, **kwargs):
    return {"message_text": dialog_manager.current_context().start_data.get("message_text", None)}


async def get_statistic_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    dict_folder_statistic = await get_folder_statistic(user_id, folder_id)
    folders_count = dict_folder_statistic['folders_count']
    items_count = dict_folder_statistic['items_count']
    deep_folders_count = dict_folder_statistic['deep_folders_count']
    deep_items_count = dict_folder_statistic['deep_items_count']

    statistic_text = (f"<i>Количество папок:</i> <b><i>{folders_count}</i></b> {smile_folder}\n"
                      f"<i>Количество записей:</i> <b><i>{items_count}</i></b> {smile_item}\n\n"
                      f"<u>С учетом вложенных папок:</u>\n"
                      f"<i>Всего папок:</i> <b><i>{deep_folders_count}</i></b> {smile_folder}\n"
                      f"<i>Всего записей:</i> <b><i>{deep_items_count}</i></b> {smile_item}")

    folder_statistic_text = f"📊 <b>Статистика папки</b>{INVISIBLE_CHAR * 20}\n\n" \
                            f"{smile_folder} {folder_name}:\n\n" \
                            f"{statistic_text}"

    data['folder_statistic_text'] = folder_statistic_text
    return data


async def get_delete_all_items_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    items_count = len(await get_folder_items(user_id, folder_id))
    if items_count:
        message_text = f"Действительно хотите удалить все записи ({items_count}) в папке " \
                       f"{smile_folder} {folder_name} ?"
    else:
        message_text = "В этой папке нет записей 🤷‍♂️"
    data['folder_id'] = folder_id
    data['items_count'] = items_count
    data['message_text'] = message_text
    return data


async def get_rename_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    folder_name = escape_markdown(folder_name)
    message_text = f"*Переименовать папку* {smile_folder}" \
                   f"\n\nМожете скопировать текущее название:" \
                   f"\n'`{folder_name}`'" \
                   f"\n\n_*Напишите новое название папки:*_"
    data = {
        'user_id': user_id,
        'folder_id': folder_id,
        'message_text': message_text,
        'btn_cancel': general_keyboards.BUTTONS['cancel'].get(language)}
    return data


async def get_delete_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    message_text = f"Хотите удалить папку <b>{smile_folder} {folder_name}</b>\nи все ее содержимое?"
    data['message_text'] = message_text
    return data


async def get_access_menu_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder: Folder = await get_folder(user_id, folder_id)
    switch_inline_query = f'access_{user_id}_{folder_id}'
    users_access_info_str, users_access_info_entities = await get_access_users_info(folder)
    users_access_info = users_access_info_str or 'Ничего не найдено.'
    # users_access_info = escape_markdown(users_access_info)
    message_text = f'🔐 <b>Управление доступом к папке</b>' \
                   f'\n\n{smile_folder} {folder.name}' \
                   f'\n\n<i>Пользователи, которым вы предоставили доступ:</i>' \
                   f'\n\n{users_access_info}'

    users_data = []
    if users_access_info_entities:
        for i in range(1):
            for user_data in users_access_info_entities:
                access_icon = '✏️' if user_data['access_type'] == AccessType.WRITE.value else '👁️'
                users_data.append(
                    {
                        "user_id": user_data['user_id'],
                        "number": user_data['number'],
                        "name": f"👤 {user_data['number']}. {user_data['user_name']} {access_icon}",
                        "access_type": user_data['access_type'],
                        # "name": f"👤 {i + 1}. {user_data['user_name']} {access_icon}"
                    }
                )

    data['users'] = users_data
    data['folder_id'] = folder_id
    data['folder_name'] = folder.name
    data['folder_has_access_users'] = len(users_data) > 0
    data['switch_inline_query'] = switch_inline_query
    data['message_text'] = message_text
    dialog_manager.current_context().dialog_data = data
    return data


async def get_user_selected_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    dialog_data = dialog_manager.current_context().dialog_data
    user = dialog_data.get('user', None)
    user_name = await get_user_info(user.get('user_id', None))
    folder_name = dialog_data.get('folder_name', '')

    dialog_manager.current_context().dialog_data = dialog_data

    access_srt = get_access_str_by_type(AccessType(user.get('access_type', '')))
    message_text = f'👤 {user_name}' \
                   f'\n\nИмеет доступ {access_srt} папки:' \
                   f'\n\n{smile_folder} {folder_name}'
    # f'\n\n<i>Выберите действие:</i>')

    data['user'] = user
    data['message_text'] = message_text
    return data


async def get_stop_all_users_access_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    message_text = (f"Действительно хотите приостановить доступ к папке "
                    f"<b>{smile_folder} {folder_name}</b>\nдля всех пользователей?")
    data['message_text'] = message_text
    return data
