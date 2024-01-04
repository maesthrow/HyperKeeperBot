import asyncio

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove, User, Chat, CallbackQuery

import handlers_item
import states
from button_manager import create_general_reply_markup, general_buttons_folder, skip_enter_item_title_button, \
    cancel_add_new_item_button
from enums import Environment
from firebase import add_user
from firebase_folder_reader import ROOT_FOLDER_ID, get_current_folder_id
from firebase_folder_writer import set_current_folder
from handlers_folder import create_folder_button, on_delete_folder, show_all_folders, show_folders
from load_all import dp, bot
from models import Item
from utils import get_environment, get_inline_markup_items_in_folder, get_inline_markup_folders
from utils_folders_db import util_get_user_folders, get_folder_path_names
from utils_items import show_all_items


# Используем фильтр CommandStart для команды /start
@dp.message_handler(CommandStart())
async def start(message: aiogram.types.Message, state: FSMContext):
    await state.reset_data()
    await state.reset_state()

    chat_id = message.from_user.id
    tg_user = aiogram.types.User.get_current()
    await add_user(tg_user)

    bot_username = (await bot.me).username

    text = (f"Привет👋, {tg_user.first_name}, давайте начнем! 🚀️\n\nДля Вас создано персональное хранилище, "
            f"которое доступно с помощью команды /storage\n\n"
            f"Управляйте вашими данными 💼, создавайте папки 🗂️ и записи 📄, используя кнопки и подсказки на клавиатуре📱\n\n"
            f"Для доступа ко всем функциям бота жмите на кнопку Меню рядом с полем ввода сообщения ↙️\n\n"
            f"Приятного использования! ☺️")
    await bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())


# Используем фильтр CommandStart для команды /storage
@dp.message_handler(commands=["storage"])
async def storage(message: aiogram.types.Message, state: FSMContext):
    await state.reset_data()
    await state.reset_state()

    tg_user = User.get_current()
    chat = Chat.get_current()
    user_folders = await util_get_user_folders()

    await set_current_folder(tg_user.id, ROOT_FOLDER_ID)

    folder_buttons = [
        await create_folder_button(folder_id, folder_data.get("name"))
        for folder_id, folder_data in user_folders.items()
    ]
    markup = create_general_reply_markup(general_buttons_folder)

    current_folder_path_names = await get_folder_path_names()
    await bot.send_message(chat.id, f"🗂️", reply_markup=markup)
    folders_inline_markup = await get_inline_markup_folders(folder_buttons, 1)

    folders_message = await bot.send_message(chat.id, f"🗂️ <b>{current_folder_path_names}</b>",
                                             reply_markup=folders_inline_markup)

    #load_message = await bot.send_message(chat.id, f"⌛️")
    items_inline_markup = await get_inline_markup_items_in_folder(ROOT_FOLDER_ID, 1)
    if items_inline_markup.inline_keyboard:
        for row in items_inline_markup.inline_keyboard:
            folders_inline_markup.add(*row)
        await folders_message.edit_reply_markup(reply_markup=folders_inline_markup)

    #await bot.delete_message(chat_id=chat.id, message_id=load_message.message_id)
    folders_message.reply_markup = folders_inline_markup
    await dp.storage.update_data(user=tg_user, chat=chat,
                                 data={'current_keyboard': markup, 'folders_message': folders_message,
                                       'page_folders': str(1), 'page_items': str(1)})


@dp.callback_query_handler(text_contains="show_all")
async def show_all_entities_handler(call: CallbackQuery):
    if 'folders' in call.data:
        await show_all_folders()
    elif 'items' in call.data:
        await show_all_items()


@dp.message_handler(Text(equals="️↩️ Назад к общему виду папки"))
async def back_to_folder(message: aiogram.types.Message):
    tg_user = User.get_current()
    folder_id = await get_current_folder_id(tg_user.id)
    await show_folders(folder_id, page_folder=1, page_item=1)


@dp.message_handler(Text(contains="🗑 Удалить"))
async def delete_handler(message: aiogram.types.Message):
    environment = await get_environment()

    if environment == Environment.FOLDERS:
        await on_delete_folder(message)
    elif environment == Environment.ITEM_CONTENT:
        await handlers_item.on_delete_item(message)


@dp.message_handler(~Command(["start", "storage"]))
async def any_message(message: aiogram.types.Message, state: FSMContext):
    buttons = [[skip_enter_item_title_button, cancel_add_new_item_button]]
    inline_markup = InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    add_item_message_1 = await bot.send_message(message.chat.id, "Сейчас сохраним Вашу новую запись 👌",
                                                reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(0.8)
    add_item_message_2 = await bot.send_message(message.chat.id, "Добавьте заголовок:",
                                                reply_markup=inline_markup)
    item = Item(message.text)

    await state.update_data(item=item, add_item_messages=(add_item_message_1, add_item_message_2))

    await states.Item.NewStepTitle.set()

