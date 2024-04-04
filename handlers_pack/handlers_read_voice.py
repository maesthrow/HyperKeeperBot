import asyncio

from aiogram import Router
from aiogram.enums import ParseMode, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from callbacks.callbackdata import ReadVoiceRunCallback, VoiceSaveTypeCallback
from handlers_pack import states
from handlers_pack.handlers_item_add_mode import add_files_to_message_handler, add_text_to_item_handler
from handlers_pack.handlers_save_item_content import files_to_message_handler, text_to_message_handler
from load_all import bot, dp
from models.item_model import INVISIBLE_CHAR, Item
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import get_voice_save_inline_markup, get_voice_read_inline_markup
from utils.utils_parse_mode_converter import escape_markdown
from utils.utils_wit_ai_voice import get_voice_text, notifies, get_video_note_text, get_start_read_notify

router = Router()
dp.include_router(router)


async def read_voice_offer(message: Message):
    inline_markup = get_voice_read_inline_markup(content_type=ContentType(message.content_type))
    message_text = f'_Выберите действие:_'
    await message.reply(text=message_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=inline_markup)
    await clean_voice_text(message)


async def clean_voice_text(message: Message):
    data = await get_data(user_id=message.from_user.id)
    data['voice_text'] = None
    await set_data(message.from_user.id, data)


async def read_voice(message: Message):
    user_id = message.from_user.id
    wait_message = await bot.send_message(
        chat_id=user_id,
        text=get_start_read_notify(ContentType(message.content_type))
    )
    try:
        voice_text = ''
        if message.content_type == ContentType.VOICE:
            voice_text = await get_voice_text(message.voice, wait_message)
        elif message.content_type == ContentType.VIDEO_NOTE:
            voice_text = await get_video_note_text(message.video_note, wait_message)
        if voice_text:
            data = await get_data(user_id)
            data['voice_text'] = voice_text
            await set_data(user_id, data)
            markdown_voice_text = escape_markdown(voice_text)
            message_text = f'{INVISIBLE_CHAR}\n`{markdown_voice_text}`'

            if message.content_type == ContentType.VOICE:
                message_text += f'\n\n\n_Как вы хотите сохранить голосовое сообщение?_'
            elif message.content_type == ContentType.VIDEO_NOTE:
                message_text += f'\n\n\n_Как вы хотите сохранить видеосообщение?_'
            inline_markup = get_voice_save_inline_markup(ContentType(message.content_type))
        else:
            inline_markup = get_voice_read_inline_markup(content_type=ContentType(message.content_type), is_retry=True)
            info_text = ('Не удалось распознать текст 🤷‍♂️'
                         '\nВозможно голос на вашей записи звучит слишком тихо.')
            message_text = (f'{escape_markdown(info_text)}'
                            f'\n\n_Попробуйте еще раз 🙏_')
    except Exception as e:
        inline_markup = get_voice_read_inline_markup(ContentType(message.content_type), is_retry=True)
        print(f'read voice error: {e}')
        message_text = (f"Что то пошло не так при распознавании текста 🤷‍♂️"
                        f"\n\n_Попробуйте еще раз 🙏_")
                        #f"\n\n_Вы можете повторить попытку\, либо сохранить голосовое сообщение:_")

    await bot.delete_message(user_id, wait_message.message_id)
    await message.reply(text=message_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=inline_markup)
    # await asyncio.gather(
    #     bot.delete_message(user_id, wait_message.message_id),
    #     message.reply(text=message_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=inline_markup)
    # )


@router.callback_query(ReadVoiceRunCallback.filter())
async def run_read_voice(call: CallbackQuery):
    user_id = call.from_user.id
    data = await get_data(user_id)
    voice_message = data.get('voice_message', None)
    if voice_message:
        await call.answer()
        await asyncio.gather(
            read_voice(voice_message),
            bot.delete_message(user_id, call.message.message_id),
        )
    else:
        await call.answer('Не удалось запустить распознавание текста 🙁')


@router.callback_query(VoiceSaveTypeCallback.filter())
async def save_type_voice(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    voice_text = data.get('voice_text', '')
    text_message = call.message
    if voice_text:
        text_message = await bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            parse_mode=ParseMode.MARKDOWN_V2,
            text=f'`{voice_text}`'
        )

    call_data = VoiceSaveTypeCallback.unpack(call.data)
    save_type = call_data.type
    state_value = await state.get_state()
    if save_type == 'text':
        if state_value == states.ItemState.AddTo:
            item: Item = data.get('item', None)
            if item:
                await add_text_to_item_handler(
                    user_id=call.from_user.id,
                    messages=[text_message],
                    state=state,
                    is_new_item=False,
                    item=item,
                    page=-1
                )
        else:
            await text_to_message_handler(text_message, state)
    elif save_type == 'voice' or save_type == 'video_note':
        voice_message: Message = data.get('voice_message', None)
        if state_value == states.ItemState.AddTo:
            await add_files_to_message_handler([voice_message], state)
        else:
            await files_to_message_handler([voice_message], state)

    await call.answer()
    if not voice_text:
        await bot.delete_message(user_id, call.message.message_id)
