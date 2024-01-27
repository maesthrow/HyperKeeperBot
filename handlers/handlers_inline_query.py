import hashlib

import aiogram
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InlineQueryResultAudio, \
    InlineQueryResultVideo, InlineQueryResultPhoto, InputTextMessageContent, InputMediaAudio, InlineQueryResultArticle, \
    InlineQueryResultVoice, InlineQueryResultDocument, InputMediaDocument

import load_all
from config import BOT_TOKEN
from load_all import bot, dp
from models.item_model import Item
from utils.data_manager import get_data

router = Router()
dp.include_router(router)


@router.inline_query(lambda query: True)
async def inline_query(query: types.InlineQuery):
    user_id = query.from_user.id
    data = await get_data(user_id)
    item: Item = data.get('current_item')  # load_all.current_item.get(user_id)
    # print(f"item {item}")
    if item:
        item_body = await item.get_body()
    else:
        item_body = "пусто"
    item_title = await item.get_inline_title()
    # file_id = await item.get_all_media_values()[0]
    input_message_content = InputTextMessageContent(message_text=item_body, parse_mode=ParseMode.HTML)

    # media_photo = None
    # photo_url = ""
    # file = None
    # for file_id in item.media['photo']:
    #     if not media_photo:
    #         media_photo = InputMediaPhoto(media=file_id)
    #     file = await bot.get_file(file_id)
    #     #print(f"file_path {file.file_path}")
    #     #photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    #     #photo_url = f"https://png.pngtree.com/png-clipart/20210309/original/pngtree-share-social-media-icon-3d-render-illustration-png-image_5860447.jpg"
    #     #photo_url = f"https://png.pngtree.com/png-vector/20191024/ourlarge/pngtree-share-icon-isolated-on-background-png-image_1861897.jpg"
    #
    #
    #     #else:
    #     #    media_photo. attach_photo(file_id)

    photo_url = f"https://avatars.mds.yandex.net/i?id=e915ed8674cf1b1719106eef318b439f5f63d37f-9236004-images-thumbs&ref=rim&n=33&w=250&h=250"

    media_results = []

    result_id = hashlib.md5(query.query.encode()).hexdigest()
    item_button = InlineKeyboardButton(text="Поделиться", switch_inline_query_current_chat=result_id)
    media_results.append(
        InlineQueryResultArticle(
            id=result_id,
            title=item_title,
            description=item.text,
            input_message_content=input_message_content,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[item_button]]),
            thumbnail_url=photo_url
        )
    )

    media_button = InlineKeyboardButton(text="Показать следующую", switch_inline_query_current_chat=result_id)
    inline_markup_media = InlineKeyboardMarkup(inline_keyboard=[[media_button]])
    await create_document_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_photo_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_audio_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_voice_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_video_results(item=item, media_results=media_results, inline_markup=inline_markup_media)
    await create_video_note_results(item=item, media_results=media_results, inline_markup=inline_markup_media)

    await bot.answer_inline_query(
        query.id,
        results=media_results,
        cache_time=0,
    )


async def create_document_results(item: Item, media_results: list, inline_markup):
    for file_info in item.media['document']:
        print(f"item.media[document] = {item.media['document']}")
        file_id = file_info.get('file_id')
        file_name = file_info.get('file_name')
        mime_type = file_info.get('mime_type')
        result = InlineQueryResultDocument(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            title=file_name,
            document_url=file_id,
            mime_type=mime_type,
            # description=item.text,
            # caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup
        )
        media_results.append(result)
    return media_results


async def create_photo_results(item: Item, media_results: list, inline_markup):
    item_title = await item.get_inline_title()
    for file_id in item.media['photo']:
        result = InlineQueryResultPhoto(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            photo_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            title=item_title,
            description=item.text,
            caption=item.text,
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
