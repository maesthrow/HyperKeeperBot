from aiogram.types import User, Chat, InlineKeyboardMarkup

from load_all import bot, dp
from utils.utils_ import get_page_info, get_inline_markup_items_in_folder, get_folder_path_names, get_sub_folders
from utils.utils_button_manager import general_buttons_items_show_all, create_general_reply_markup
from utils.utils_data import get_current_folder_id


async def show_all_items(current_folder_id=None, need_to_resend=False):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(chat=chat, user=tg_user)
    if not current_folder_id:
        current_folder_id = await get_current_folder_id()

    if need_to_resend:
        general_buttons = general_buttons_items_show_all[:]
        markup = create_general_reply_markup(general_buttons)
        data['markup'] = markup
        await bot.send_message(chat.id, f"🗂️", reply_markup=markup)

    current_folder_path_names = await get_folder_path_names(current_folder_id)

    # load_message = await bot.send_message(chat.id, f"⌛️")
    items_page_info = await get_page_info(current_folder_id, 'items', 0)
    current_item_page = items_page_info.get('current_page_items')
    new_page_items = items_page_info.get('page_items')

    items_inline_markup = await get_inline_markup_items_in_folder(current_folder_id, current_page=current_item_page)
    if need_to_resend:
        folders_message = await bot.send_message(chat.id, f"🗂️ <b>{current_folder_path_names}</b>",
                                                 reply_markup=items_inline_markup)
    else:
        folders_message = data.get('folders_message')
        await bot.edit_message_reply_markup(chat_id=chat.id, message_id=folders_message.message_id,
                                            reply_markup=items_inline_markup)
    # await bot.delete_message(chat_id=chat.id, message_id=load_message.message_id)

    page_folders = data.get('page_folders')

    data['folders_message'] = folders_message
    data['page_folders'] = page_folders
    data['page_items'] = str(new_page_items)

    await dp.storage.update_data(user=tg_user, chat=chat, data=data)


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


def get_items_count_in_markups(dict_inline_markups: dict) -> int:
    total_items_count = 0

    for key, value in dict_inline_markups.items():
        inline_markup: InlineKeyboardMarkup = value

        # Подсчет кнопок в каждой строке клавиатуры
        for row in inline_markup.inline_keyboard:
            total_items_count += len(row)

    return total_items_count
