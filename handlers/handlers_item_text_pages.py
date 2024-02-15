from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from callbacks.callbackdata import TextPagesCallback
from load_all import dp, bot
from models.item_model import Item
from utils.utils_button_manager import get_text_pages_buttons, get_repost_button_in_markup
from utils.utils_items_reader import get_item

router = Router()
dp.include_router(router)


@router.callback_query(TextPagesCallback.filter())
async def text_pages_handler(call: CallbackQuery):
    #user_id = call.from_user.id
    data: TextPagesCallback = TextPagesCallback.unpack(call.data)
    inline_markup = call.message.reply_markup
    repost_button = get_repost_button_in_markup(inline_markup)
    author_user_id, item_id = repost_button.switch_inline_query.split('_')
    page = data.page
    print(f'author_user_id {author_user_id}\nitem_id {item_id}\npage {page}')

    item: Item = await get_item(int(author_user_id), item_id)

    message = call.message

    if page is not None:
        inline_markup.inline_keyboard.pop(0)
        inline_markup.inline_keyboard.insert(0, get_text_pages_buttons(item, page))
        await message.edit_text(
            text=item.get_body_markdown(page),
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )