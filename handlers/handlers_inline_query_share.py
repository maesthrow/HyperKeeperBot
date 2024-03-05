import copy
import hashlib
from typing import Union

import aiogram
from aiogram import types, Router
from aiogram.enums import ParseMode, ContentType
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InlineQueryResultAudio, \
    InlineQueryResultVideo, InlineQueryResultPhoto, InputTextMessageContent, InputMediaAudio, InlineQueryResultArticle, \
    InlineQueryResultVoice, InlineQueryResultDocument, InputMediaDocument, InlineQueryResultCachedSticker, \
    InlineQueryResultLocation, Location, Contact, InlineQueryResultContact, CallbackQuery, InlineQueryResult
from aiogram.utils.keyboard import InlineKeyboardBuilder

import load_all
from callbacks.callbackdata import InlineQueryCallback, SendItemCallback, SwitchInlineQueryCallback, ItemShowCallback
from config import BOT_TOKEN
from load_all import bot, dp
from models.item_model import Item
from mongo_db.mongo_collection_folders import get_user_folders_data
from utils.data_manager import get_data
from utils.utils_ import smile_item
from utils.utils_bot import get_bot_link, get_bot_name, to_url_data_item
from utils.utils_file_finder import FileFinder
from utils.utils_files import dict_to_sticker, dict_to_location, dict_to_contact
from utils.utils_inline_query import get_inline_query_result
from utils.utils_item_show_files import show_item_files
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import escape_markdown

router = Router()
dp.include_router(router)


@router.inline_query(lambda query: len(query.query.split("_")) > 5 and query.query.split("_")[0] == 'browse')
async def inline_query_file(query: Union[types.InlineQuery, types.CallbackQuery]):
    query_data = query.query.split('_')
    author_user_id, item_id, text_page, file_type = int(query_data[1]), query_data[2], query_data[3], query_data[4]
    if file_type == 'video-note':
        file_type = 'video_note'
    file_type = ContentType(file_type)
    file_id = "_".join(query_data[5:])
    print(f"file_type = {file_type}, file_id = {file_id}")
    repost_switch_inline_query = query.query
    bot_name = await get_bot_name()
    bot_link = await get_bot_link()
    file_data = to_url_data_item("_".join(['browse', str(author_user_id), item_id, text_page, file_type, file_id[16:24]]))
    url = f"{bot_link}?start={file_data}"
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Поделиться",
            switch_inline_query=repost_switch_inline_query,
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=bot_name,
            url=url,
        )
    )
    inline_markup_media = builder.as_markup()

    file_info = await FileFinder.get_file_info_in_item_by_short_file_id(author_user_id, item_id, file_type, file_id[16:24])
    result = await get_inline_query_result(file_type, file_id, file_info, inline_markup_media)

    await bot.answer_inline_query(
        query.id,
        results=[result],
        cache_time=60,
    )


@router.inline_query(lambda query: len(query.query.split("_")) <= 5 and query.query.split("_")[0] == 'browse')
async def inline_query(query: Union[types.InlineQuery]):  # , types.CallbackQuery]):
    print(f"query {query.query}")
    if not query.query:
        return
    query_data = query.query.split('_')
    if not query_data or len(query_data) <= 1:
        return

    author_user_id = int(query_data[1])
    item_id = query_data[2]
    text_page = int(query_data[3])

    # if text_page >= 0:
    #     return

    tag = query_data[4] if len(query_data) > 4 else None
    item: Item = Item("", [""])
    print(f'repost_switch_inline_query = f"browse_{author_user_id}_{item.id}_{text_page}"')
    user_id = result_id = 0
    if isinstance(query, types.InlineQuery):
        user_id = query.from_user.id
        item: Item = await get_item(author_user_id, item_id)
        result_id = hashlib.md5(query.query.encode()).hexdigest()

    media_results = []

    if not tag and text_page == -1:
        if item:
            item_body = item.get_body_markdown()
        else:
            item_body = ""
        item_title = item.get_inline_title()

        input_message_content = InputTextMessageContent(message_text=item_body, parse_mode=ParseMode.MARKDOWN_V2)

        # icon_url = (f"https://avatars.mds.yandex.net/i?id=e915ed8674cf1b1719106eef318b439f5f63d37f-"
        #              f"9236004-images-thumbs&ref=rim&n=33&w=250&h=250")
        icon_url = "https://p2.trrsf.com/image/fget/cf/1200/1200/middle/images.terra.com/2023/01/14/1510187297-i612355.jpeg"

        repost_switch_inline_query = f"browse_{author_user_id}_{item.id}_{text_page}"
        inline_markup = await get_main_inline_markup(repost_switch_inline_query)
        item_body_result = InlineQueryResultArticle(
            id=result_id,
            title=f'{smile_item} {item_title}',
            description=item.get_text(),
            input_message_content=input_message_content,
            reply_markup=inline_markup,
            thumbnail_url=icon_url,
        )
        media_results.append(item_body_result)

    bot_name = await get_bot_name()
    bot_link = await get_bot_link()
    builder = InlineKeyboardBuilder()

    repost_switch_inline_query = f"browse_{author_user_id}_{item_id}_{text_page}"

    if tag == 'content':
        builder.add(
            InlineKeyboardButton(
                text=f"🚀️ Показать запись {smile_item}",
                url=f"{bot_link}?start={to_url_data_item(repost_switch_inline_query)}",
                #callback_data=ItemShowCallback(author_user_id=author_user_id, item_id=item_id, with_folders=True).pack()
                #f'item_{item_id}_with-folders',
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🧐 Обзор контента",
                switch_inline_query_current_chat=f"browse_{author_user_id}_{item_id}_{text_page}_content"
            )
        )
    else:
        builder.add(
            InlineKeyboardButton(
                text="Поделиться",
                switch_inline_query=repost_switch_inline_query,
            )
        )
        builder.add(
            InlineKeyboardButton(
                text=bot_name,
                url=f"{bot_link}?start={to_url_data_item(repost_switch_inline_query)}",
            )
        )
    inline_markup_media = builder.as_markup()

    # print(f'to_url_data_item(repost_switch_inline_query) = {to_url_data_item(repost_switch_inline_query)}')

    if item.pages_count() > 1 or item.files_count() > 0:
        await create_text_results(
            item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag, text_page=text_page
        )
    if text_page == -1:
        await create_document_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_photo_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_audio_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_voice_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_video_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_video_note_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_sticker_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_location_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)
        await create_contact_results(item=item, media_results=media_results, inline_markup=inline_markup_media, tag=tag)

    # если только 1 результат, который для всей записи (со значком телеги),
    # то удаляем из клавиатуры кнопку "🧐 Обзор контента 📲"
    if not tag and text_page == -1 and len(media_results) == 1:
        media_results[0].reply_markup.inline_keyboard.pop(-1)

    await bot.answer_inline_query(
        query.id,
        results=media_results,
        cache_time=120,
    )


async def get_main_inline_markup(repost_switch_inline_query):
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
            text=f"💾 {bot_name}",
            url=f"{bot_link}?start={to_url_data_item(repost_switch_inline_query)}",
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🧐 Обзор контента 📲",
            switch_inline_query_current_chat=f'{repost_switch_inline_query}_content',
        )
    )

    builder.adjust(2)
    return builder.as_markup()


def rewrite_path_by_page(path, page):
    print(f'path = {path}')
    return f'{'_'.join(path.split('_')[:-1])}_{page}'


async def create_text_results(item: Item, media_results: list, inline_markup, tag, text_page):
    this_inline_markup = copy.deepcopy(inline_markup)

    if text_page == -1:
        for page in range(len(item.text)):
            if not item.get_text(page):
                continue
            await create_text_result_for_page(item, media_results, this_inline_markup, tag, page)
    else:
        await create_text_result_for_page(item, media_results, this_inline_markup, tag, text_page)

    return media_results


async def create_text_result_for_page(item: Item, media_results: list, inline_markup, tag, page):
    if tag != 'content':
        rp_button: InlineKeyboardButton = inline_markup.inline_keyboard[-1][0]
        hk_button: InlineKeyboardButton = inline_markup.inline_keyboard[-1][1]
        rp_button.switch_inline_query = rewrite_path_by_page(rp_button.switch_inline_query, page)
        print(f'new_path = {rp_button.switch_inline_query}')
        hk_button.url = rewrite_path_by_page(hk_button.url, page)
        print(f'new_path = {hk_button.url}')

    input_text_message_content = InputTextMessageContent(
        message_text=item.get_body_markdown(page),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    result_id = hashlib.md5(f'{item.title}_{page}'.encode()).hexdigest()
    display_page = page + 1
    title_pages = f'{display_page} из {len(item.text)}'
    item_text_result = InlineQueryResultArticle(
        id=result_id,
        title=title_pages,
        description=item.get_text(page),
        input_message_content=input_text_message_content,
        reply_markup=copy.deepcopy(inline_markup),
    )
    media_results.append(item_text_result)


async def update_markup_for_content_mode(inline_markup: InlineKeyboardMarkup, content_type: str, file_id):
    query_base = "_".join(inline_markup.inline_keyboard[-1][0].switch_inline_query.split("_")[:4])
    switch_inline_query = f"{query_base}_{content_type}_{file_id}"
    inline_markup.inline_keyboard[-1][0].switch_inline_query = switch_inline_query

    bot_link = await get_bot_link()
    file_data = to_url_data_item(f'{query_base}_{content_type}_{file_id[16:24]}')
    print(f'switch_inline_query {switch_inline_query}\nfile_data {file_data}')
    url = f"{bot_link}?start={file_data}"
    inline_button: InlineKeyboardButton = inline_markup.inline_keyboard[-1][1]
    inline_button.url = url
    print(f'inline_button.url = {url}')


async def create_document_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['document']:
        caption = escape_markdown(file_info['caption'])
        file_id = FileFinder.get_file_id(file_info)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='document',
                file_id=file_id
            )

        file_name = file_info['fields'].get('file_name')
        mime_type = file_info['fields'].get('mime_type') or 'application/octet-stream'
        result = InlineQueryResultDocument(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            title=file_name,
            document_url=file_id,
            caption=caption,
            description=caption,
            mime_type=mime_type,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results


async def create_photo_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['photo']:
        caption = escape_markdown(file_info['caption'])
        file_id = FileFinder.get_file_id(file_info)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='photo',
                file_id=file_id
            )

        media_results.append(
            InlineQueryResultPhoto(
                id=hashlib.md5(file_id.encode()).hexdigest(),
                photo_url=file_id,
                thumb_url=file_id,
                thumbnail_url=file_id,
                title=caption,
                description=caption,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=this_inline_markup,
            )
        )

    return media_results


async def create_audio_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['audio']:
        caption = escape_markdown(file_info['caption'])
        file_id = FileFinder.get_file_id(file_info)
        file: InputMediaAudio = await bot.get_file(file_id)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='audio',
                file_id=file_id
            )

        result = InlineQueryResultAudio(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            audio_url=file_id,
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results


async def create_voice_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['voice']:
        caption = escape_markdown(file_info['caption'])
        file_id = FileFinder.get_file_id(file_info)
        file = await bot.get_file(file_id)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='voice',
                file_id=file_id
            )

        result = InlineQueryResultVoice(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            voice_url=file_id,
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results


async def create_video_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['video']:
        caption = escape_markdown(file_info['caption'])
        file_id = FileFinder.get_file_id(file_info)
        file = await bot.get_file(file_id)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='video',
                file_id=file_id
            )

        result = InlineQueryResultVideo(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            video_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            mime_type='video/mp4',
            title=file.file_path,
            description=caption,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results


async def create_video_note_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['video_note']:
        caption = escape_markdown(file_info['caption'])
        file_id = FileFinder.get_file_id(file_info)
        file = await bot.get_file(file_id)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='video-note',
                file_id=file_id
            )

        result = InlineQueryResultVideo(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            video_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            mime_type='video/mp4',
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results


async def create_sticker_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['sticker']:
        file_id = FileFinder.get_file_id(file_info)
        sticker = await bot.get_file(file_id)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='sticker',
                file_id=file_id
            )

        result = InlineQueryResultCachedSticker(
            id=hashlib.md5(sticker.file_id.encode()).hexdigest(),
            sticker_file_id=sticker.file_id,
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results


async def create_location_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['location']:
        file_id = file_info['file_id']
        location_dict = file_info['fields']
        location: Location = dict_to_location(location_dict)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='location',
                file_id=file_id
            )

        result = InlineQueryResultLocation(
            id=hashlib.md5((str(location.latitude) + str(location.longitude)).encode()).hexdigest(),
            latitude=location.latitude,
            longitude=location.longitude,
            title="📍",
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results


async def create_contact_results(item: Item, media_results: list, inline_markup, tag):
    for file_info in item.media['contact']:
        file_id = file_info['file_id']
        contact_dict = file_info['fields']
        contact: Contact = dict_to_contact(contact_dict)

        this_inline_markup = copy.deepcopy(inline_markup)
        if tag != 'content':
            await update_markup_for_content_mode(
                this_inline_markup,
                content_type='contact',
                file_id=file_id
            )

        result = InlineQueryResultContact(
            id=hashlib.md5(contact.phone_number.encode()).hexdigest(),
            phone_number=contact.phone_number,
            first_name=contact.first_name,
            last_name=contact.last_name,
            vcard=contact.vcard,
            reply_markup=this_inline_markup
        )
        media_results.append(result)
    return media_results
