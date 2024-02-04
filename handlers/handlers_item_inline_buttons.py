import asyncio
import concurrent.futures
import functools

import aiogram.types
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from handlers.handlers_folder import show_folders
from load_all import bot, dp
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import show_item_files_button, hide_item_files_button
from utils.utils_data import get_current_folder_id
from utils.utils_item_show_files import show_item_files
from utils.utils_items_db import util_delete_item
from utils.utils_items_reader import get_folder_id
from utils.utils_parse_mode_converter import to_markdown_text_show

# import handlers.handlers_item_edit_inline_buttons


delete_question = f"\n\n\n_*Хотите удалить запись?*_"

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "close_item")
async def close_item_handler(call: CallbackQuery = None, message: aiogram.types.Message = None):
    if message is None:
        message = call.message

    user_id = call.from_user.id if call else message.from_user.id if message else None
    data = await get_data(user_id)
    item_files_messages = data.get('item_files_messages', [])
    accept_add_item_message = data.get('accept_add_item_message', None)

    tasks = [
        close_files(item_files_messages),
        bot.delete_message(message.chat.id, message.message_id)
    ]
    if accept_add_item_message:
        tasks.insert(0, bot.delete_message(chat_id=user_id, message_id=accept_add_item_message.message_id))

    await asyncio.gather(*tasks)

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
    inline_markup = call.message.reply_markup
    inline_markup.inline_keyboard[-1][-1] = hide_item_files_button

    data = await get_data(call.from_user.id)
    item = data.get('current_item', None)
    if item:
        await call.message.edit_reply_markup(reply_markup=inline_markup)
        await asyncio.gather(
            show_item_files(call.from_user.id, item),
            update_inline_markup_data(call.from_user.id, inline_markup)
        )
    await call.answer()


@router.callback_query(F.data == "hide_item_files")
async def hide_item_files_handler(call: CallbackQuery):
    inline_markup = call.message.reply_markup
    inline_markup.inline_keyboard[-1][-1] = show_item_files_button

    user_id = call.from_user.id

    data = await get_data(user_id)
    item_files_messages = data.get('item_files_messages', [])

    await call.message.edit_reply_markup(reply_markup=inline_markup)
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

    format_message_text = to_markdown_text_show(call.message.text, call.message.entities)
    print(f"format_message_text\n{format_message_text}")

    await call.answer()
    await call.message.edit_text(
        text=f"{format_message_text}{delete_question}",
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )


@router.callback_query(F.data == "edit_item_back")
@router.callback_query(F.data == "delete_item_no")
async def cancel_delete_item_handler(call: CallbackQuery):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item: Item = data.get('current_item', None)
    if item:
        inline_markup = await get_current_inline_markup(user_id)
        item_body = item.get_body_markdown()
        print(f"cancel_delete_item_body\n{item_body}")
        await call.message.edit_text(
            text=item_body,
            reply_markup=inline_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    await call.answer()


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


