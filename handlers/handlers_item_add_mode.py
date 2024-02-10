import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers import states
from handlers.handlers_folder import show_folders
from handlers.handlers_item import show_item
from load_all import dp, bot
from models.item_model import Item
from utils.data_manager import get_data
from utils.utils_items_db import util_edit_item
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import preformat_text

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "add_to_item")
async def add_to_item_handler(call: CallbackQuery, state: FSMContext):
    await bot.send_message(call.from_user.id, "Отправьте в сообщении то, чем хотите дополнить новую запись:")
    await state.set_state(states.Item.AddTo)


@router.message(states.Item.AddTo, F.content_type == 'text')
async def add_text_message(message: Message, state: FSMContext):
    format_message_text = preformat_text(message.text, message.entities)
    user_id = message.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')
    item: Item = await get_item(user_id, item_id)
    item.add_text(format_message_text)

    message_success_text = "Добавил новый текст в запись ✅"
    message_failure_text = "Что то пошло не так при добавлении текста ❌"

    result = await util_edit_item(user_id, item_id, item)
    if result:
        sent_message = await bot.send_message(user_id, message_success_text)
    else:
        sent_message = await bot.send_message(user_id, message_failure_text)
    await state.clear()
    await show_folders(user_id, need_to_resend=True)
    await asyncio.sleep(0.1)
    await show_item(user_id, item_id)
