import asyncio
import concurrent.futures
import functools
from typing import List

import aiogram
from aiogram import Router, F
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, KeyboardButton, Message, ReplyKeyboardRemove, Location, \
    Contact
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import ChooseTypeAddText, MessageBoxCallback
from handlers import states
from handlers.filters import NewItemValidateFilter
from handlers.handlers_folder import show_all_folders, show_folders
from handlers.handlers_item import show_item
from handlers.handlers_item_add_mode import add_files_to_message_handler
from handlers.handlers_read_voice import read_voice_offer
from handlers.handlers_save_item_content import files_to_message_handler, save_text_to_new_item_and_set_title, \
    text_to_message_handler
from load_all import dp, bot
from models.folder_model import Folder
from models.item_model import Item
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.data_manager import get_data, set_data
from utils.utils_ import get_inline_markup_items_in_folder, get_inline_markup_folders, get_folder_path_names, \
    smile_item, smile_folder, smile_file
from utils.utils_bot import from_url_data
from utils.utils_button_manager import create_general_reply_markup, general_buttons_movement_item, \
    get_folders_with_items_inline_markup, save_file_buttons, new_general_buttons_folder, \
    get_folder_pin_inline_markup
from utils.utils_data import set_current_folder_id, get_current_folder_id, add_user_collections
from utils.utils_file_finder import FileFinder
from utils.utils_files import dict_to_location, dict_to_contact
from utils.utils_folders_reader import get_folder
from utils.utils_items import show_all_items
from utils.utils_items_reader import get_folder_id
from utils.utils_sender_message_loop import send_storage_folders, send_storage_with_items
from utils.utils_show_item_entities import show_item_page_as_text_only, show_item_full_mode

router = Router()
dp.include_router(router)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    tg_user = message.from_user
    url_data = from_url_data(message.text).split()
    await start_init(tg_user, message, state, url_data)


async def start_init(tg_user, message, state, url_data: List[str]):
    if len(url_data) == 1:
        await start_handler(state, tg_user)
    else:
        if len(url_data[1].split('_')) == 2:
            await start_url_data_folder_handler(message, tg_user)
        elif 2 < len(url_data[1].split('_')) <= 4:
            await start_url_data_item_handler(message, tg_user)
        elif len(url_data[1].split('_')) > 4:
            await start_url_data_file_handler(message, state, tg_user)


async def start_handler(state: FSMContext, tg_user):
    await state.clear()

    # Добавляем пользователя и все его коллекции в базу данных, если их еще нет
    await add_user_collections(tg_user)

    # me = await bot.me()
    # bot_username = me.username
    text = (f"👋 Привет, {tg_user.first_name}, давайте начнем! 🚀️\n\nДля вас создано персональное хранилище, "
            f"которое доступно с помощью команды /storage\n\n"
            f"Управляйте вашими данными 🗃️, создавайте папки 🗂️ и записи 📄, сохраняйте медиафайлы 📸, "
            f"используя кнопки и подсказки на клавиатуре📱\n\n"
            f"Для доступа ко всем функциям бота жмите на кнопку 'Меню' рядом с полем ввода сообщения ↙️\n\n"
            f"Приятного использования! ☺️")
    await bot.send_message(tg_user.id, text, reply_markup=ReplyKeyboardRemove())


async def start_url_data_folder_handler(message, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        # await start_handler(message, state, tg_user)
        url_data = from_url_data(message.text).split()[1]
        url_data_split = url_data.split('_')
        author_user_id = int(url_data_split[0])
        folder_id = url_data_split[1]

        if author_user_id == tg_user.id:
            await show_folders(user_id=tg_user.id, current_folder_id=folder_id, need_to_resend=True)
        else:
            author_user_chat_member = await bot.get_chat_member(author_user_id, author_user_id)
            print(f'author_user = {author_user_chat_member.user}')
            await bot.send_message(
                tg_user.id,
                f"Папка, которую вы пытаетесь открыть, "
                f"принадлежит пользователю @{author_user_chat_member.user.username}"
                f"\n\nВы можете запросить у него доступ к этой папке {smile_folder}🔑"
            )

        data = await get_data(tg_user.id)
        await asyncio.sleep(0.5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)

    else:
        await bot.delete_message(tg_user.id, message.message_id)


async def start_url_data_item_handler(message, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        # await start_handler(message, state, tg_user)
        url_data = from_url_data(message.text).split()[1]
        url_data_split = url_data.split('_')
        author_user_id = int(url_data_split[1])
        item_id = url_data_split[2]
        page = int(url_data_split[3])
        if page == -1:
            if author_user_id != tg_user.id:
                await show_item_full_mode(
                    user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id
                )
            else:
                folder_id = get_folder_id(item_id)
                await show_folders(user_id=tg_user.id, current_folder_id=folder_id, need_to_resend=True)
                await show_item(tg_user.id, item_id)
        else:
            await show_item_page_as_text_only(
                user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id, page=page
            )

        data = await get_data(tg_user.id)
        await asyncio.sleep(0.5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)

    else:
        await bot.delete_message(tg_user.id, message.message_id)


async def start_url_data_file_handler(message, state, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    print(f"author_user_id {author_user_id}")
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        # await start_handler(message, state, tg_user)

        url_data = from_url_data(message.text).split()[1]
        print(f"url_data = {url_data}")
        url_data_split = url_data.split('_')

        author_user_id = int(url_data_split[1])
        item_id = url_data_split[2]
        page = int(url_data_split[3])
        short_file_id = url_data[-8:]
        str_content_type = url_data[:-8].split('_')[-2]
        if str_content_type == 'video-note':
            str_content_type = 'video_note'
        file_type: ContentType = ContentType(str_content_type)
        file_info = await FileFinder.get_file_info_in_item_by_short_file_id(author_user_id, item_id, file_type,
                                                                            short_file_id)
        file_id = FileFinder.get_file_id(file_info)
        caption = file_info['caption']

        inline_markup = InlineKeyboardMarkup(inline_keyboard=save_file_buttons)

        if file_type == 'document':
            await bot.send_document(chat_id=tg_user.id, document=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'photo':
            await bot.send_photo(chat_id=tg_user.id, photo=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'audio':
            await bot.send_audio(chat_id=tg_user.id, audio=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'voice':
            await bot.send_voice(chat_id=tg_user.id, voice=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'video':
            await bot.send_video(chat_id=tg_user.id, video=file_id, caption=caption, reply_markup=inline_markup)
        elif file_type == 'video_note':
            await bot.send_video_note(chat_id=tg_user.id, video_note=file_id, reply_markup=inline_markup)
        elif file_type == 'sticker':
            await bot.send_sticker(chat_id=tg_user.id, sticker=file_id, reply_markup=inline_markup)
        elif file_type == 'location':
            location: Location = dict_to_location(file_info['fields'])
            await bot.send_location(
                chat_id=tg_user.id,
                latitude=location.latitude,
                longitude=location.longitude,
                horizontal_accuracy=location.horizontal_accuracy,
                live_period=location.live_period,
                heading=location.heading,
                proximity_alert_radius=location.proximity_alert_radius,
                reply_markup=inline_markup
            )
        elif file_type == 'contact':
            contact: Contact = dict_to_contact(file_info['fields'])
            await bot.send_contact(
                chat_id=tg_user.id,
                phone_number=contact.phone_number,
                first_name=contact.first_name,
                last_name=contact.last_name,
                vcard=contact.vcard,
                reply_markup=inline_markup
            )
            # await bot.send_contact(chat_id=tg_user.id, latitude=None, longitude=None, reply_markup=inline_markup)

        await asyncio.sleep(0.5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)
    else:
        await bot.delete_message(tg_user.id, message.message_id)


@router.message(Command(commands=["search"]))
async def inline_search(message: Message, state: FSMContext):
    bot_username = (await message.bot.get_me()).username
    prompt_text = "\n*Вводите запрос для поиска по хранилищу из любого чата, используя инлайн режим\\:*" \
                  "\n\nГлобальный поиск 🌐" \
                  f"\n'@{bot_username} _ваш\\_запрос'_" \
                  f"\n\nПоиск папок {smile_folder} \\(только в чате с ботом\\)" \
                  f"\n'@{bot_username} folders/_ваш\\_запрос_'" \
                  f"\n\nПоиск записей {smile_item}" \
                  f"\n'@{bot_username} items/_ваш\\_запрос_'" \
                  f"\n\nПоиск файлов {smile_file}" \
                  f"\n'@{bot_username} files/_ваш\\_запрос_'" \
                  "\n\nЛибо используйте кнопки ⬇️"

    builder = InlineKeyboardBuilder()
    builder.button(text=f"🔍 Глобальный поиск 🌐", switch_inline_query_current_chat="")
    builder.button(text=f"🔍 Поиск папок {smile_folder}", switch_inline_query_current_chat="folders/")
    builder.button(text=f"🔍 Поиск записей {smile_item}", switch_inline_query_current_chat="items/")
    builder.button(text=f"🔍 Поиск файлов {smile_file}", switch_inline_query_current_chat="files/")
    builder.button(text="✖️ Закрыть", callback_data=MessageBoxCallback(result='cancel').pack())
    builder.adjust(1)
    await message.answer(
        text=prompt_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=builder.as_markup())
    await bot.delete_message(message.from_user.id, message.message_id)


@router.message(Command(commands=["storage"]))
async def storage(message: Message, state: FSMContext):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        user_id = message.from_user.id
        folder: Folder = await get_folder(user_id)
        pin = folder.get_pin() if folder else None
        if pin:
            inline_markup = get_folder_pin_inline_markup(user_id, pin=pin)
            await bot.send_message(
                chat_id=user_id,
                text=f'_Введите текущий PIN\-код для папки:_\n\n{smile_folder} {folder.name}',
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=inline_markup
            )
        else:
            future = executor.submit(functools.partial(show_storage, message, state))
            result = await future.result(timeout=5)


async def show_storage(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id

    data = await get_data(user_id)
    await set_current_folder_id(user_id)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    movement_item_initial_folder_id = get_folder_id(movement_item_id) if movement_item_id else None

    if movement_item_id:
        general_buttons = general_buttons_movement_item[:]
        if movement_item_initial_folder_id != ROOT_FOLDER_ID:
            general_buttons.insert(0, [KeyboardButton(text="🔀 Переместить в текущую папку")])
    else:
        general_buttons = new_general_buttons_folder[:]

    markup = create_general_reply_markup(general_buttons)

    current_folder_path_names = await get_folder_path_names(user_id)

    folders_inline_markup, items_inline_markup = await get_folders_and_items(user_id, ROOT_FOLDER_ID)

    await bot.send_message(user_id, f"🗂️", reply_markup=markup)
    folders_message: Message
    folders_message = await bot.send_message(user_id, "⏳")
    # await asyncio.sleep(0.3)
    folders_message = await send_storage_folders(
        user_id=user_id,
        message=folders_message,
        text=f"🗂️ <b>{current_folder_path_names}</b>",
        inline_markup=folders_inline_markup,
        max_attempts=5
    )
    # folders_message = await asyncio.wait_for(folders_message.edit_text(
    #     text=f"🗂️ <b>{current_folder_path_names}</b>",
    #     reply_markup=folders_inline_markup,
    # ), timeout=1)

    if items_inline_markup.inline_keyboard:
        folders_inline_markup = get_folders_with_items_inline_markup(folders_inline_markup, items_inline_markup)
        # await folders_message.edit_reply_markup(reply_markup=folders_inline_markup)

    print(f"len {len(folders_inline_markup.inline_keyboard)}\n{folders_inline_markup.inline_keyboard}")

    folders_message = await send_storage_with_items(
        user_id=user_id,
        message=folders_message,
        inline_markup=folders_inline_markup,
        max_attempts=1
    )
    # await asyncio.sleep(0.3)
    #print(len(folders_message.reply_markup.inline_keyboard))
    data['folders_message'] = folders_message
    data['current_keyboard'] = markup
    data['page_folders'] = str(1)
    data['page_items'] = str(1)
    data['item_id'] = None
    data['dict_search_data'] = None
    await set_data(user_id, data)


async def get_folders_and_items(user_id, root_folder_id):
    # Вызов двух асинхронных функций параллельно и ожидание результатов
    folders_inline_markup_task = get_inline_markup_folders(user_id, root_folder_id, 1)
    items_inline_markup_task = get_inline_markup_items_in_folder(user_id, root_folder_id, 1)

    # Ожидание завершения обоих задач
    folders_inline_markup = await folders_inline_markup_task
    items_inline_markup = await items_inline_markup_task

    return folders_inline_markup, items_inline_markup


@router.callback_query(F.data.contains("storage_show_all"))
async def show_all_entities_handler(call: CallbackQuery):
    user_id = call.from_user.id
    if 'folders' in call.data:
        await show_all_folders(user_id, need_resend=True)
    elif 'items' in call.data:
        await show_all_items(user_id, need_to_resend=False)
    await call.answer()


@router.message(F.text == "↪️ Перейти к общему виду папки 🗂️📄")
async def back_to_folder(message: aiogram.types.Message):
    folder_id = await get_current_folder_id(message.from_user.id)
    await show_folders(message.from_user.id, folder_id, page_folder=1, page_item=1, need_to_resend=True)


@router.message(NewItemValidateFilter(), F.via_bot == None, F.content_type == 'text')
async def any_message(message: Message, state: FSMContext):
    await text_to_message_handler(message, state)


# @router.message(NotEditFileCaptionFilter(), F.via_bot, F.text.startswith('folders/'))  # NotAddToFilter(),
# async def search_folder_result_message(message: Message, state: FSMContext):
#     message_data = message.text.replace('folders/', '', 1)
#     author_user_id, folder_id = message_data.split('|')
#     author_user_id = int(author_user_id)
#     if author_user_id == message.from_user.id:
#         await show_folders(user_id=author_user_id, current_folder_id=folder_id, need_to_resend=True)


@router.callback_query(states.ItemState.ChooseTypeAddTextToNewItem, ChooseTypeAddText.filter())
async def add_text_to_new_item_handler(call: CallbackQuery, state: FSMContext):
    callback_data: ChooseTypeAddText = ChooseTypeAddText.unpack(call.data)
    is_new_page = callback_data.type == 'new_page'
    data = await state.get_data()
    item: Item = data.get('item')
    messages = data.get('text_messages', [])
    await save_text_to_new_item_and_set_title(state=state, item=item, messages=messages, is_new_page=is_new_page)
    await call.answer()


@router.message(F.via_bot == None, F.content_type.in_(
    ['photo', 'document', 'video', 'audio', 'voice', 'video_note', 'sticker', 'location', 'contact']
))
async def media_files_handler(message: Message, state: FSMContext):
    IS_PREMIUM = True
    if (IS_PREMIUM and
            (message.content_type == 'voice' or message.content_type == 'video_note')):
        await state.update_data(voice_message=message)
        await read_voice_offer(message)
        return

    state_value = await state.get_state()
    func = add_files_to_message_handler if state_value == states.ItemState.AddTo else files_to_message_handler

    data = await state.get_data()
    file_messages = data.get('file_messages', [])
    file_messages.append(message)
    if message.media_group_id:
        await state.update_data(file_messages=file_messages)
        if len(file_messages) == 1:
            await func(file_messages, state)
    else:
        await func(file_messages, state)


@router.callback_query(MessageBoxCallback.filter())
async def message_box_show_handler(call: CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
