from aiogram.types import User, Chat

from button_manager import general_buttons_items_show_all, create_general_reply_markup
from load_all import bot, dp
from utils import get_page_info, get_inline_markup_items_in_folder, get_current_folder_id
from utils_folders_db import get_folder_path_names, get_sub_folders


async def show_all_items(current_folder_id=None):
    tg_user = User.get_current()
    chat = Chat.get_current()
    if not current_folder_id:
        current_folder_id = await get_current_folder_id()

    general_buttons = general_buttons_items_show_all[:]
    markup = create_general_reply_markup(general_buttons)

    current_folder_path_names = await get_folder_path_names(current_folder_id)
    await bot.send_message(chat.id, f"🗂️", reply_markup=markup)

    # load_message = await bot.send_message(chat.id, f"⌛️")
    items_page_info = await get_page_info(current_folder_id, 'items', 0)
    current_item_page = items_page_info.get('current_page_items')
    new_page_items = items_page_info.get('page_items')

    items_inline_markup = await get_inline_markup_items_in_folder(current_folder_id, current_page=current_item_page)
    folders_message = await bot.send_message(chat.id, f"🗂️ <b>{current_folder_path_names}</b>",
                                             reply_markup=items_inline_markup)
    # await bot.delete_message(chat_id=chat.id, message_id=load_message.message_id)

    data = await dp.storage.get_data(chat=chat, user=tg_user)
    page_folders = data.get('page_folders')
    await dp.storage.update_data(user=tg_user, chat=chat,
                                 data={'current_keyboard': markup, 'folders_message': folders_message,
                                       'page_folders': page_folders, 'page_items': str(new_page_items)})


async def get_all_search_items(folder_id, search_text):
    dict_inline_markups = {}
    await get_search_items(folder_id, search_text, dict_inline_markups)
    return dict_inline_markups


async def get_search_items(folder_id, search_text, dict_inline_markups):
    inline_markup = await get_inline_markup_items_in_folder(folder_id, 0, search_text)
    if any(inline_button for inline_button in inline_markup.inline_keyboard):
        dict_inline_markups[folder_id] = inline_markup
    sub_folders = await get_sub_folders(folder_id)
    for sub_folder_id in sub_folders:
        await get_search_items(sub_folder_id, search_text, dict_inline_markups)


def get_word_items_by_count(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "запись"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return "записи"
    else:
        return "записей"

