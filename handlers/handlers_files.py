import aiogram
from aiogram.dispatcher import FSMContext

from load_all import dp
from aiogram.dispatcher.filters import Command


# @dp.message_handler(content_types=['document', 'photo'])
# async def files_message(message: aiogram.types.Message, state: FSMContext):
#     await message.answer(message.text)