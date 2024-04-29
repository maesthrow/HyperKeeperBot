from aiogram_dialog import DialogManager

import dialogs.main_menu.keyboards as keyboards
import dialogs.general_keyboards as general_keyboards
from models.item_model import INVISIBLE_CHAR
from resources.text_getter import get_start_first_text, get_start_text, get_text
from utils.utils_ import smile_folder, smile_item, smile_file
from utils.utils_data import get_current_lang


async def get_start_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    start_data = dialog_manager.current_context().start_data
    is_first_connect = start_data.get('is_first_connect', False) if start_data else False
    if is_first_connect:
        start_text = await get_start_first_text(user)
    else:
        start_text = await get_start_text(user)

    return {
        'start_text': start_text,
        'btn_menu': general_keyboards.BUTTONS['menu'].get(language),
    }


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    menu_text = await get_text(user_id, 'menu')
    return {
        'message_text': f'<b>☰ {menu_text}</b>',  # {INVISIBLE_CHAR * 40}'
        'btn_storage': keyboards.BUTTONS['storage'].get(language),
        'btn_accesses': keyboards.BUTTONS['accesses'].get(language),
        'btn_search': keyboards.BUTTONS['search'].get(language),
        'btn_profile': keyboards.BUTTONS['profile'].get(language),
        'btn_settings': keyboards.BUTTONS['settings'].get(language),
        'btn_help': keyboards.BUTTONS['help'].get(language),
    }


async def get_live_search_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    data = dialog_manager.current_context().dialog_data
    live_search_title = await get_text(user_id, 'live_search_title')
    prompt_text = f"{live_search_title}{INVISIBLE_CHAR * 20}"
    if not data:
        bot_username = (await dialog_manager.event.bot.get_me()).username
        prompt_text_template = await get_text(user_id, 'live_search_prompt_text_template')
        prompt_text += prompt_text_template.format(
            bot_username=bot_username,
            smile_folder=smile_folder,
            smile_item=smile_item,
            smile_file=smile_file)

    data = {
        'message_text': prompt_text,
        'btn_menu': general_keyboards.BUTTONS['menu'].get(language),
        'btn_global': keyboards.SEARCH_BUTTONS['global'].get(language),
        'btn_folders': keyboards.SEARCH_BUTTONS['folders'].get(language),
        'btn_items': keyboards.SEARCH_BUTTONS['items'].get(language),
        'btn_files': keyboards.SEARCH_BUTTONS['files'].get(language),
    }
    dialog_manager.current_context().dialog_data = data
    return data
