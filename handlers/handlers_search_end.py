from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from enums.enums import Environment
from handlers import states
from handlers.handlers_folder import show_folders
from handlers.handlers_item import show_item
from load_all import dp
from utils.data_manager import get_data, set_data
from utils.utils_ import get_environment
from utils.utils_data import set_current_folder_id
from utils.utils_items_reader import get_folder_id

router = Router()
dp.include_router(router)


@router.message(states.Item.Search, F.text == "❎ Завершить режим поиска 🔍️")
@router.message(states.Item.SearchResults, F.text == "❎ Завершить режим поиска 🔍️")
async def search_item_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await get_data(user_id)
    data['dict_search_data'] = None
    await set_data(user_id, data)

    environment: Environment = await get_environment(user_id)
    if environment is Environment.FOLDERS:
        await show_folders(user_id)
    elif environment is Environment.ITEM_CONTENT:
        item_id = data.get('item_id')
        if item_id:
            current_folder = get_folder_id(item_id)
            await set_current_folder_id(user_id, current_folder)
            await show_item(user_id, item_id)