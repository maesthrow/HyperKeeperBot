import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext

from handlers import states
from handlers.handlers_item_inline_buttons import close_item_handler
from load_all import bot
from models.item_model import Item
from utils.data_manager import get_data
from utils.utils_items_db import util_edit_item
from utils.utils_items_reader import get_item


async def on_edit_item(user_id, edit_text, state: FSMContext):
    data = await get_data(user_id)
    item_id = data.get('item_id')
    item: Item = await get_item(user_id, item_id)
    current_state = await state.get_state()
    if current_state == states.Item.EditTitle.state:
        item.title = edit_text
        message_success_text = "Новый заголовок сохранен ✅"
        message_failure_text = "Что то пошло не так при сохранении заголовка ❌"
    else:
        text_page = data.get('item_text_page', None)
        item.text[text_page] = edit_text

        message_success_text = "Новый текст сохранен ✅"
        message_failure_text = "Что то пошло не так при сохранении текста ❌"

    item.date_modified = datetime.now()

    item_message = data.get('bot_message', None)
    if item_message:
        await close_item_handler(message=item_message)
        #await bot.delete_message(chat_id=chat.id, message_id=item_message.message_id)

    result = await util_edit_item(user_id, item_id, item)
    if result:
        sent_message = await bot.send_message(user_id, message_success_text)
    else:
        sent_message = await bot.send_message(user_id, message_failure_text)

    await asyncio.sleep(0.4)

    await state.get_state()
    # await show_item(item_id)