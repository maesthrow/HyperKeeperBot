from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager

from callbacks.callbackdata import AnswerUserAfterContactSupportCallback, \
    AnswerAdminAfterAnswerUserContactSupportCallback
from handlers_pack.states import UserSupportState
from load_all import dp, bot
from utils.data_manager import set_any_message_ignore

router = Router()
dp.include_router(router)


@router.callback_query(AnswerUserAfterContactSupportCallback.filter())
async def answer_user_after_contact_support_handler(
        call: CallbackQuery,
        callback_data: AnswerUserAfterContactSupportCallback,
        dialog_manager: DialogManager
):
    await call.answer()
    contact_user_id = callback_data.contact_user_id
    await set_any_message_ignore(call.from_user.id, True)
    await dialog_manager.start(UserSupportState.AnswerUserContactSupport, data={'contact_user_id': contact_user_id})


@router.callback_query(AnswerAdminAfterAnswerUserContactSupportCallback.filter())
async def answer_user_after_contact_support_handler(
        call: CallbackQuery,
        dialog_manager: DialogManager
):
    await call.answer()
    await set_any_message_ignore(call.from_user.id, True)
    await dialog_manager.start(UserSupportState.ContactSupport)
