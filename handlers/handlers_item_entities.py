from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from callbacks.callbackdata import SaveItemCallback
from handlers.handlers_ import files_to_message_handler
from handlers.handlers_item import on_create_new_item
from handlers.handlers_save_item_files import text_to_new_item_handler
from load_all import dp, bot
from models.item_model import Item
from utils.utils_button_manager import save_file_buttons, save_page_buttons
from utils.utils_items_reader import get_item

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "close_entity")
async def close_entity_handler(call: CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.answer()


@router.callback_query(F.data == "save_file")
async def save_file_handler(call: CallbackQuery, state: FSMContext):
    await files_to_message_handler([call.message], state)
    await call.answer()


@router.callback_query(F.data == "save_text_page")
async def save_text_page_handler(call: CallbackQuery, state: FSMContext):
    await text_to_new_item_handler([call.message], state)
    await call.answer()


@router.callback_query(SaveItemCallback.filter())
async def save_item_handler(call: CallbackQuery, state: FSMContext):
    callback_data: SaveItemCallback = SaveItemCallback.unpack(call.data)
    author_user_id = callback_data.author_user_id
    item_id = callback_data.item_id
    item: Item = await get_item(author_user_id, item_id)
    await on_create_new_item(state, item, call=call)
    await call.answer()
