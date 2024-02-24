import asyncio

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Document, InputMediaPhoto, Location, Contact

from callbacks.callbackdata import MarkFileCallback
from handlers import states
from load_all import dp, bot
from models.item_model import Item
from utils.data_manager import get_data, set_data
from utils.utils_button_manager import get_edit_item_files_keyboard, create_general_reply_markup, \
    get_edit_file_inline_markup, file_mark_off, file_mark_on
from utils.utils_file_finder import FileFinder
from utils.utils_files import dict_to_document, dict_to_location, dict_to_contact
from utils.utils_items_reader import get_item

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "edit_item_files")
async def edit_item_files_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)

    buttons = get_edit_item_files_keyboard()
    markup = create_general_reply_markup(buttons)
    await bot.send_message(chat_id=user_id, text='Редактирование файлов:', reply_markup=markup)
    await show_all_files_edit_mode(user_id, item)
    await state.set_state(states.Item.EditFiles)
    await call.answer()


async def show_all_files_edit_mode(user_id, item: Item):
    edit_file_messages = []
    delete_file_ids = {}

    for content_type, files in item.media.items():
        for file_info in files:
            if content_type == 'document':
                file_id = FileFinder.get_file_id(file_info)
                caption = file_info['caption']
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_document(
                        chat_id=user_id, document=file_id, caption=caption, reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'photo':
                file_id = FileFinder.get_file_id(file_info)
                caption = file_info['caption']
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_photo(
                        chat_id=user_id, photo=file_id, caption=caption, reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'audio':
                file_id = FileFinder.get_file_id(file_info)
                caption = file_info['caption']
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_audio(
                        chat_id=user_id, audio=file_id, caption=caption, reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'voice':
                file_id = FileFinder.get_file_id(file_info)
                caption = file_info['caption']
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_voice(
                        chat_id=user_id, voice=file_id, caption=caption, reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'video':
                file_id = FileFinder.get_file_id(file_info)
                caption = file_info['caption']
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_video(
                        chat_id=user_id, video=file_id, caption=caption, reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'video_note':
                file_id = FileFinder.get_file_id(file_info)
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_video_note(
                        chat_id=user_id, video_note=file_id, reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'sticker':
                file_id = FileFinder.get_file_id(file_info)
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_sticker(
                        chat_id=user_id, sticker=file_id, reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'location':
                file_id = FileFinder.get_file_id(file_info)
                location_dict = file_info['fields']
                location: Location = dict_to_location(location_dict)
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_location(
                        chat_id=user_id,
                        longitude=location.longitude,
                        latitude=location.latitude,
                        horizontal_accuracy=location.horizontal_accuracy,
                        live_period=location.live_period,
                        heading=location.heading,
                        proximity_alert_radius=location.proximity_alert_radius,
                        reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'contact':
                file_id = FileFinder.get_file_id(file_info)
                contact_dict = file_info['fields']
                contact: Contact = dict_to_contact(contact_dict)
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_contact(
                        chat_id=user_id,
                        phone_number=contact.phone_number,
                        first_name=contact.first_name,
                        last_name=contact.last_name,
                        vcard=contact.vcard,
                        reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]

            await asyncio.sleep(0.2)

    data = await get_data(user_id)
    data['edit_file_messages'] = edit_file_messages
    data['delete_file_ids'] = delete_file_ids
    await set_data(user_id, data)


@router.callback_query(MarkFileCallback.filter())
async def edit_item_files_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    inline_markup = call.message.reply_markup
    mark_button = inline_markup.inline_keyboard[-1][0]
    call_data: MarkFileCallback = MarkFileCallback.unpack(call.data)
    data = await get_data(user_id)
    delete_file_ids = data.get('delete_file_ids')
    if delete_file_ids[call_data.file_id][1]:
        mark_button.text = file_mark_off
        delete_file_ids[call_data.file_id][1] = False
    else:
        mark_button.text = file_mark_on
        delete_file_ids[call_data.file_id][1] = True
    inline_markup.inline_keyboard[-1][0] = mark_button
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup)
    await call.answer()

