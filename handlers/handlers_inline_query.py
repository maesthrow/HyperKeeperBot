import hashlib

import aiogram
from aiogram import types, Router
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import load_all
from load_all import bot, dp
from models.item_model import Item

router = Router()
dp.include_router(router)


@router.inline_query(lambda query: True)
async def inline_query(query: types.InlineQuery):
    user_id = query.from_user.id
    item: Item = load_all.current_item.get(user_id)
    if item:
        item_body = await item.get_body()
    else:
        item_body = "пусто"
    item_title = await item.get_inline_title()
    #file_id = await item.get_all_media_values()[0]
    input_message_content = types.InputTextMessageContent(message_text=item_body, parse_mode=ParseMode.HTML)

    media = aiogram.types.InputMedia() #MediaGroup
    for file_id in item.media['photo']:
        media.attach_photo(file_id)

    media_results = []

    result_id = hashlib.md5(query.query.encode()).hexdigest()
    button = InlineKeyboardButton(text="Поделиться", switch_inline_query_current_chat=result_id)
    media_results.append(
        types.InlineQueryResultArticle(
            id=result_id,
            title=item_title,
            description=item.text,
            input_message_content=input_message_content,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[button]])
            )
    )

    for file_id in item.media['photo']:
        button = InlineKeyboardButton(text="Показать следующую", switch_inline_query_current_chat="next_photo")
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

    await bot.answer_inline_query(
        query.id,
        results=media_results,
        cache_time=0,
    )

