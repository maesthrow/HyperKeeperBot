from typing import Optional

from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from dialogs import keyboards
from handlers.dialog.folder_control_handler import on_rename_folder, on_error_rename_folder, cancel_delete_handler, \
    stop_window_handler
from handlers.states import FolderControlStates
from models.folder_model import Folder
from models.item_model import INVISIBLE_CHAR
from utils.utils_ import smile_folder, smile_item
from utils.utils_access import get_access_users_info
from utils.utils_data import get_current_folder_id
from utils.utils_folders import get_folder_statistic, is_valid_folder_name
from utils.utils_folders_reader import get_folder_name, get_folder
from utils.utils_handlers import get_folders_message_text
from utils.utils_items_reader import get_folder_items
from utils.utils_parse_mode_converter import escape_markdown


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    message_text = await get_folders_message_text(user_id, folder_id)
    #message_text = escape_markdown(folders_message_text)
    data['folder_id'] = folder_id
    data['message_text'] = f'🛠 <b>Меню управления папкой</b>\n\n{message_text}'
    return data


async def get_message_text(dialog_manager: DialogManager, **kwargs):
    return {"message_text": dialog_manager.current_context().dialog_data.get("message_text", None)}


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
        message_text = "В этой папке нет записей."
    data['folder_id'] = folder_id
    data['items_count'] = items_count
    data['message_text'] = message_text
    return data


async def get_rename_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    folder_name = escape_markdown(folder_name)
    message_text = f"*Переименовать папку* {smile_folder}"\
                   f"\n\nМожете скопировать текущее название:"\
                   f"\n'`{folder_name}`'"\
                   f"\n\n_*Напишите новое название папки:*_"
    data['user_id'] = user_id
    data['folder_id'] = folder_id
    data['message_text'] = message_text
    return data


async def get_delete_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder_name = await get_folder_name(user_id, folder_id)
    message_text = f"Хотите удалить папку {smile_folder} '{folder_name}' и все ее содержимое?"
    data['message_text'] = message_text
    return data


async def get_access_menu_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folder: Folder = await get_folder(user_id, folder_id)
    switch_inline_query = f'access_{user_id}_{folder_id}'
    users_access_info = await get_access_users_info(folder) or 'Ничего не найдено.'
    #users_access_info = escape_markdown(users_access_info)
    message_text = f'🔐 <b>Управление доступом к папке</b>'\
                   f'\n\n{smile_folder} {folder.name}'\
                   f'\n\n<i>Пользователи, которым вы предоставили доступ:</i>'\
                   f'\n\n{users_access_info}'
    data['folder_has_access_users'] = folder.has_access_users()
    data['switch_inline_query'] = switch_inline_query
    data['message_text'] = message_text
    return data


def filter_invalid_chars(message: Message) -> Optional[str]:
    input_text = message.text
    if is_valid_folder_name(input_text):
        return input_text
    return None


folder_control_main_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_main_menu(),
    state=FolderControlStates.MainMenu,
    getter=get_main_menu_data
)

folder_control_info_message_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_info_message(),
    state=FolderControlStates.InfoMessage,
    getter=get_message_text
)

folder_control_statistic_window = Window(
    Format("{folder_statistic_text}"),
    *keyboards.folder_control_statistic(),
    state=FolderControlStates.StatisticMenu,
    getter=get_statistic_data
)

folder_control_delete_all_items_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_delete_all_items(),
    state=FolderControlStates.DeleteAllItemsQuestion,
    getter=get_delete_all_items_data
)

folder_control_rename_window = Window(
    Format("{message_text}"),
    TextInput(
        id="new_folder_name",
        on_success=on_rename_folder,
        on_error=on_error_rename_folder,
        filter=filter_invalid_chars),
    Button(id='cancel_rename', text=Const('Отменить'), on_click=cancel_delete_handler),
    state=FolderControlStates.Rename,
    getter=get_rename_data,
    parse_mode=ParseMode.MARKDOWN_V2
)

folder_control_delete_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_delete(),
    state=FolderControlStates.Delete,
    getter=get_delete_data
)

folder_control_after_delete_message_window = Window(
    Format("{message_text}"),
    *keyboards.folder_control_after_delete_message(),
    state=FolderControlStates.AfterDelete,
    getter=get_message_text
)

folder_control_access_menu_window = Window(
    Format("{message_text}"),
    #MessageInput(func=stop_window_handler),
    *keyboards.folder_control_access_menu(),
    state=FolderControlStates.AccessMenu,
    getter=get_access_menu_data
)

folder_control_access_confirm_window = Window(
    #Format("{message_text}"),
    Const("Подтверждаете доступ?"),
    *keyboards.folder_control_access_confirm(),
    state=FolderControlStates.AccessConfirm,
    #getter=get_access_menu_data
)

dialog_folder_control_main_menu = Dialog(
    folder_control_main_window,
    folder_control_info_message_window,
    folder_control_statistic_window,
    folder_control_delete_all_items_window,
    folder_control_rename_window,
    folder_control_delete_window,
    folder_control_after_delete_message_window,
    folder_control_access_menu_window
)

