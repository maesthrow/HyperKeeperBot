from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager

from handlers_pack.filters import NewItemValidateFilter
from handlers_pack.handlers_rag import rag_search_handler
from handlers_pack.handlers_save_item_content import text_to_message_handler
from load_all import dp

router = Router()
dp.include_router(router)

BOT_MENTION_KEEP = "Кип"
BOT_MENTION_HYP = "Гип"


@router.message(NewItemValidateFilter(), F.via_bot == None, F.content_type == 'text')
async def any_message(message: Message, state: FSMContext, dialog_manager: DialogManager):
    print("ANY MESSAGE")

    if (message.text.lower().startswith(f'{BOT_MENTION_KEEP.lower()} ')
            or message.text.lower().startswith(f'{BOT_MENTION_KEEP.lower()}, ')
            or message.text.lower().startswith(f'{BOT_MENTION_HYP.lower()} ')
            or message.text.lower().startswith(f'{BOT_MENTION_HYP.lower()}, ')
    ):
        await rag_search_handler(message, state)
    else:
        await text_to_message_handler(message, state)

