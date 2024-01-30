import hashlib
from typing import Union

import aiogram
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InlineQueryResultAudio, \
    InlineQueryResultVideo, InlineQueryResultPhoto, InputTextMessageContent, InputMediaAudio, InlineQueryResultArticle, \
    InlineQueryResultVoice, InlineQueryResultDocument, InputMediaDocument, InlineQueryResultCachedSticker, \
    InlineQueryResultLocation, Location, Contact, InlineQueryResultContact, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import load_all
from callbacks.callbackdata import InlineQueryCallback, SendItemCallback
from config import BOT_TOKEN
from load_all import bot, dp
from models.item_model import Item
from mongo_db.mongo_collection_folders import get_user_folders_data
from utils.data_manager import get_data
from utils.utils_bot import get_bot_link, get_bot_name, to_url_data_item
from utils.utils_files import dict_to_sticker, dict_to_location, dict_to_contact
from utils.utils_item_show_files import show_item_files
from utils.utils_items_reader import get_item

router = Router()
dp.include_router(router)


@router.inline_query(lambda query: True)
#@router.callback_query(InlineQueryCallback.filter())
async def inline_query(query: Union[types.InlineQuery, types.CallbackQuery]):
    print(f"query {query.query}")
    query_data = query.query.split('_')
    author_user_id = int(query_data[0])
    item_id = query_data[1]
    item: Item = Item("", "")
    user_id = 0
    result_id = 0
    if isinstance(query, types.InlineQuery):
        user_id = query.from_user.id
        #data = await get_data(user_id)
        #item: Item = data.get('current_item')  # load_all.current_item.get(user_id)
        item: Item = await get_item(author_user_id, item_id)
        result_id = hashlib.md5(query.query.encode()).hexdigest()
    # elif isinstance(query, types.CallbackQuery):
    #     data_parts = query.data.split(":")
    #     action = data_parts[1]
    #     autor_user_id = int(data_parts[2])
    #     item_id = data_parts[3]
    #     item: Item = await get_item(autor_user_id, item_id)
    #     user_id = query.from_user.id
    #     data_str = f"{user_id}"
    #     result_id = hashlib.md5(data_str.encode()).hexdigest()

        #item = await get_item(user_id, item_id)
    #print(f"user_id {user_id}\nitem {item}")
    if item:
        item_body = await item.get_body()
    else:
        item_body = "пусто"
    item_title = item.get_inline_title()
    # file_id = await item.get_all_media_values()[0]
    input_message_content = InputTextMessageContent(message_text=item_body, parse_mode=ParseMode.HTML)

    photo_url = (f"https://avatars.mds.yandex.net/i?id=e915ed8674cf1b1719106eef318b439f5f63d37f-"
                 f"9236004-images-thumbs&ref=rim&n=33&w=250&h=250")

    media_results = []

    # item_button = InlineKeyboardButton(text="Поделиться", switch_inline_query_current_chat=result_id)
    inline_markup = await get_main_inline_markup(user_id, author_user_id, item, result_id)
    media_results.append(
        InlineQueryResultArticle(
            id=result_id,
            title=item_title,
            description=item.text,
            input_message_content=input_message_content,
            reply_markup=inline_markup,
            thumbnail_url=photo_url
        )
    )

    repost_switch_inline_query = f"{author_user_id}_{item.id}"
    bot_name = await get_bot_name()
    bot_link = await get_bot_link()
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
            url=bot_link
        )
    )
    inline_markup_media = builder.as_markup()
    # media_button = InlineKeyboardButton(text="Показать следующую", switch_inline_query_current_chat=result_id)
    #inline_markup_media = InlineKeyboardMarkup(inline_keyboard=[[media_button]])
    await create_document_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_photo_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_audio_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_voice_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_video_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_video_note_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_sticker_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_location_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_contact_results(item=item, media_results=media_results, inline_markup=inline_markup_media)

    await bot.answer_inline_query(
        query.id,
        results=media_results,
        cache_time=0,
    )


async def get_main_inline_markup(user_id, author_user_id, item: Item, result_id):
    repost_switch_inline_query = f"{author_user_id}_{item.id}"
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
            text=bot_name,
            url=f"{bot_link}?start={to_url_data_item(repost_switch_inline_query)}",
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="📑 Показать весь контент",
            switch_inline_query_current_chat=repost_switch_inline_query,
        )
    )

    builder.adjust(2)
    return builder.as_markup()


# @router.callback_query(InlineQueryCallback.filter())
# async def show_hide_files_handler(call: CallbackQuery):
#     await call.answer()
#     print(f"call_message {call.message}")
#     message = await bot.edit_message_text(text="sss", inline_message_id=call.inline_message_id)
#     print(f"message {message}")
#     current_chat_id = call.from_user.id
#
#     data_parts = call.data.split(":")
#     action = data_parts[1]
#     autor_user_id = int(data_parts[2])
#     item_id = data_parts[3]
#     item: Item = await get_item(autor_user_id, item_id)
#
#     #await show_item_files(current_chat_id, item)


async def create_document_results(item: Item, media_results: list, inline_markup):
    for file_info in item.media['document']:
        # print(f"item.media[document] = {item.media['document']}")
        file_id = file_info.get('file_id')
        file_name = file_info.get('file_name')
        mime_type = file_info.get('mime_type')
        result = InlineQueryResultDocument(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            title=file_name,
            document_url=file_id,
            mime_type=mime_type,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_photo_results(item: Item, media_results: list, inline_markup):
    item_title = item.get_inline_title()
    for file_id in item.media['photo']:
        result = InlineQueryResultPhoto(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            photo_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            title=item_title,
            # description=item.text,
            # caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_audio_results(item: Item, media_results: list, inline_markup):
    for file_id in item.media['audio']:
        file: InputMediaAudio = await bot.get_file(file_id)
        # file = await bot.get_file(file_id)
        result = InlineQueryResultAudio(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            audio_url=file_id,
            title=file.file_path,
            # caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_voice_results(item: Item, media_results: list, inline_markup):
    for file_id in item.media['voice']:
        file = await bot.get_file(file_id)
        result = InlineQueryResultVoice(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            voice_url=file_id,
            title=file.file_path,
            # caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_video_results(item: Item, media_results: list, inline_markup):
    for file_id in item.media['video']:
        file = await bot.get_file(file_id)
        result = InlineQueryResultVideo(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            video_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            mime_type='video/mp4',
            title=file.file_path,
            # description=item.text,
            # caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_video_note_results(item: Item, media_results: list, inline_markup):
    for file_id in item.media['video_note']:
        file = await bot.get_file(file_id)
        result = InlineQueryResultVideo(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            video_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            mime_type='video/mp4',
            title=file.file_path,
            # caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_sticker_results(item: Item, media_results: list, inline_markup):
    for sticker_dict in item.media['sticker']:
        sticker = await bot.get_file(sticker_dict.get("file_id"))
        result = InlineQueryResultCachedSticker(
            id=hashlib.md5(sticker.file_id.encode()).hexdigest(),
            sticker_file_id=sticker.file_id,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_location_results(item: Item, media_results: list, inline_markup):
    for location_dict in item.media['location']:
        location: Location = dict_to_location(location_dict)
        result = InlineQueryResultLocation(
            id=hashlib.md5((str(location.latitude) + str(location.longitude)).encode()).hexdigest(),
            latitude=location.latitude,
            longitude=location.longitude,
            title="📍",
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_contact_results(item: Item, media_results: list, inline_markup):
    for contact_dict in item.media['contact']:
        contact: Contact = dict_to_contact(contact_dict)
        result = InlineQueryResultContact(
            id=hashlib.md5(contact.phone_number.encode()).hexdigest(),
            phone_number=contact.phone_number,
            first_name=contact.first_name,
            last_name=contact.last_name,
            vcard=contact.vcard,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results
