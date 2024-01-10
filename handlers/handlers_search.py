import asyncio

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.types import User, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Chat
from aiogram.dispatcher.filters import Text

from handlers import states
from utils.utils_button_manager import create_general_reply_markup, general_buttons_search_items
from handlers.handlers_folder import show_folders
from load_all import dp, bot
from utils.utils_ import get_folder_path_names
from utils.utils_data import get_current_folder_id
from utils.utils_items import get_all_search_items, get_items_count_in_markups
from utils.utils_statistic import get_word_items_by_count

cancel_enter_search_text_button = InlineKeyboardButton("Отменить", callback_data="cancel_enter_search_text")


@dp.message_handler(Text(equals="🔍 Поиск") | Text(equals="🔄 Новый поиск 🔍️"))
async def search_item_handler(message: aiogram.types.Message):
    tg_user = User.get_current()
    chat = Chat.get_current()
    data = await dp.storage.get_data(user=tg_user, chat=chat)
    data['dict_search_data'] = None
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)

    await bot.send_message(message.chat.id, "🔍", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.3)
    buttons = [[cancel_enter_search_text_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    await bot.send_message(message.chat.id, "Введите текст для поиска:", reply_markup=inline_markup)
    await states.Item.Search.set()


@dp.message_handler(state=states.Item.Search)
async def get_search_text(message: aiogram.types.Message, state: FSMContext):
    tg_user = User.get_current()
    chat = Chat.get_current()

    wait_message = await bot.send_message(chat.id, f"⌛️")

    folder_id = await get_current_folder_id()
    dict_inline_markups = await get_all_search_items(folder_id, search_text=message.text)

    dict_search_data = {
        'source_folder_id': folder_id, 'search_text': message.text, 'dict_inline_markups': dict_inline_markups
    }

    await show_search_results(dict_search_data)
    await bot.delete_message(chat.id, wait_message.message_id)

    if len(dict_inline_markups) > 0:
        data = await dp.storage.get_data(user=tg_user, chat=chat)
        data['dict_search_data'] = dict_search_data
        await dp.storage.update_data(user=tg_user, chat=chat, data=data)

    # else:
    #     await asyncio.sleep(0.5)
    #     await search_item_handler(message)
    # await show_folders()

    await state.reset_state()


async def show_search_results(dict_search_data):
    tg_user = User.get_current()
    chat = Chat.get_current()

    source_folder_id = dict_search_data['source_folder_id']
    search_text = dict_search_data['search_text']
    dict_inline_markups = dict_search_data['dict_inline_markups']

    general_buttons = general_buttons_search_items[:]
    markup = create_general_reply_markup(general_buttons)

    data = await dp.storage.get_data(user=tg_user, chat=chat)
    data['current_keyboard'] = markup
    await dp.storage.update_data(user=tg_user, chat=chat, data=data)

    chat = Chat.get_current()

    level_folder_path_names = await get_folder_path_names(source_folder_id)
    searched_items_count = get_items_count_in_markups(dict_inline_markups)
    word_items_by_count = get_word_items_by_count(searched_items_count)
    await bot.send_message(chat.id, f"⬇️ <b>РЕЗУЛЬТАТЫ ПОИСКА</b> 🔎\n\n"
                                    f"<u>Найдено</u>: <b>{searched_items_count}</b> {word_items_by_count}\n\n"
                                    f"<u>Уровень (включая вложенные папки)</u>:\n"
                                    f"🗂️ <b>{level_folder_path_names[:-1]}</b>\n\n"
                                    f"<u>Запрос</u>: "
                                    f"<b>'{search_text}'</b>",
                           reply_markup=markup)
    if len(dict_inline_markups) > 0:
        for sub_folder_id, inline_markup in dict_inline_markups.items():
            await asyncio.sleep(0.2)
            folder_path_names = await get_folder_path_names(sub_folder_id)
            await bot.send_message(Chat.get_current().id, f"🗂️ {folder_path_names}",
                                   reply_markup=inline_markup)
    else:
        await asyncio.sleep(0.2)
        await bot.send_message(chat.id, f"Ничего не найдено 🤷‍♂️")


@dp.callback_query_handler(text_contains="cancel_enter_search_text", state=states.Item.Search)
async def cancel_enter_search_text(call: CallbackQuery, state: FSMContext):
    # await call.message.answer("⌛️")
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await state.reset_state()
    await show_folders()
