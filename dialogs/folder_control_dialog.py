from aiogram_dialog import Window, Dialog, DialogManager, setup_dialogs
from aiogram_dialog.widgets.text import Format

from dialogs import keyboards
from handlers.states import FolderControlStates
from load_all import dp
from utils.utils_ import smile_folder, smile_item
from utils.utils_data import get_current_folder_id
from utils.utils_folders import get_folder_statistic
from utils.utils_folders_reader import get_folder_name
from utils.utils_handlers import get_folders_message_text
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

    statistic_text = (f"<u>Количество папок</u> {smile_folder}: <b>{folders_count}</b>\n"
                      f"<u>Количество записей</u> {smile_item}: <b>{items_count}</b>\n\n"
                      f"<b>С учетом вложенных папок:</b>\n"
                      f"<u>Всего папок</u> {smile_folder}: <b>{deep_folders_count}</b>\n"
                      f"<u>Всего записей</u> {smile_item}: <b>{deep_items_count}</b>")

    folder_statistic_text = f"📊 <b>Статистика папки</b>\n\n"\
                            f"{smile_folder} {folder_name}:\n\n"\
                            f"{statistic_text}"

    data['folder_statistic_text'] = folder_statistic_text
    return data


folder_control_main_window = Window(
    Format("{folders_message_text}"),
    *keyboards.folder_control_main_menu(),
    state=FolderControlStates.MainMenu,
    getter=get_main_menu_data
)

folder_control_statistic_window = Window(
    Format("{folder_statistic_text}"),
    *keyboards.folder_control_statistic(),
    state=FolderControlStates.StatisticMenu,
    getter=get_statistic_data
)


dialog_folder_control_main_menu = Dialog(folder_control_main_window, folder_control_statistic_window)

dp.include_router(dialog_folder_control_main_menu)

setup_dialogs(dp)
