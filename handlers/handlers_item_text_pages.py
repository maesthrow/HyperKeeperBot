from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import TextPagesCallback
from handlers.handlers_item import get_item_inline_markup
from load_all import dp, bot
from models.item_model import Item
from utils.utils_button_manager import get_text_pages_buttons, get_repost_button_in_markup
from utils.utils_items_reader import get_item

router = Router()
dp.include_router(router)

select_smile = '✅'
numbers = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣',
           '9': '9️⃣'}


@router.callback_query(TextPagesCallback.filter())
async def text_pages_handler(call: CallbackQuery):
    data: TextPagesCallback = TextPagesCallback.unpack(call.data)
    message = call.message
    inline_markup = message.reply_markup
    item_id = data.item_id
    author_user_id = data.author_user_id
    page = data.page
    print(f'author_user_id {author_user_id}\nitem_id {item_id}\npage {page}')

    item: Item = await get_item(int(author_user_id), item_id)

    if data.action == 'prev' or data.action == 'next':
        inline_markup.inline_keyboard.pop(0)
        inline_markup.inline_keyboard.insert(0, get_text_pages_buttons(author_user_id, item, page))
        await message.edit_text(
            text=item.get_body_markdown(page),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )
    elif data.action == 'all' or data.action == 'this':
        await text_all_pages(author_user_id, item, page, data.action, message)
    elif data.action == 'back':
        inline_markup = await get_item_inline_markup(author_user_id, item, page)
        await message.edit_reply_markup(reply_markup=inline_markup)

    await call.answer()


async def text_all_pages(author_user_id: int, item: Item, page_number: int, action: str, message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='↩️ Назад',
        callback_data=TextPagesCallback(author_user_id=author_user_id, item_id=item.id, action='back',
                                        page=page_number).pack()
    )
    for page in range(len(item.text)):
        display_page = ''.join([numbers[n] for n in str(page + 1)])
        text = f'{display_page} {item.get_inline_page_text(page)}'
        text = f'{select_smile} {text}' if page == page_number else text
        builder.button(
            text=text,
            callback_data=TextPagesCallback(
                author_user_id=author_user_id,
                item_id=item.id,
                action='this',
                page=page)
            .pack()
        )
    builder.adjust(1)
    new_body = item.get_body_markdown(page_number)
    inline_markup = builder.as_markup(resize_keyboard=True)
    if action == 'all':
        await message.edit_reply_markup(reply_markup=inline_markup)
    elif action == 'this':
        # if message.reply_markup != inline_markup:
        try:
            await message.edit_text(
                text=new_body,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=inline_markup
            )
        except:
            pass
