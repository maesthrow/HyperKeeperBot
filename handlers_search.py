import asyncio

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.types import User, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text

import states
from button_manager import create_general_reply_markup, general_buttons_search_items
from firebase_folder_reader import get_current_folder_id
from handlers_folder import show_folders
from load_all import dp, bot
from utils_folders_db import get_folder_path_names
from utils_items import get_search_items, get_all_search_items


@dp.message_handler(Text(equals="🔍 Поиск"))
async def search_item_handler(message: aiogram.types.Message):
    await bot.send_message(message.chat.id, "Введите текст для поиска:", reply_markup=ReplyKeyboardRemove())
    await states.Item.Search.set()


@dp.message_handler(state=states.Item.Search)
async def get_search_text(message: aiogram.types.Message, state: FSMContext):
    tg_user = User.get_current()
    folder_id = await get_current_folder_id(tg_user.id)
    dict_inline_markups = await get_all_search_items(folder_id, search_text=message.text)
    if len(dict_inline_markups) > 0:
        general_buttons = general_buttons_search_items[:]
        markup = create_general_reply_markup(general_buttons)
        await bot.send_message(message.chat.id, "🔍 РЕЗУЛЬТАТЫ ПОИСКА ⬇️", reply_markup=markup)
        for sub_folder_id, inline_markup in dict_inline_markups.items():
            await asyncio.sleep(0.5)
            folder_path_names = await get_folder_path_names(sub_folder_id)
            await bot.send_message(message.chat.id, f"🗂️ {folder_path_names}", reply_markup=inline_markup)
    else:
        await bot.send_message(message.chat.id, "По Вашему запросу ничего не найдено")

    await state.reset_state()


@dp.message_handler(Text(equals="🫡 Завершить поиск"))
async def search_item_handler(message: aiogram.types.Message):
    await show_folders()
