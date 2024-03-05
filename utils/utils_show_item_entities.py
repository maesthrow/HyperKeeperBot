import copy

from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks.callbackdata import SaveItemCallback
from load_all import bot
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import save_page_buttons, FilesButtons, get_text_pages_buttons, item_inline_buttons, \
    item_inline_buttons_with_files, save_item_full_mode_button
from utils.utils_items_reader import get_item


async def show_item_page_as_text_only(user_id, item_id, author_user_id=None, page=0):
    if not author_user_id:
        author_user_id = user_id
    item = await get_item(author_user_id, item_id)

    inline_markup = InlineKeyboardMarkup(inline_keyboard=save_page_buttons)
    message_text = item.get_text_markdown(page)
    bot_message = await bot.send_message(
        chat_id=user_id,
        text=message_text,
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def show_item_full_mode(user_id, item_id, author_user_id=None, page=0):
    if not author_user_id:
        author_user_id = user_id
    item = await get_item(author_user_id, item_id)

    inline_markup = await get_saved_item_inline_markup(author_user_id, item, page)
    message_text = item.get_body_markdown(page)
    bot_message = await bot.send_message(
        chat_id=user_id,
        text=message_text,
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    data = await get_data(user_id)
    add_item_messages = data.get('add_item_messages', [])
    add_item_messages.append(bot_message)
    data['add_item_messages'] = add_item_messages
    await set_data(user_id, data)


async def get_saved_item_inline_markup(author_user_id, item: Item, page: int):
    if item.files_count() == 0:
        item_inlines = [copy.deepcopy(item_inline_buttons[0])]
    else:
        item_inlines = copy.deepcopy([item_inline_buttons_with_files[0], item_inline_buttons_with_files[2]])
        files_button: InlineKeyboardButton = FilesButtons.get_show_button(item.files_count())
        item_inlines[-1][-1] = files_button

    save_button = copy.deepcopy(save_item_full_mode_button)
    save_button.callback_data = SaveItemCallback(author_user_id=author_user_id, item_id=item.id).pack()
    item_inlines[0][0] = save_button
    if item.files_count() > 0:
        item_inlines[-1][0].switch_inline_query_current_chat = f"browse_{author_user_id}_{item.id}_{-1}_content"
    if item.pages_count() > 1:
        item_inlines.insert(0, get_text_pages_buttons(author_user_id, item, page))

    return InlineKeyboardMarkup(row_width=2, inline_keyboard=item_inlines, resize_keyboard=True)