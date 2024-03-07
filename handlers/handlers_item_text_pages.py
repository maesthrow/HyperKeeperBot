import copy

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import TextPagesCallback
from handlers.handlers_item import get_item_inline_markup
from handlers.handlers_item_edit_inline_buttons import edit_question, edit_question_text, get_instruction_copy_edit_text
from load_all import dp
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import get_text_pages_buttons, get_repost_button_in_markup, item_edit_buttons, \
    delete_page_inline_button, get_edit_page_buttons
from utils.utils_constants import numbers
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import markdown_without_code

router = Router()
dp.include_router(router)

select_smile = '✅'


@router.callback_query(TextPagesCallback.filter())
async def text_pages_handler(call: CallbackQuery):
    call_data: TextPagesCallback = TextPagesCallback.unpack(call.data)
    message = call.message
    inline_markup = message.reply_markup
    item_id = call_data.item_id
    author_user_id = call_data.author_user_id
    page = call_data.page
    print(f'author_user_id {author_user_id}\nitem_id {item_id}\npage {page}')

    item: Item = await get_item(int(author_user_id), item_id)
    if call_data.action.startswith('prev') or call_data.action.startswith('next'):
        new_body = get_item_body_of_page(item, page, call_data.action, message)
        inline_markup.inline_keyboard.pop(0)
        mode = f'_{'_'.join(call_data.action.split('_')[1:])}'
        if mode == '_edit':
            user_id = call.from_user.id
            data = await get_data(user_id=user_id)
            data['item_text_page'] = page
            await set_data(user_id=user_id, data=data)
        inline_markup.inline_keyboard.insert(0, get_text_pages_buttons(author_user_id, item, page, mode))
        await message.edit_text(
            text=new_body,
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )
    elif call_data.action.startswith('all') or call_data.action.startswith('this'):
        await text_all_pages(author_user_id, item, page, call_data.action, message)
    elif call_data.action == 'back':
        inline_markup = await get_item_inline_markup(author_user_id, item, page)
        await message.edit_reply_markup(reply_markup=inline_markup)
    elif call_data.action == 'back_pre_edit':
        item_inlines = copy.deepcopy(item_edit_buttons)
        if len(item.text) > 1:
            item_inlines.insert(0, get_text_pages_buttons(author_user_id, item, page, mode='_pre_edit'))
        inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=item_inlines, resize_keyboard=True)
        await message.edit_reply_markup(reply_markup=inline_markup)
    elif call_data.action == 'back_edit':
        if len(item.text) > 1:
            page_buttons = get_text_pages_buttons(author_user_id, item, page, mode='_edit')
            buttons = [page_buttons, get_edit_page_buttons()]
            inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=buttons, resize_keyboard=True)
            await message.edit_reply_markup(reply_markup=inline_markup)

    await call.answer()


async def text_all_pages(author_user_id: int, item: Item, page_number: int, action: str, message: Message):
    print(f'action {action}')
    back_action = 'back'
    this_action = 'this'
    if '_pre_edit' in action:
        back_action = 'back_pre_edit'
        this_action = 'this_pre_edit'
    elif '_edit' in action:
        back_action = 'back_edit'
        this_action = 'this_edit'
    builder = InlineKeyboardBuilder()
    builder.button(
        text='↩️ Назад',
        callback_data=TextPagesCallback(author_user_id=author_user_id, item_id=item.id, action=back_action,
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
                action=this_action,
                page=page)
            .pack()
        )
    builder.adjust(1)
    new_body = get_item_body_of_page(item, page_number, action, message)
    inline_markup = builder.as_markup(resize_keyboard=True)
    if action.startswith('all'):
        await message.edit_reply_markup(reply_markup=inline_markup)
    elif action.startswith('this'):
        # if message.reply_markup != inline_markup:
        try:
            await message.edit_text(
                text=new_body,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=inline_markup
            )
        except:
            pass


def get_item_body_of_page(item: Item, page_number: int, action: str, message: Message):
    if '_pre_edit' in action:
        item_body = item.get_body_markdown(page_number)
        last_row = message.text.split('\n')[-1]
        if edit_question in last_row:
            item_body += edit_question_text
    elif '_edit' in action:
        item_body = get_instruction_copy_edit_text(item, page_number)
    else:
        item_body = item.get_body_markdown(page_number)

    return item_body




