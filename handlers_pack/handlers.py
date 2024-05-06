import asyncio
import concurrent.futures
import concurrent.futures
import functools
from typing import List

import aiogram
from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardRemove, User
from aiogram_dialog import DialogManager, ShowMode

from callbacks.callbackdata import ChooseTypeAddText, MessageBoxCallback
from dialogs.giga_chat.keyboards import get_chat_reply_keyboard
from handlers_pack import states
from handlers_pack.filters import NewItemValidateFilter
from handlers_pack.handlers_folder import show_all_folders, show_folders, finalized_inline_markup
from handlers_pack.handlers_item_add_mode import add_files_to_message_handler
from handlers_pack.handlers_read_voice import read_voice_offer
from handlers_pack.handlers_save_item_content import files_to_message_handler, save_text_to_new_item_and_set_title
from handlers_pack.handlers_start_command_with_args import start_url_data_folder_handler, start_url_data_item_handler, \
    start_url_data_file_handler, start_url_data_access_provide_handler
from handlers_pack.states import AccessesState, MainMenuState, SettingsMenuState, GigaChatState
from load_all import bot, dp
from models.folder_model import Folder
from models.item_model import Item
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from mongo_db.mongo_collection_users import has_user
from resources.text_getter import get_text
from utils.data_manager import get_data, set_data, set_any_message_ignore
from utils.utils_ import get_inline_markup_items_in_folder, get_inline_markup_folders, \
    smile_folder
from utils.utils_bot import from_url_data
from utils.utils_button_manager import create_general_reply_markup, general_buttons_movement_item, \
    get_folders_with_items_inline_markup, new_general_buttons_folder, \
    get_folder_pin_inline_markup
from utils.utils_data import set_current_folder_id, get_current_folder_id, add_user_collections, get_current_lang
from utils.utils_folders_reader import get_folder
from utils.utils_handlers import get_folder_path_names
from utils.utils_items import show_all_items
from utils.utils_items_reader import get_folder_id
from utils.utils_sender_message_loop import send_storage_folders, send_storage_with_items

router = Router()
dp.include_router(router)


@router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager, state: FSMContext):
    tg_user = message.from_user
    url_data = from_url_data(message.text).split()
    await start_init(tg_user, message, state, url_data, dialog_manager)


async def start_init(tg_user, message, state, url_data: List[str], dialog_manager: DialogManager):
    is_first_connect = not await has_user(tg_user)
    # Добавляем пользователя и все его коллекции в базу данных, если их еще нет
    if is_first_connect:
        await add_user_collections(tg_user)

    if len(url_data) == 1:
        await start_handler(tg_user, state, dialog_manager, is_first_connect)
    else:
        url_data_args = url_data[1].split('_')
        print(f'url_data_args = {url_data_args}')
        if url_data_args[0].startswith('ap'):
            await start_url_data_access_provide_handler(message, tg_user, state, dialog_manager)
        elif len(url_data_args) == 2:
            await start_url_data_folder_handler(message, tg_user)
        elif 2 < len(url_data_args) <= 4:
            await start_url_data_item_handler(message, tg_user)
        elif len(url_data_args) > 4:
            await start_url_data_file_handler(message, state, tg_user)


async def start_handler(tg_user: User, state: FSMContext, dialog_manager: DialogManager, is_first_connect: bool):
    await state.clear()

    start_message = await bot.send_message(tg_user.id, '🚀️', reply_markup=ReplyKeyboardRemove())

    await dialog_manager.start(
        MainMenuState.Start,
        data={
            'start_message': start_message,
            'is_first_connect': is_first_connect,
        }
    )


@router.message(Command(commands=["access"]))
async def accesses_handler(message: Message, state: FSMContext, dialog_manager: DialogManager):
    start_message = await bot.send_message(message.from_user.id, '🔐', reply_markup=ReplyKeyboardRemove())
    await dialog_manager.start(AccessesState.UsersMenu, data={'start_message': start_message})


@router.message(Command(commands=["gpt"]))
async def gpt_handler(message: Message, state: FSMContext, dialog_manager: DialogManager):
    user_id = dialog_manager.event.from_user.id
    language = await get_current_lang(user_id)
    await set_any_message_ignore(user_id, True)
    reply_keyboard = get_chat_reply_keyboard(language)
    new_chat_title = await get_text(user_id, 'giga_new_chat_title')
    message_text = f'<b>{new_chat_title}</b>'
    try:
        await dialog_manager.done()
    except:
        pass
    await bot.send_message(user_id, message_text, reply_markup=reply_keyboard)
    await dialog_manager.start(GigaChatState.NewChat, show_mode=ShowMode.DELETE_AND_SEND)
    #await asyncio.gather(*tasks)


@router.message(Command(commands=["search"]))
async def inline_search(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuState.LiveSearch)


@router.message(Command(commands=["settings"]))
async def settings_handler(message: aiogram.types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(SettingsMenuState.Menu)


@router.message(Command(commands=["profile"]))
async def profile_handler(message: aiogram.types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuState.UserProfile)


@router.message(Command(commands=["help"]))
async def help_handler(message: aiogram.types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainMenuState.HelpMenu)


@router.message(Command(commands=["storage"]))
async def storage(message: Message, state: FSMContext):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        user_id = message.from_user.id
        folder_id = await get_current_folder_id(user_id)
        folder: Folder = await get_folder(user_id, folder_id)
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
            future = executor.submit(functools.partial(show_storage, message=message, state=state, folder_id=folder_id))
            result = await future.result(timeout=5)


async def show_storage(user_id=None, message: Message = None, state: FSMContext = None, folder_id=ROOT_FOLDER_ID):
    if state:
        await state.clear()

    if not user_id and message:
        user_id = message.from_user.id
    if not user_id:
        return

    data = await get_data(user_id)
    await set_current_folder_id(user_id)

    # если это перемещение записи
    movement_item_id = data.get('movement_item_id')
    movement_item_initial_folder_id = get_folder_id(movement_item_id) if movement_item_id else None

    if movement_item_id:
        general_buttons = general_buttons_movement_item[:]
        if movement_item_initial_folder_id != folder_id:
            general_buttons.insert(0, [KeyboardButton(text="🔀 Переместить в текущую папку")])
    else:
        general_buttons = new_general_buttons_folder[:]

    markup = create_general_reply_markup(general_buttons)

    current_folder_path_names = await get_folder_path_names(user_id, folder_id)

    folders_inline_markup, items_inline_markup = await get_folders_and_items(user_id, folder_id)

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
    folders_inline_markup = finalized_inline_markup(folders_inline_markup, folder_id)

    folders_message = await send_storage_with_items(
        user_id=user_id,
        message=folders_message,
        inline_markup=folders_inline_markup,
        max_attempts=1
    )

    if not folders_inline_markup.inline_keyboard:
        storage_empty_message = await get_text(user_id, 'storage_empty_message')
        await bot.send_message(user_id, text=storage_empty_message)

    data['current_folder_id'] = folder_id
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


@router.message(
    F.via_bot == None,
    F.content_type.in_([
        'photo', 'document', 'video', 'audio', 'voice', 'video_note', 'sticker', 'location', 'contact'
    ]),
    NewItemValidateFilter(),
)
async def media_files_handler(message: Message, state: FSMContext):
    if message.content_type == 'audio':
        print(f'audio {message.audio}')

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
async def message_box_show_handler(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await state.set_state(state=None)
