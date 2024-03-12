import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext

from handlers import states
from handlers.handlers_item_inline_buttons import close_item_handler
from load_all import bot
from models.item_model import Item
from utils.data_manager import get_data
from utils.utils_data import get_current_folder_id
from utils.utils_items_db import util_edit_item
from utils.utils_items_reader import get_item


async def edit_item(user_id, state: FSMContext, edit_text=None):
    data = await get_data(user_id)
    item_id = data.get('item_id')
    item: Item = await get_item(user_id, item_id)
    current_state = await state.get_state()
    if current_state == states.ItemState.EditTitle.state:
        item.title = edit_text.strip() if edit_text else ''
        message_success_text = "Новый заголовок сохранен ✅"
        message_failure_text = "Что то пошло не так при сохранении заголовка ❌"
    else:
        state_data = await state.get_data()
        text_page = state_data.get('item_text_page', 0)
        #item.text[text_page] = edit_text
        if edit_text:
            item.insert_text(page=text_page, text_inserted=edit_text, rewrite_page=True)
        else:
            item.clear_text()
            await state.update_data(item_text_page=0)

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

