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
    menu_text = await get_text(user_id, 'Menu')
    return {
        'message_text': f'<b>☰ {menu_text}</b>', # {INVISIBLE_CHAR * 40}'
        'btn_storage': keyboards.BUTTONS['storage'].get(language),
        'btn_accesses': keyboards.BUTTONS['accesses'].get(language),
        'btn_search': keyboards.BUTTONS['search'].get(language),
        'btn_profile': keyboards.BUTTONS['profile'].get(language),
        'btn_settings': keyboards.BUTTONS['settings'].get(language),
        'btn_help': keyboards.BUTTONS['help'].get(language),
    }


async def get_live_search_data(dialog_manager: DialogManager, **kwargs):
    language = await get_current_lang(dialog_manager.event.from_user.id)
    data = dialog_manager.current_context().dialog_data
    live_search_title = f"🔍 <b>Live-поиск</b>"
    if not data:
        bot_username = (await dialog_manager.event.bot.get_me()).username
        prompt_text = f"{live_search_title}" \
                      "\n\n<i>Вводите поисковый запрос из любого чата, упоминая бота:</i>" \
                      "\n\nГлобальный поиск 🌐" \
                      f"\n'@{bot_username} <i>ваш_запрос'</i>" \
                      f"\n\nПоиск папок {smile_folder}" \
                      f"\n'@{bot_username} folders/<i>ваш_запрос</i>'" \
                      f"\n\nПоиск записей {smile_item}" \
                      f"\n'@{bot_username} items/<i>ваш_запрос</i>'" \
                      f"\n\nПоиск файлов {smile_file}" \
                      f"\n'@{bot_username} files/<i>ваш_запрос</i>'" \
                      "\n\n<i>Либо используйте кнопки</i> ⬇️"
    else:
        prompt_text = f"{live_search_title}{INVISIBLE_CHAR*20}"

    data = {
        'message_text': prompt_text,
        'btn_menu': (general_keyboards.BUTTONS['menu'].get(language),)
    }
    dialog_manager.current_context().dialog_data = data
    return data

