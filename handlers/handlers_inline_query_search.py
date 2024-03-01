import hashlib

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.handlers_inline_query_share import get_main_inline_markup
from handlers.handlers_item import show_item
from load_all import dp, bot
from models.item_model import Item
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from utils.utils_ import smile_item
from utils.utils_bot import get_bot_name, get_bot_link, to_url_data_item
from utils.utils_folders_reader import get_folders_in_folder
from utils.utils_items_reader import get_folder_items, get_item

router = Router()
dp.include_router(router)


@router.inline_query(lambda query: not query.query.startswith('browse_'))
async def inline_query_search(query: InlineQuery):
    query_data = query.query
    if not query_data:
        return
    print(f'query_data = {query_data}')

    user_id = query.from_user.id

    search_items = await get_search_items(
        user_id=user_id, folder_id=ROOT_FOLDER_ID, text_search=query_data, result_search_items={}
    )
    if not search_items:
        return
    print(f'search_items:\n{search_items}')

    search_results = []
    for item_id in search_items:
        item: Item = await get_item(user_id, item_id)

        if item:
            item_body = item.get_body_markdown()
        else:
            continue

        item_title = item.get_inline_title()

        search_icon_url = f"https://avatars.dzeninfra.ru/get-zen-logos/1526540/pub_621e86861d7c8367c948c8ab_622247ebaf5140641266fc11/xh"

        repost_switch_inline_query = f"browse_{user_id}_{item.id}_-1"
        inline_markup = await get_result_inline_markup(repost_switch_inline_query, query_data)
        result_id = hashlib.md5(item.id.encode()).hexdigest()
        item_body_result = InlineQueryResultArticle(
            id=result_id,
            title=item_title,
            description=item.get_text(),
            input_message_content=InputTextMessageContent(message_text=item_body, parse_mode=ParseMode.MARKDOWN_V2),
            reply_markup=inline_markup,
            thumbnail_url=search_icon_url,
        )
        search_results.append(item_body_result)

    await bot.answer_inline_query(
        query.id,
        results=search_results,
        cache_time=0,
    )


async def get_result_inline_markup(repost_switch_inline_query, query_data):
    bot_name = await get_bot_name()
    bot_link = await get_bot_link()

    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Поделиться",
            switch_inline_query=repost_switch_inline_query
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=f"🚀️ Показать запись {smile_item}",
            url=f"{bot_link}?start={to_url_data_item(repost_switch_inline_query)}",
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🧐 Все результаты поиска 🔍",
            switch_inline_query_current_chat=query_data,
        )
    )

    builder.adjust(2)
    return builder.as_markup()


async def get_search_items(user_id, folder_id, text_search, result_search_items: dict):
    search_items = await get_folder_items(user_id, folder_id, text_search=text_search)
    for search_item in search_items:
        result_search_items[search_item] = search_items[search_item]
    folders_in_folder = await get_folders_in_folder(user_id, folder_id)
    for sub_folder_id in folders_in_folder:
        result_search_items = await get_search_items(user_id, sub_folder_id, text_search, result_search_items)
    return result_search_items
