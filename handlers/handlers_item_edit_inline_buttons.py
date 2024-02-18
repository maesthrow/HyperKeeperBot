import asyncio
import copy

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, Message

from callbacks.callbackdata import TextPagesCallback
from handlers import states
from handlers.handlers_folder import show_folders
from handlers.handlers_item import show_item
from handlers.handlers_item_inline_buttons import get_item_body_and_current_markup
from load_all import bot, dp
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_ import invisible_char
from utils.utils_button_manager import item_edit_buttons, create_general_reply_markup, \
    get_edit_item_title_keyboard, cancel_edit_item_button, get_edit_item_text_keyboard, delete_page_inline_button
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import to_markdown_text, preformat_text, full_escape_markdown, \
    markdown_without_code

edit_question = 'Что будете редактировать?'
edit_question_text = f"\n\n_*{edit_question}*_"

# add_none_title_item_button = InlineKeyboardButton(text="🪧 Пустой заголовок", callback_data=f"add_none_title_item")
# cancel_edit_item_button = InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_edit_item")

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "edit_item")
async def edit_item_handler(call: CallbackQuery):
    item_inlines = copy.deepcopy(item_edit_buttons)
    current_markup = call.message.reply_markup
    middle_btn = current_markup.inline_keyboard[0][1]
    if middle_btn.callback_data and TextPagesCallback.__prefix__ in middle_btn.callback_data:
        for btn in current_markup.inline_keyboard[0]:
            callback_data: TextPagesCallback = TextPagesCallback.unpack(btn.callback_data)
            action = callback_data.action.split('_')[0]
            callback_data.action = f'{action}_pre_edit'
            btn.callback_data = callback_data.pack()
        item_inlines.insert(0, current_markup.inline_keyboard[0])
    inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=item_inlines)

    item_body, current_markup = await get_item_body_and_current_markup(call.from_user.id)
    #format_message_text = to_markdown_text(call.message.text, call.message.entities)

    await call.message.edit_text(
        text=f"{item_body}{edit_question_text}",
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await call.answer()


@router.callback_query(F.data == "edit_item_title")
async def edit_item_title_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)

    edit_item_messages = []

    if item.title:
        edit_item_messages.append(
            await bot.send_message(call.message.chat.id,
                                   f"Нажмите на текст ниже, чтобы скопировать текущий заголовок:"
                                   f"\n\n`{item.title}`",
                                   parse_mode=ParseMode.MARKDOWN_V2)
        )

    await asyncio.sleep(0.4)

    buttons = get_edit_item_title_keyboard(item.title)
    markup = create_general_reply_markup(buttons)

    edit_item_messages.append(
        await bot.send_message(call.message.chat.id,
                               f"Придумайте новый заголовок:",
                               reply_markup=markup)
    )

    data = await get_data(user_id)
    data['edit_item_messages'] = edit_item_messages
    await set_data(user_id, data)

    await state.set_state(states.Item.EditTitle)
    await call.answer()


@router.callback_query(F.data == "edit_item_text")
async def edit_item_text_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)
    inline_markup, page = await get_inline_markup_and_page(call.message)

    edit_item_messages = []
    if item.get_text():
        edit_item_messages.append(
            await bot.send_message(chat_id=call.message.chat.id,
                                   text=get_instruction_copy_edit_text(item, page),
                                   parse_mode=ParseMode.MARKDOWN_V2,
                                   reply_markup=inline_markup
                                   )
        )

    await asyncio.sleep(0.4)

    buttons = get_edit_item_text_keyboard(item.text)
    markup = create_general_reply_markup(buttons)

    edit_item_messages.append(
        await bot.send_message(call.message.chat.id,
                               text=get_instruction_new_edit_text(item),
                               reply_markup=markup)
    )

    data['item_text_page'] = page
    data['edit_item_messages'] = edit_item_messages
    await set_data(user_id, data)

    await state.set_state(states.Item.EditText)
    await call.answer()


async def get_inline_markup_and_page(message: Message):
    current_markup = message.reply_markup
    middle_btn = current_markup.inline_keyboard[0][1]
    inline_markup = None
    page = 0
    if middle_btn.callback_data and TextPagesCallback.__prefix__ in middle_btn.callback_data:
        for btn in current_markup.inline_keyboard[0]:
            callback_data: TextPagesCallback = TextPagesCallback.unpack(btn.callback_data)
            if btn == middle_btn:
                page = callback_data.page
            action = callback_data.action.split('_')[0]
            callback_data.action = f'{action}_edit'
            btn.callback_data = callback_data.pack()

        buttons = [current_markup.inline_keyboard[0], [delete_page_inline_button]]
        inline_markup = InlineKeyboardMarkup(row_width=3, inline_keyboard=buttons)
    return inline_markup, page


@router.callback_query(F.data == "remove_page")
async def remove_text_page_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)
    inline_markup, page = await get_inline_markup_and_page(call.message)

    item_inlines = [
        [
            InlineKeyboardButton(text="☑️ Да", callback_data="delete_page_yes"),
            InlineKeyboardButton(text="✖️ Нет", callback_data="delete_page_no"),
        ]
    ]
    inline_markup = InlineKeyboardMarkup(row_width=2, inline_keyboard=item_inlines)

    await bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        text=f'{get_instruction_copy_edit_text(item, page)}\n\n\n _*Хотите удалить {page + 1} страницу?*_',
        reply_markup=inline_markup,
        parse_mode=ParseMode.MARKDOWN_V2
    )

def get_instruction_copy_edit_text(item: Item, page_number: int):
    entity = f'страницы {(page_number + 1)}' if len(item.text) > 1 else 'записи'
    return f"_Нажмите на текущий текст {entity}, чтобы скопировать:_ ↙️" \
           f"\n\n`{markdown_without_code(item.get_text(page_number))}`"


def get_instruction_new_edit_text(item: Item):
    addiction = f' для выбранной страницы' if len(item.text) > 1 else ''
    return f"Напишите новый текст{addiction} или выберите действие:"
