import asyncio
import concurrent.futures
import functools

import aiogram.types
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from callbacks.callbackdata import TextPagesCallback, SaveItemCallback
from handlers.handlers_folder import show_folders
from load_all import bot, dp
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import FilesButtons, get_repost_button_in_markup, get_save_button_in_markup
from utils.utils_data import get_current_folder_id
from utils.utils_item_show_files import show_item_files
from utils.utils_items_db import util_delete_item
from utils.utils_items_reader import get_folder_id, get_item
from utils.utils_parse_mode_converter import to_markdown_text

# import handlers.handlers_item_edit_inline_buttons


delete_question = f"\n\n_*Хотите удалить запись?*_"

router = Router()
dp.include_router(router)


@router.callback_query(F.data.contains("close_item"))
async def close_item_handler(call: CallbackQuery = None, message: Message = None):
    #print(f"call {call}\nmessage {message}")
    if message is None:
        message = call.message
        if not message:
            return

    user_id = call.from_user.id if call else message.from_user.id if message else None
    message_id = message.message_id
    data = await get_data(user_id)
    item_files_messages = data.get('item_files_messages', [])
    accept_add_item_message = data.get('accept_add_item_message', None)

    chat_id = message.chat.id if message else call.from_user.id
    tasks = [
        close_files(item_files_messages),
        bot.delete_message(chat_id, message_id)
    ]
    if accept_add_item_message:
        tasks.insert(0, bot.delete_message(chat_id=user_id, message_id=accept_add_item_message.message_id))

    try:
        await asyncio.gather(*tasks)
    except:
        print('close_item_handler -> Не был найден message для удаления')

    data['item_files_messages'] = []
    data['accept_add_item_message'] = None
    await set_data(user_id, data)
    if call:
        await call.answer()


async def update_inline_markup_data(user_id, inline_markup: InlineKeyboardMarkup):
    data = await get_data(user_id)
    data['current_inline_markup'] = inline_markup
    await set_data(user_id, data)


async def get_current_inline_markup(user_id):
    data = await get_data(user_id)
    inline_markup = data.get('current_inline_markup', None)
    return inline_markup


@router.callback_query(F.data == "show_item_files")
async def show_item_files_handler(call: CallbackQuery):
    user_id = call.from_user.id
    inline_markup = call.message.reply_markup
    repost_button = get_repost_button_in_markup(inline_markup)
    if repost_button:
        author_user_id, item_id, page = repost_button.switch_inline_query.split('_')
    else:
        save_button: InlineKeyboardButton = get_save_button_in_markup(inline_markup)
        print(f'save_button.callback_data {save_button.callback_data}')
        save_button_call_data: SaveItemCallback = SaveItemCallback.unpack(save_button.callback_data)
        author_user_id = save_button_call_data.author_user_id
        item_id = save_button_call_data.item_id

    print(f"author_user_id {author_user_id}\nitem_id {item_id}")

    item: Item = await get_item(int(author_user_id), item_id) #  data.get('current_item', None)
    data = await get_data(user_id)
    data['current_item'] = item
    await set_data(user_id, data)

    files_button = FilesButtons.get_hide_button(item.files_count())
    inline_markup.inline_keyboard[-1][-1] = files_button

    await call.message.edit_reply_markup(reply_markup=inline_markup)
    await asyncio.gather(
        show_item_files(user_id, item),
        update_inline_markup_data(call.from_user.id, inline_markup)
    )

    await call.answer()


@router.callback_query(F.data == "hide_item_files")
async def hide_item_files_handler(call: CallbackQuery, is_native_call=True):
    user_id = call.from_user.id
    data = await get_data(user_id)
    inline_markup = call.message.reply_markup
    item: Item = data.get('current_item', None)

    if is_native_call:
        files_button = FilesButtons.get_show_button(item.files_count())
        inline_markup.inline_keyboard[-1][-1] = files_button
        await call.message.edit_reply_markup(reply_markup=inline_markup)

    item_files_messages = data.get('item_files_messages', [])
    await asyncio.gather(
        close_files(item_files_messages),
        update_inline_markup_data(user_id, inline_markup)
    )
    await call.answer()


async def close_files(item_files_messages: list):
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future = executor.submit(functools.partial(on_close_files, item_files_messages))
            result = await future.result(timeout=3)
    except:
        pass


async def on_close_files(item_files_messages: list):
    if len(item_files_messages) > 0:
        delete_tasks = [delete_files_message(message) for message in item_files_messages]
        await asyncio.gather(*delete_tasks)


async def delete_files_message(message):
    if isinstance(message, list):
        delete_tasks = [delete_message(msg.chat.id, msg.message_id) for msg in message]
        await asyncio.gather(*delete_tasks)
    else:
        await bot.delete_message(message.chat.id, message.message_id)


async def delete_message(chat_id, message_id):
    await bot.delete_message(chat_id, message_id)


@router.callback_query(F.data == "delete_item")
async def delete_item_handler(call: CallbackQuery):
    item_inlines = [
        [
            InlineKeyboardButton(text="☑️ Да", callback_data="delete_item_yes"),
            InlineKeyboardButton(text="✖️ Нет", callback_data="delete_item_no"),
        ]
    ]
    inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=item_inlines)
    item_body, current_markup = await get_item_body_and_current_markup(call.from_user.id)

    await call.message.edit_text(
        text=f'{item_body}{delete_question}',
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await call.answer()


@router.callback_query(F.data == "edit_item_back")
@router.callback_query(F.data == "delete_item_no")
async def cancel_delete_item_handler(call: CallbackQuery):
    item_body, current_markup = await get_item_body_and_current_markup(call.from_user.id)
    await call.message.edit_text(
        text=item_body,
        reply_markup=current_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await call.answer()


async def get_item_body_and_current_markup(user_id):
    data = await get_data(user_id)
    item: Item = data.get('current_item', None)
    item_body = ''
    current_markup = None
    if item:
        page = 0
        current_markup = await get_current_inline_markup(user_id)
        middle_btn = current_markup.inline_keyboard[0][1]
        if middle_btn.callback_data and TextPagesCallback.__prefix__ in middle_btn.callback_data:
            callback_data: TextPagesCallback = TextPagesCallback.unpack(middle_btn.callback_data)
            page = callback_data.page
        item_body = item.get_body_markdown(page)
    return item_body, current_markup


@router.callback_query(F.data == "delete_item_yes")
async def accept_delete_item_handler(call: CallbackQuery):
    data = await get_data(call.from_user.id)
    item_id = data.get('item_id', None)
    if item_id:
        result = await util_delete_item(call.from_user.id, item_id)
        if result:
            await asyncio.gather(
                close_item_handler(call=call),
                refresh_folder(call.from_user.id)
            )
        await call.answer(text=f"Не получилось удалить запись.'", show_alert=True)
    else:
        await call.answer(text=f"Что то пошло не так при удалении записи.", show_alert=True)


async def refresh_folder(user_id):
    folder_id = await get_current_folder_id(user_id)
    await show_folders(user_id, current_folder_id=folder_id, need_to_resend=False)


@router.callback_query(F.data == "move_item")
async def movement_item_handler(call: CallbackQuery, folder_id=None):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    if not data.get('movement_item_id'):
        data['movement_item_id'] = item_id
        await set_data(user_id, data)

    message_text = "❗Вы не завершили перемещение❗\n" if folder_id else ""
    message_text += f"Выберите папку, в которую хотите переместить запись: ⬇️"
    await bot.send_message(call.message.chat.id, message_text)
    await asyncio.sleep(0.5)

    if not folder_id:
        folder_id = get_folder_id(item_id)
    await show_folders(user_id, folder_id, need_to_resend=True)


