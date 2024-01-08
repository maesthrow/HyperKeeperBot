import asyncio

import aiogram
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup

from load_all import dp, bot

settings_buttons = [
    [InlineKeyboardButton("🗂️ Количество папок на странице", callback_data="settings_count_folders_on_page")],
    [InlineKeyboardButton("📄 Количество записей на странице", callback_data="settings_count_items_on_page")],
    [InlineKeyboardButton("🌐 Язык интерфейса", callback_data="settings_language")],
    [InlineKeyboardButton("❌ Закрыть", callback_data="settings_close")],
]

back_to_settings_button = InlineKeyboardButton("Назад", callback_data="settings_back")

START_COUNT_RANGE = 3
END_COUNT_RANGE = 11
ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS = 2

settings_count_folders_buttons = [[] for _ in range(ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS + 1)]
for row in range(START_COUNT_RANGE, END_COUNT_RANGE):
    index = int((row - START_COUNT_RANGE) //
                ((END_COUNT_RANGE - START_COUNT_RANGE) / ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS)
                )
    (settings_count_folders_buttons[index]
     .append(InlineKeyboardButton(f"{row} 🗂️", callback_data=f"settings_count_folders_{row}")))
settings_count_folders_buttons[ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS].append(back_to_settings_button)

settings_count_items_buttons = [[], [], []]
for row in range(3, 11):
    index = int((row - START_COUNT_RANGE) //
                ((END_COUNT_RANGE - START_COUNT_RANGE) / ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS)
                )
    (settings_count_items_buttons[index]
     .append(InlineKeyboardButton(f"{row} 📄", callback_data=f"settings_count_items_{row}")))
settings_count_items_buttons[ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS].append(back_to_settings_button)


settings_languages_buttons = [
    [InlineKeyboardButton("🇷🇺 Русский", callback_data="settings_language_russian")],
    [InlineKeyboardButton("🇬🇧 English", callback_data="settings_language_english")],
]
settings_languages_buttons.append([back_to_settings_button])


@dp.message_handler(commands=["settings"])
async def search_item_handler(message: aiogram.types.Message):
    pre_message = await bot.send_message(message.chat.id, "⌛️", reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(chat_id=pre_message.chat.id, message_id=pre_message.message_id)
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=settings_buttons)
    await bot.send_message(message.chat.id, "<b>⚙️ Настройки:</b>", reply_markup=inline_markup)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'settings_count_folders_on_page')
async def settings_count_folders_on_page_handler(callback_query: aiogram.types.CallbackQuery):
    new_inline_markup = InlineKeyboardMarkup(row_width=4, inline_keyboard=settings_count_folders_buttons)
    new_text = "<b>🗂️ Количество папок на странице:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'settings_count_items_on_page')
async def settings_count_items_on_page_handler(callback_query: aiogram.types.CallbackQuery):
    new_inline_markup = InlineKeyboardMarkup(row_width=4, inline_keyboard=settings_count_items_buttons)
    new_text = "<b>📄 Количество записей на странице:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'settings_language')
async def settings_language_handler(callback_query: aiogram.types.CallbackQuery):
    new_inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=settings_languages_buttons)
    new_text = "<b>🌐 Язык интерфейса:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'settings_back')
async def back_settings_handler(callback_query: aiogram.types.CallbackQuery):
    # Новая клавиатура и текст
    new_inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=settings_buttons)
    new_text = "<b>⚙️ Настройки:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup
                                )



@dp.callback_query_handler(lambda callback_query: callback_query.data == 'settings_close')
async def close_settings_handler(callback_query: aiogram.types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
