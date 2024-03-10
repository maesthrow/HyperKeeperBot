import hashlib

from aiogram import Router
from aiogram.enums import ParseMode, ContentType
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardButton, \
    InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.handlers_inline_query_share import update_markup_for_content_mode
from load_all import dp, bot
from models.file_model import File
from models.item_model import Item, INVISIBLE_CHAR
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.utils_ import smile_item, smile_folder
from utils.utils_bot import get_bot_name, get_bot_link, to_url_data
from utils.utils_file_finder import FileFinder
from utils.utils_folders_reader import get_folders_in_folder
from utils.utils_inline_query import get_inline_query_result
from utils.utils_items_reader import get_folder_items, get_item
from utils.utils_search_fragmentator import SearchFragmentator

router = Router()
dp.include_router(router)


@router.inline_query(
    lambda query: not query.query.startswith('browse_')
                  and not query.query.startswith('access_')
                  and not query.query.startswith('folders/')
                  and not query.query.startswith('items/')
                  and not query.query.startswith('files/')
)
async def inline_query_search(query: InlineQuery):
    query_data = query.query
    if not query_data:
        return
    print(f'query_data = {query_data}')

    user_id = query.from_user.id

    search_results_folders = await get_search_results_folders(user_id, query_data)
    search_results_items = await get_search_results_items(user_id, query_data)
    search_results_files = await get_search_results_files(user_id, query_data)

    search_results = []
    search_results.extend(search_results_folders)
    search_results.extend(search_results_items)
    search_results.extend(search_results_files)

    await bot.answer_inline_query(
        query.id,
        results=search_results,
        cache_time=60,
    )


@router.inline_query(lambda query: query.query.startswith('folders/'))
async def inline_query_search_folders(query: InlineQuery):
    query_data = query.query
    user_id = query.from_user.id
    search_results_folders = await get_search_results_folders(user_id, query_data)
    await bot.answer_inline_query(
        query.id,
        results=search_results_folders,
        cache_time=60,
    )


@router.inline_query(lambda query: query.query.startswith('items/'))
async def inline_query_search_items(query: InlineQuery):
    query_data = query.query
    user_id = query.from_user.id
    search_results_items = await get_search_results_items(user_id, query_data)
    await bot.answer_inline_query(
        query.id,
        results=search_results_items,
        cache_time=60,
    )


@router.inline_query(lambda query: query.query.startswith('files/'))
async def inline_query_search_files(query: InlineQuery):
    query_data = query.query
    user_id = query.from_user.id
    search_results_files = await get_search_results_files(user_id, query_data)
    # for result in search_results_files:
    #     print(f'result_id = {result.id}')
    await bot.answer_inline_query(
        query.id,
        results=search_results_files,
        cache_time=60,
    )


async def get_search_results_folders(user_id, query_data):
    search_results = []
    text_search = query_data.replace('folders/', '', 1)
    print(f'query_data folders = {text_search}')

    search_folders = await get_search_folders(
        user_id=user_id, folder_id=ROOT_FOLDER_ID, text_search=text_search, result_search_folders={}
    )
    if not search_folders:
        return search_results

    search_results = []
    for folder_id in search_folders:
        folder_name = search_folders[folder_id]['name']

        search_icon_url = f"https://avatars.dzeninfra.ru/get-zen-logos/1526540/pub_621e86861d7c8367c948c8ab_622247ebaf5140641266fc11/xh"
        # search_icon_url = f"https://cdn-icons-png.flaticon.com/512/3767/3767084.png"
        # search_icon_url = f"https://cdn-icons-png.flaticon.com/512/3979/3979425.png"

        #message_content = InputTextMessageContent(message_text=f'folders/{user_id}|{folder_id}')
        message_content = InputTextMessageContent(message_text=f'{smile_folder} {folder_name}')

        folder_url_data = f'{user_id}_{folder_id}'
        inline_markup = await get_result_inline_markup(query_data, folder_url_data=folder_url_data)

        result_id = hashlib.md5(folder_id.encode()).hexdigest()
        search_folder_result = InlineQueryResultArticle(
            id=result_id,
            title=f'{smile_folder} {folder_name}',
            input_message_content=message_content,
            reply_markup=inline_markup,
            thumbnail_url=search_icon_url,
        )
        search_results.append(search_folder_result)
    return search_results


async def get_search_results_items(user_id, query_data):
    search_results = []
    text_search = query_data.replace('items/', '', 1)
    search_items = await get_search_items(
        user_id=user_id, folder_id=ROOT_FOLDER_ID, text_search=text_search, result_search_items={}
    )
    if not search_items:
        return search_results

    for item_id in search_items:
        item: Item = await get_item(user_id, item_id)

        if item:
            required = SearchFragmentator.get_search_item_fragment_and_page(item, text_search)
            if required:
                search_fragment, page = required
            else:
                search_fragment, page = None, 0
            item_body = item.get_body_markdown(page)
        else:
            continue

        item_title = item.get_inline_title()

        search_icon_url = f"https://avatars.dzeninfra.ru/get-zen-logos/1526540/pub_621e86861d7c8367c948c8ab_622247ebaf5140641266fc11/xh"
        # search_icon_url = f"https://cdn-icons-png.flaticon.com/256/9561/9561874.png"
        # search_icon_url = f"https://cdn-icons-png.flaticon.com/512/11677/11677437.png"

        repost_switch_inline_query = f"browse_{user_id}_{item.id}_-1"
        inline_markup = await get_result_inline_markup(query_data, repost_switch_inline_query=repost_switch_inline_query)
        result_id = hashlib.md5(item.id.encode()).hexdigest()
        search_item_result = InlineQueryResultArticle(
            id=result_id,
            title=f'{smile_item} {item_title}',
            description=search_fragment,  # item.get_text(),
            input_message_content=InputTextMessageContent(message_text=item_body, parse_mode=ParseMode.MARKDOWN_V2),
            reply_markup=inline_markup,
            thumbnail_url=search_icon_url,
        )
        search_results.append(search_item_result)
    return search_results





async def get_search_results_files(user_id, query_data):
    search_results = []
    text_search = query_data.replace('files/', '', 1)
    # if not text_search:
    #     return search_results
    print(f'query_data files = {text_search}')

    search_files = await get_search_files(
        user_id=user_id, folder_id=ROOT_FOLDER_ID, text_search=text_search, result_search_files={}
    )
    if not search_files:
        return search_results

    search_results = []
    for file_id in search_files:
        file: File = search_files[file_id]
        repost_switch_inline_query = f"browse_{user_id}_{file.item_id}_-1"
        inline_markup = await get_result_inline_markup(
            query_data=query_data,
            repost_switch_inline_query=repost_switch_inline_query,
            content_type=file.content_type,
            file_id=file.file_id
        )
        file_info = await FileFinder.get_file_info_in_item_by_file_id(
            user_id, file.item_id, file.content_type, file.file_id
        )
        search_file_result = await get_inline_query_result(
            file.content_type, file.file_id, file_info, inline_markup, text_search
        )
        search_results.append(search_file_result)
    return search_results


async def get_search_folders(user_id, folder_id, text_search, result_search_folders: dict):
    search_folders = await get_folders_in_folder(user_id, folder_id)  # , text_search=text_search)
    for folder_id in search_folders:
        if text_search.lower() in search_folders[folder_id]['name'].lower():
            result_search_folders[folder_id] = search_folders[folder_id]
    folders_in_folder = await get_folders_in_folder(user_id, folder_id)
    for sub_folder_id in folders_in_folder:
        result_search_folders = await get_search_folders(user_id, sub_folder_id, text_search, result_search_folders)
    return result_search_folders


async def get_search_items(user_id, folder_id, text_search, result_search_items: dict):
    search_items = await get_folder_items(user_id, folder_id, text_search=text_search)
    for search_item in search_items:
        result_search_items[search_item] = search_items[search_item]
    folders_in_folder = await get_folders_in_folder(user_id, folder_id)
    for sub_folder_id in folders_in_folder:
        result_search_items = await get_search_items(user_id, sub_folder_id, text_search, result_search_items)
    return result_search_items


async def get_search_files(user_id, folder_id, text_search, result_search_files: dict):
    items = await get_folder_items(user_id, folder_id)
    # print(f'items = {items}')
    for item_id in items:
        # print(f'item_id = {item_id}')
        item: Item = await get_item(user_id, item_id)
        for content_type, files in item.media.items():
            # print(files)
            for file_info in files:
                file_name, caption, is_match = file_is_match(content_type, file_info, text_search)
                if is_match:
                    file_id = FileFinder.get_file_id(file_info)
                    result_search_files[file_id] = File(file_id, content_type, file_name, caption, item_id)

    folders_in_folder = await get_folders_in_folder(user_id, folder_id)
    for sub_folder_id in folders_in_folder:
        result_search_files = await get_search_files(user_id, sub_folder_id, text_search, result_search_files)
    return result_search_files


def file_is_match(content_type: ContentType, file_info, text_search):
    is_match = not text_search
    text_search = text_search.lower()
    caption = file_info['caption'].lower() if file_info['caption'] else None
    file_name = file_info['fields']['file_name'].lower() \
        if file_info['fields'] and 'file_name' in file_info['fields'] and file_info['fields']['file_name'] else None
    if ((caption and text_search in caption)
            or (file_name and text_search in file_name)):
        is_match = True
    if content_type == 'audio':
        if file_info['fields']:
            performer = file_info['fields']['performer'].lower() if ('performer' in file_info['fields']
                                                                     and file_info['fields']['performer']) else None
            title = file_info['fields']['title'].lower() if ('title' in file_info['fields']
                                                             and file_info['fields']['title']) else None
            if ((performer and text_search in performer)
                    or (title and text_search in title)):
                is_match = True
    return file_name, caption, is_match


async def get_result_inline_markup(
        query_data,
        folder_url_data=None,
        repost_switch_inline_query=None,
        content_type: ContentType = None,
        file_id: str = None
):
    bot_link = await get_bot_link()

    builder = InlineKeyboardBuilder()
    search_results_button = InlineKeyboardButton(
                text="🧐 Все результаты 🔍", # 🔍 🔎
                switch_inline_query_current_chat=query_data,
            )

    if repost_switch_inline_query:
        builder.add(
            InlineKeyboardButton(
                text="Поделиться",
                switch_inline_query=repost_switch_inline_query
            )
        )
        builder.add(
            InlineKeyboardButton(
                text=f"🚀️ Показать запись {smile_item}",
                url=f"{bot_link}?start={to_url_data(repost_switch_inline_query)}",
            )
        )
        inline_markup = builder.as_markup()
        if content_type and file_id:
            await update_markup_for_search_file(inline_markup, content_type, file_id)
        inline_markup.inline_keyboard.append([search_results_button])
    else:
        if folder_url_data:
            builder.add(
                InlineKeyboardButton(
                    text=f'Открыть папку {smile_folder}',
                    url=f"{bot_link}?start={to_url_data(folder_url_data)}",
                )
            )
        builder.add(search_results_button)
        inline_markup = builder.as_markup()

    builder.adjust(2)
    return inline_markup


async def update_markup_for_search_file(inline_markup: InlineKeyboardMarkup, content_type: str, file_id):
    query_base = "_".join(inline_markup.inline_keyboard[-1][0].switch_inline_query.split("_")[:4])
    switch_inline_query = f"{query_base}_{content_type}_{file_id}"
    inline_markup.inline_keyboard[-1][0].switch_inline_query = switch_inline_query

    bot_link = await get_bot_link()
    file_data = to_url_data(f'{query_base}_{content_type}_{file_id[16:24]}')
    url = f"{bot_link}?start={file_data}"
    inline_button: InlineKeyboardButton = inline_markup.inline_keyboard[-1][1]
    inline_button.url = url
    bot_name = await get_bot_name()
    inline_button.text = f'{bot_name}'

