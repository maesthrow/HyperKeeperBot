from aiogram_dialog import DialogManager

from dialogs.item_control import keyboards
from utils.data_manager import get_data
from utils.utils_data import get_current_lang
from utils.utils_items_reader import get_item


async def get_show_item_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)

    data = await get_data(user_id)
    item_id = data.get('show_item_id', '0-1/1')
    page = data.get('show_item_page', 0)

    author_user_id = user_id
    item = await get_item(author_user_id, item_id)
    message_text = item.get_body_markdown(page)
    if item.files_count() > 0:
        message_text = f'{message_text}\n_{item.get_files_statistic_text()}_'
    return {
        'message_text': message_text,
        'btn_storage': keyboards.BUTTONS['storage'].get(language),
        'btn_accesses': keyboards.BUTTONS['accesses'].get(language),
        'btn_search': keyboards.BUTTONS['search'].get(language),
        'btn_profile': keyboards.BUTTONS['profile'].get(language),
        'btn_settings': keyboards.BUTTONS['settings'].get(language),
        'btn_help': keyboards.BUTTONS['help'].get(language),
    }