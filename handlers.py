import asyncio

import aiogram
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, CommandStart, Text
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardRemove

import states
from button_manager import create_general_reply_markup, general_buttons_folder, skip_enter_item_title_button, \
    cancel_add_new_item_button
from firebase import add_user
from firebase_folder_reader import ROOT_FOLDER_ID, get_user_folders, get_folder_path_names
from firebase_folder_writer import set_current_folder
from handlers_folder import create_folder_button, on_delete_folder
from load_all import dp, bot
from utils import get_environment, get_inline_markup_items_in_folder, get_inline_markup_folders
from enums import Environment
from models import Item

import handlers_item


# Используем фильтр CommandStart для команды /start
@dp.message_handler(CommandStart())
async def start(message: aiogram.types.Message, state: FSMContext):
    await state.reset_data()
    await state.reset_state()

    chat_id = message.from_user.id
    tg_user = aiogram.types.User.get_current()
    await add_user(tg_user)

    bot_username = (await bot.me).username

    text = (f"Привет👋, {tg_user.first_name}, давайте начнем! 🚀️\n\nДля Вас создано персональное хранилище 🗂️, "
            f"которое доступно с помощью команды /storage\n\n"
            f"Управляйте вашими данными 💼, создавайте папки 📁 и записи 📄, используя кнопки и подсказки на клавиатуре📱\n\n"
            f"Для доступа ко всем функциям бота жмите на кнопку Меню рядом с полем ввода сообщения ↙️\n\n"
            f"Приятного использования! ☺️")
    await bot.send_message(chat_id, text, reply_markup=ReplyKeyboardRemove())


# Используем фильтр CommandStart для команды /storage
@dp.message_handler(commands=["storage"])
async def storage(message: aiogram.types.Message, state: FSMContext):
    await state.reset_data()
    await state.reset_state()

    tg_user = aiogram.types.User.get_current()
    chat = aiogram.types.Chat.get_current()
    user_folders = await get_user_folders(tg_user.id)

    await set_current_folder(tg_user.id, ROOT_FOLDER_ID)

    folder_buttons = [
        await create_folder_button(folder_id, folder_data.get("name"))
        for folder_id, folder_data in user_folders.items()
    ]

    markup = create_general_reply_markup(general_buttons_folder)
    await state.update_data(current_keyboard=markup)
    await dp.storage.update_data(user=tg_user, chat=message.chat, data={'current_keyboard': markup})

    current_folder_path_names = await get_folder_path_names(tg_user.id)
    await bot.send_message(chat.id, f"🗂️ <b>{current_folder_path_names}</b>", reply_markup=markup)
    folders_inline_markup = get_inline_markup_folders(folder_buttons)
    if folders_inline_markup.inline_keyboard:
        await bot.send_message(message.chat.id, f"⬇️ Папки", reply_markup=folders_inline_markup)
    load_message = await bot.send_message(chat.id, f"⌛️")
    items_inline_markup = await get_inline_markup_items_in_folder(ROOT_FOLDER_ID)
    if items_inline_markup.inline_keyboard:
        await bot.send_message(message.chat.id, f"⬇️ Записи", reply_markup=items_inline_markup)
    await bot.delete_message(chat_id=chat.id, message_id=load_message.message_id)


@dp.message_handler(Text(equals="🗑 Удалить"))
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

