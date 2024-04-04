import copy

import aiogram
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from enums.enums import Language
from handlers_pack.handlers_folder import show_folders
from load_all import bot, dp
from utils.utils_data import get_from_user_collection, set_to_user_collection

settings_buttons = [
    [InlineKeyboardButton(text="🗂️ Количество папок на странице", callback_data="settings_count_folders_on_page")],
    [InlineKeyboardButton(text="📄 Количество записей на странице", callback_data="settings_count_items_on_page")],
    [InlineKeyboardButton(text="🌐 Язык интерфейса", callback_data="settings_language")],
    [InlineKeyboardButton(text="✖️ Закрыть", callback_data="settings_close")],
]

back_to_settings_button = InlineKeyboardButton(text="↩️ Назад", callback_data="settings_back")

START_FOLDER_COUNT_RANGE = 6
END_FOLDER_COUNT_RANGE = 20
COUNT_FOLDER_ON_ROW = 2

START_ITEM_COUNT_RANGE = 3
END_ITEM_COUNT_RANGE = 10
COUNT_ITEM_ON_ROW = 1

ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS = 2

CURRENT_LABEL = "✅"  # "🟢"

settings_count_folders_buttons = [[] for _ in range(ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS + 1)]
for row in range(START_FOLDER_COUNT_RANGE, END_FOLDER_COUNT_RANGE + COUNT_FOLDER_ON_ROW, COUNT_FOLDER_ON_ROW):
    index = int((row - START_FOLDER_COUNT_RANGE + COUNT_FOLDER_ON_ROW) //
                ((END_FOLDER_COUNT_RANGE + COUNT_FOLDER_ON_ROW + (COUNT_FOLDER_ON_ROW - 1) - START_FOLDER_COUNT_RANGE) /
                 ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS)
                )
    (settings_count_folders_buttons[index]
     .append(InlineKeyboardButton(text=str(row), callback_data=f"settings_count_folders_{row}")))
settings_count_folders_buttons[ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS].append(back_to_settings_button)

settings_count_items_buttons = [[], [], []]
for row in range(START_ITEM_COUNT_RANGE, END_ITEM_COUNT_RANGE + 1):
    index = int((row - START_ITEM_COUNT_RANGE) //
                ((END_ITEM_COUNT_RANGE + COUNT_ITEM_ON_ROW + (COUNT_ITEM_ON_ROW - 1) - START_ITEM_COUNT_RANGE) /
                 ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS)
                )
    (settings_count_items_buttons[index]
     .append(InlineKeyboardButton(text=str(row), callback_data=f"settings_count_items_{row}")))
settings_count_items_buttons[ROWS_COUNT_FOR_COUNT_ON_PAGE_SETTINGS].append(back_to_settings_button)

# Создаем кнопки для каждого языка
settings_languages_buttons = []

for lang in Language:
    key, value = list(lang.value.items())[0]
    row = InlineKeyboardButton(text=value, callback_data=f"settings_language_{key}")
    settings_languages_buttons.append(row)

# Группируем по две кнопки в каждой строке
settings_languages_buttons = [settings_languages_buttons[i:i + 2] for i in range(0, len(settings_languages_buttons), 2)]
settings_languages_buttons.append([back_to_settings_button])

router = Router()
dp.include_router(router)


@router.callback_query(lambda callback_query: callback_query.data == 'settings_count_folders_on_page')
async def settings_count_folders_on_page_handler(call: CallbackQuery):
    settings = await get_from_user_collection(call.from_user.id, 'settings')
    folders_on_page_count = settings.get('folders_on_page_count', 4)

    current_inline_markup = get_inline_markup_with_selected_current_setting(
        copy.deepcopy(settings_count_folders_buttons), str(folders_on_page_count)
    )

    new_inline_markup = InlineKeyboardMarkup(row_width=4, inline_keyboard=current_inline_markup)
    new_text = "<b>🗂️ Количество папок на странице:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )
    await call.answer()


@router.callback_query(lambda callback_query: 'settings_count_folders_' in callback_query.data)
async def choose_count_folders_handler(call: aiogram.types.CallbackQuery):
    user_id = call.from_user.id
    folders_on_page_count = call.data.split('_')[-1]

    current_inline_markup = get_inline_markup_with_selected_current_setting(
        copy.deepcopy(settings_count_folders_buttons), folders_on_page_count
    )

    new_inline_markup = InlineKeyboardMarkup(row_width=4, inline_keyboard=current_inline_markup)
    new_text = "<b>🗂️ Количество папок на странице:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )

    settings = await get_from_user_collection(user_id, 'settings')
    settings["folders_on_page_count"] = int(folders_on_page_count)
    await set_to_user_collection(user_id, 'settings', settings)
    await call.answer()


@router.callback_query(lambda callback_query: callback_query.data == 'settings_count_items_on_page')
async def settings_count_items_on_page_handler(call: aiogram.types.CallbackQuery):
    settings = await get_from_user_collection(call.from_user.id, 'settings')
    items_on_page_count = settings.get('items_on_page_count', 4)

    current_inline_markup = get_inline_markup_with_selected_current_setting(
        copy.deepcopy(settings_count_items_buttons), str(items_on_page_count)
    )

    new_inline_markup = InlineKeyboardMarkup(row_width=4, inline_keyboard=current_inline_markup)
    new_text = "<b>📄 Количество записей на странице:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )
    await call.answer()


@router.callback_query(lambda callback_query: 'settings_count_items_' in callback_query.data)
async def choose_count_items_handler(call: aiogram.types.CallbackQuery):
    user_id = call.from_user.id
    items_on_page_count = call.data.split('_')[-1]

    current_inline_markup = get_inline_markup_with_selected_current_setting(
        copy.deepcopy(settings_count_items_buttons), items_on_page_count
    )

    new_inline_markup = InlineKeyboardMarkup(row_width=4, inline_keyboard=current_inline_markup)
    new_text = "<b>📄 Количество записей на странице:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )

    settings = await get_from_user_collection(user_id, 'settings')
    settings["items_on_page_count"] = int(items_on_page_count)
    await set_to_user_collection(user_id, 'settings', settings)
    await call.answer()


@router.callback_query(lambda callback_query: callback_query.data == 'settings_language')
async def settings_language_handler(call: aiogram.types.CallbackQuery):
    settings = await get_from_user_collection(call.from_user.id, 'settings')
    language = settings.get('language', "russian")
    lang_value = get_language_value(language)

    current_inline_markup = get_inline_markup_with_selected_current_setting(
        copy.deepcopy(settings_languages_buttons), lang_value
    )

    new_inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=current_inline_markup)
    new_text = "<b>🌐 Выберите язык интерфейса:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )
    await call.answer()


@router.callback_query(lambda callback_query: 'settings_language_' in callback_query.data)
async def choose_language_handler(call: aiogram.types.CallbackQuery):
    user_id = call.from_user.id
    language = call.data.split('_')[-1]
    lang_value = get_language_value(language)

    current_inline_markup = get_inline_markup_with_selected_current_setting(
        copy.deepcopy(settings_languages_buttons), lang_value
    )

    new_inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=current_inline_markup)
    new_text = "<b>🌐 Выберите язык интерфейса:</b>"

    # Изменение существующего сообщения
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=new_text,
                                reply_markup=new_inline_markup,
                                )

    settings = await get_from_user_collection(user_id, 'settings')
    settings["language"] = language
    await set_to_user_collection(user_id, 'settings', settings)
    await call.answer()


@router.callback_query(lambda callback_query: callback_query.data == 'settings_back')
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
    await callback_query.answer()


@router.callback_query(lambda callback_query: callback_query.data == 'settings_close')
async def close_settings_handler(callback_query: aiogram.types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await callback_query.answer()
    await show_folders(callback_query.from_user.id, need_to_resend=True)


def get_inline_markup_with_selected_current_setting(inline_keyboard, current_value):
    #print(f"current_value {current_value}")
    for row in inline_keyboard:
        for button in row:
            if button.text.replace(CURRENT_LABEL, "").strip() == current_value:
                button.text = button.text.replace(CURRENT_LABEL, "").strip() + f" {CURRENT_LABEL}"
    return inline_keyboard


def get_language_value(setting_language_key):
    for lang in Language:
        if setting_language_key in lang.value:
            return lang.value[setting_language_key]