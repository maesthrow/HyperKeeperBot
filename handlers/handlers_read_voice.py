import asyncio

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from callbacks.callbackdata import ReadVoiceRetryCallback, VoiceSaveTypeCallback
from handlers import states
from handlers.handlers_item_add_mode import add_files_to_message_handler
from handlers.handlers_save_item_files import files_to_message_handler, text_to_message_handler
from load_all import bot, dp
from models.item_model import INVISIBLE_CHAR
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import get_voice_save_inline_markup, get_voice_read_fail_inline_markup
from utils.utils_parse_mode_converter import escape_markdown
from utils.utils_wit_ai_voice import get_voice_text

router = Router()
dp.include_router(router)


async def read_voice(message: Message):
    user_id = message.from_user.id
    wait_message = await bot.send_message(
        chat_id=user_id,
        text='🎧 Слушаю ваше голосовое...'
    )
    try:
        voice_text = await get_voice_text(message.voice, message)
        data = await get_data(user_id)
        data['voice_text'] = voice_text
        markdown_voice_text = escape_markdown(voice_text)
        await set_data(user_id, data)
        message_text = f'{INVISIBLE_CHAR}\n`{markdown_voice_text}`\n\n\n_Как вы хотите сохранить голосовое сообщение?_'
        inline_markup = get_voice_save_inline_markup()
    except Exception as e:
        inline_markup = get_voice_read_fail_inline_markup()
        message_text = ("Что то пошло не так при распознавании текста 🤷‍♂️"
                        "\n\n_Вы можете повторить попытку\, либо сохранить голосовое сообщение:_")

    await asyncio.gather(
        delete_message_and_reply(user_id, message, message_text, wait_message, inline_markup)
    )


async def delete_message_and_reply(
        user_id,
        message: Message,
        message_text: str,
        wait_message: Message,
        inline_markup: InlineKeyboardMarkup):
    await bot.delete_message(user_id, wait_message.message_id)
    await message.reply(
        text=message_text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=inline_markup)


@router.callback_query(ReadVoiceRetryCallback.filter())
async def retry_voice(call: CallbackQuery):
    user_id = call.from_user.id
    data = await get_data(user_id)
    voice_message = data.get('voice_message', None)
    await call.answer()
    if voice_message:
        await read_voice(voice_message)
    else:
        await call.answer('Не удалось повторить распознавание текста 🙁')
    await bot.delete_message(user_id, call.message.message_id)


@router.callback_query(VoiceSaveTypeCallback.filter())
async def save_type_voice(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    voice_text = data.get('voice_text', '')
    text_message = await bot.edit_message_text(
        chat_id=user_id,
        message_id=call.message.message_id,
        parse_mode=ParseMode.MARKDOWN_V2,
        text=f'`{voice_text}`'
    )
    call_data = VoiceSaveTypeCallback.unpack(call.data)
    save_type = call_data.type
    func = add_files_to_message_handler if state == states.ItemState.AddTo else files_to_message_handler

    if save_type == 'text':
        await text_to_message_handler(text_message, state)
    elif save_type == 'voice':
        voice_message: Message = data.get('voice_message', None)
        await func([voice_message], state)

    await call.answer()
    #await bot.delete_message(user_id, call.message.message_id)
