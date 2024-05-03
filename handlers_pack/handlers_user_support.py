from aiogram import Router
from aiogram.types import CallbackQuery

from callbacks.callbackdata import AnswerUserAfterContactSupportCallback
from load_all import dp, bot

router = Router()
dp.include_router(router)


@router.callback_query(AnswerUserAfterContactSupportCallback.filter())
async def answer_user_after_contact_support_handler(
        call: CallbackQuery,
        callback_data: AnswerUserAfterContactSupportCallback
):
    contact_user_id = callback_data.user_id
    await bot.send_message(contact_user_id, 'answer')
    await call.answer()
