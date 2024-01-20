import asyncio
import hashlib

import aiogram
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.types import Chat, User

import load_all
from load_all import dp, bot, current_item
from models.item_model import Item


@dp.inline_handler(lambda query: True)
async def inline_query(query: types.InlineQuery):
    tg_user = User.get_current()
    # data = await dp.storage.get_data(user=tg_user, chat=tg_user.id)
    item: Item = load_all.current_item.get(tg_user.id)
    if item:
        item_body = await item.get_body()
    else:
        item_body = "пусто"
    item_title = await item.get_inline_title()
    file_id = await item.get_all_media_values()[0]
    input_message_content = types.InputTextMessageContent(item_body, parse_mode=types.ParseMode.HTML)

    media = aiogram.types.InputMedia() #MediaGroup
    for file_id in item.media['photo']:
        media.attach_photo(file_id)

    media_results = []

    result_id = hashlib.md5(query.query.encode()).hexdigest()
    media_results.append(
        types.InlineQueryResultArticle(
            id=result_id,
            title=item_title,
            description=item.text,
            input_message_content=input_message_content,
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(text="Поделиться", switch_inline_query_current_chat=result_id)
            ),
        ),
    )

    for file_id in item.media['photo']:
        photo_result = types.InlineQueryResultPhoto(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            photo_url=file_id,
            thumb_url=file_id,
            title=item_title,
            description=item.text,
            caption=item.text,
            parse_mode=ParseMode.HTML,
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton(text="Показать следующую", switch_inline_query_current_chat="next_photo")
            ),
        )
        media_results.append(photo_result)

    await bot.answer_inline_query(
        query.id,
        results=media_results,
        cache_time=0,
    )

    # result_id = hashlib.md5(query.query.encode()).hexdigest()
    # await bot.answer_inline_query(
    #     query.id,
    #     results=[
    #         types.InlineQueryResultArticle(
    #             id=result_id,
    #             title=item_title,
    #             input_message_content=input_message_content,
    #             reply_markup=types.InlineKeyboardMarkup().add(
    #                 types.InlineKeyboardButton("Поделиться", switch_inline_query_current_chat=result_id)
    #             ),
    #         ),
    #         # Другие результаты по вашему выбору
    #     ],
    #     cache_time=0,
    # )
