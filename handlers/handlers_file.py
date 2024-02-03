from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from handlers.handlers_ import files_in_message_handler
from load_all import dp, bot

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "close_file")
async def close_file_handler(call: CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.answer()


@router.callback_query(F.data == "save_file")
async def save_file_handler(call: CallbackQuery, state: FSMContext):
    await files_in_message_handler([call.message], state)