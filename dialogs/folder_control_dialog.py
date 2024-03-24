from aiogram_dialog import Window, Dialog, DialogManager, setup_dialogs
from aiogram_dialog.widgets.text import Format

from dialogs import keyboards
from handlers.states import FolderControlStates
from load_all import dp
from models.item_model import INVISIBLE_CHAR
from utils.utils_ import smile_folder, smile_item
from utils.utils_data import get_current_folder_id
from utils.utils_folders import get_folder_statistic
from utils.utils_folders_reader import get_folder_name
from utils.utils_handlers import get_folders_message_text
from utils.utils_items_reader import get_folder_items
from utils.utils_parse_mode_converter import escape_markdown


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user_id = dialog_manager.event.from_user.id
    folder_id = await get_current_folder_id(user_id)
    folders_message_text = await get_folders_message_text(user_id, folder_id)
    folders_message_text = escape_markdown(folders_message_text)
    data['folder_id'] = folder_id
    data['folders_message_text'] = f'🛠 <b>Меню управления папкой</b>\n\n{folders_message_text}'
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

    folder_statistic_text = f"📊 <b>Статистика папки</b>{INVISIBLE_CHAR*20}\n\n"\
                            f"{smile_folder} {folder_name}:\n\n"\
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


folder_control_main_window = Window(
    Format("{folders_message_text}"),
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


dialog_folder_control_main_menu = Dialog(
    folder_control_main_window,
    folder_control_info_message_window,
    folder_control_statistic_window,
    folder_control_delete_all_items_window,
)

dp.include_router(dialog_folder_control_main_menu)

setup_dialogs(dp)
