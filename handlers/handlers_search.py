import asyncio

import aiogram
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from handlers import states
from handlers.handlers_folder import show_folders
from load_all import bot, dp
from utils.data_manager import get_data, set_data
from utils.utils_ import get_folder_path_names
from utils.utils_button_manager import create_general_reply_markup, general_buttons_search_items
from utils.utils_data import get_current_folder_id
from utils.utils_items import get_all_search_items, get_items_count_in_markups
from utils.utils_statistic import get_word_items_by_count

cancel_enter_search_text_button = InlineKeyboardButton(text="Отменить", callback_data="cancel_enter_search_text")

router = Router()
dp.include_router(router)


@router.message(F.text.in_({"🔍 Поиск", "🔄 Новый поиск 🔍️"}))
async def search_item_handler(message: aiogram.types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    data['dict_search_data'] = None
    await set_data(user_id, data)

    await bot.send_message(message.chat.id, "🔍", reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.3)
    buttons = [[cancel_enter_search_text_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    await bot.send_message(message.chat.id, "Введите текст для поиска:", reply_markup=inline_markup)
    await state.set_state(states.Item.Search)


@router.message(states.Item.Search)
async def get_search_text(message: aiogram.types.Message, state: FSMContext):
    user_id = message.from_user.id

    wait_message = await bot.send_message(user_id, f"⌛️")

    folder_id = await get_current_folder_id(user_id)
    dict_inline_markups = await get_all_search_items(user_id, folder_id, search_text=message.text)

    dict_search_data = {
        'source_folder_id': folder_id, 'search_text': message.text, 'dict_inline_markups': dict_inline_markups
    }

    await show_search_results(user_id, dict_search_data)
    await bot.delete_message(user_id, wait_message.message_id)

    if len(dict_inline_markups) > 0:
        data = await get_data(user_id)
        data['dict_search_data'] = dict_search_data
        await set_data(user_id, data)

    # else:
    #     await asyncio.sleep(0.5)
    #     await search_item_handler(message)
    # await show_folders()

    await state.set_state()


async def show_search_results(user_id, dict_search_data):
    source_folder_id = dict_search_data['source_folder_id']
    search_text = dict_search_data['search_text']
    dict_inline_markups = dict_search_data['dict_inline_markups']

    general_buttons = general_buttons_search_items[:]
    markup = create_general_reply_markup(general_buttons)

    data = await get_data(user_id)
    data['current_keyboard'] = markup
    await set_data(user_id, data)

    level_folder_path_names = await get_folder_path_names(user_id, source_folder_id)
    searched_items_count = get_items_count_in_markups(dict_inline_markups)
    word_items_by_count = get_word_items_by_count(searched_items_count)
    await bot.send_message(user_id, f"⬇️ <b>РЕЗУЛЬТАТЫ ПОИСКА</b> 🔎\n\n"
                                    f"<u>Найдено</u>: <b>{searched_items_count}</b> {word_items_by_count}\n\n"
                                    f"<u>Уровень (включая вложенные папки)</u>:\n"
                                    f"🗂️ <b>{level_folder_path_names[:-1]}</b>\n\n"
                                    f"<u>Запрос</u>: "
                                    f"<b>'{search_text}'</b>",
                           reply_markup=markup)
    if len(dict_inline_markups) > 0:
        for sub_folder_id, inline_markup in dict_inline_markups.items():
            await asyncio.sleep(0.2)
            folder_path_names = await get_folder_path_names(user_id, sub_folder_id)
            await bot.send_message(user_id, f"🗂️ {folder_path_names}",
                                   reply_markup=inline_markup)
    else:
        await asyncio.sleep(0.2)
        await bot.send_message(user_id, f"Ничего не найдено 🤷‍♂️")


@router.callback_query(states.Item.Search, F.data.contains("cancel_enter_search_text"))
async def cancel_enter_search_text(call: CallbackQuery, state: FSMContext):
    # await call.message.answer("⌛️")
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    await state.set_state()
    await show_folders(call.from_user.id)
    await call.answer()
