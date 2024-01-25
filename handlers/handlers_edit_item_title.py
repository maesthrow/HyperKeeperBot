import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext

from firebase_pack.firebase_item_reader import get_item
from handlers import states
from handlers.handlers_item_inline_buttons import close_item_handler
from load_all import bot
from models.item_model import Item
from utils.data_manager import get_data
from utils.utils_items_db import util_edit_item


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
        data = await state.get_data()
        type_edit_text = data.get('type_edit_text', None)
        if type_edit_text == 'new_text_type_add' or type_edit_text is None:
            item.text = f"{item.text}\n{edit_text}" if item.text != "" else f"{edit_text}"
        else:
            item.text = edit_text
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

    await state.set_state()
    # await show_item(item_id)