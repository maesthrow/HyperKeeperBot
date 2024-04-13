from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from handlers_pack.filters import NewItemValidateFilter
from handlers_pack.handlers_save_item_content import text_to_message_handler
from load_all import dp

router = Router()
dp.include_router(router)


@router.message(NewItemValidateFilter(), F.via_bot == None, F.content_type == 'text')
async def any_message(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await text_to_message_handler(message, state)