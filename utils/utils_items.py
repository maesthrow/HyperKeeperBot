from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

from callbacks.callbackdata import BackToStandardFolderView
from load_all import bot
from utils.data_manager import get_data, set_data
from utils.utils_ import get_page_info, get_inline_markup_items_in_folder
from utils.utils_button_manager import create_general_reply_markup, general_buttons_folder
from utils.utils_data import get_current_folder_id
from utils.utils_folders_reader import get_sub_folders
from utils.utils_handlers import get_folder_path_names


async def show_all_items(user_id, current_folder_id=None, need_to_resend=False):
    data = await get_data(user_id)
    if not current_folder_id:
        current_folder_id = await get_current_folder_id(user_id)

    if need_to_resend:
        general_buttons = general_buttons_folder[:] #general_buttons_items_show_all[:]
        markup = create_general_reply_markup(general_buttons)
        data['markup'] = markup
        await bot.send_message(user_id, f"🗂️", reply_markup=markup)

    current_folder_path_names = await get_folder_path_names(user_id, current_folder_id)

    current_page_folder, current_page_item = await get_currents_pages(user_id, current_folder_id)

    items_page_info = await get_page_info(user_id, current_folder_id, 'items', 0)
    new_page_item = items_page_info.get('current_page_items')
    new_page_items = items_page_info.get('page_items')

    items_inline_markup = await get_inline_markup_items_in_folder(
        user_id, current_folder_id, current_page=new_page_item
    )
    items_inline_markup.inline_keyboard.insert(
        0,
        [
            InlineKeyboardButton(text='↩️ К папке', callback_data=BackToStandardFolderView(
                page_folder=current_page_folder, page_item=current_page_item
            ).pack())
        ]
    )
    if need_to_resend:
        folders_message = await bot.send_message(user_id, f"🗂️ <b>{current_folder_path_names}</b>",
                                                 reply_markup=items_inline_markup)
    else:
        folders_message = data.get('folders_message')
        await bot.edit_message_reply_markup(chat_id=user_id, message_id=folders_message.message_id,
                                            reply_markup=items_inline_markup)
    # await bot.delete_message(chat_id=chat.id, message_id=load_message.message_id)

    page_folders = data.get('page_folders')

    data['folders_message'] = folders_message
    data['page_folders'] = page_folders
    data['page_items'] = str(new_page_items)

    await set_data(user_id, data)


async def get_currents_pages(user_id, current_folder_id):
    folders_page_info = await get_page_info(user_id, current_folder_id, 'folders')
    current_page_folder = folders_page_info.get('current_page_folders')
    items_page_info = await get_page_info(user_id, current_folder_id, 'items')
    current_page_item = items_page_info.get('current_page_items')
    current_page_folder = 1 if not current_folder_id else current_page_folder
    current_page_item = 1 if not current_page_item else current_page_item
    return current_page_folder, current_page_item


async def get_all_search_items(user_id, folder_id, search_text):
    dict_inline_markups = {}
    await get_search_items(user_id, folder_id, search_text, dict_inline_markups)
    return dict_inline_markups


async def get_search_items(user_id, folder_id, search_text, dict_inline_markups):
    inline_markup = await get_inline_markup_items_in_folder(user_id, folder_id, 0, search_text)
    if any(inline_button for inline_button in inline_markup.inline_keyboard):
        dict_inline_markups[folder_id] = inline_markup
    sub_folders = await get_sub_folders(user_id, folder_id)
    for sub_folder_id in sub_folders:
        await get_search_items(user_id, sub_folder_id, search_text, dict_inline_markups)


def get_items_count_in_markups(dict_inline_markups: dict) -> int:
    total_items_count = 0

    for key, value in dict_inline_markups.items():
        inline_markup: InlineKeyboardMarkup = value

        # Подсчет кнопок в каждой строке клавиатуры
        for row in inline_markup.inline_keyboard:
            total_items_count += len(row)

    return total_items_count
