import hashlib

import aiogram
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

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
    item: Item = data.get('current_item')  #load_all.current_item.get(user_id)
    #print(f"item {item}")
    if item:
        item_body = await item.get_body()
    else:
        item_body = "пусто"
    item_title = await item.get_inline_title()
    #file_id = await item.get_all_media_values()[0]
    input_message_content = types.InputTextMessageContent(message_text=item_body, parse_mode=ParseMode.HTML)

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
    button = InlineKeyboardButton(text="Поделиться", switch_inline_query_current_chat=result_id)
    media_results.append(
        types.InlineQueryResultArticle(
            id=result_id,
            title=item_title,
            description=item.text,
            input_message_content=input_message_content,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[button]]),
            thumbnail_url=photo_url
            )
    )

    for file_id in item.media['photo']:
        button = InlineKeyboardButton(text="Показать следующую", switch_inline_query_current_chat=result_id)
        photo_result = types.InlineQueryResultPhoto(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            photo_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            title=item_title,
            description=item.text,
            caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[button]])
            )

        media_results.append(photo_result)

    for file_id in item.media['video']:
        file = await bot.get_file(file_id)
        button = InlineKeyboardButton(text="Показать следующую", switch_inline_query_current_chat=result_id)
        video_result = types.InlineQueryResultVideo(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            video_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            mime_type='video/mp4',
            title=file.file_path,
            #description=item.text,
            #caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[button]])
            )

        media_results.append(video_result)

    await bot.answer_inline_query(
        query.id,
        results=media_results,
        cache_time=0,
    )

