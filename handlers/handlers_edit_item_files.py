import asyncio
from typing import List

from aiogram import Router, F
from aiogram.enums import ContentType, ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Document, InputMediaPhoto, Location, Contact, Message, InlineKeyboardButton

from callbacks.callbackdata import MarkFileCallback, DeleteFileCallback, RequestDeleteFileCallback, \
    RequestDeleteFilesCallback, EditFileCaptionCallback
from handlers import states
from handlers.handlers_item import on_cancel_edit_item
from handlers.handlers_item_inline_buttons import hide_item_files_handler
from load_all import dp, bot
from models.item_model import Item, INVISIBLE_CHAR
from utils.data_manager import get_data, set_data
from utils.message_box import MessageBox
from utils.utils_button_manager import get_edit_item_files_keyboard, create_general_reply_markup, \
    get_edit_file_inline_markup, file_mark_off, file_mark_on, file_has_caption, get_delete_file_inline_markup, \
    general_buttons_edit_item_files, get_edit_file_caption_keyboard, leave_current_caption_button, \
    remove_current_caption_button
from utils.utils_file_finder import FileFinder, get_file_id_by_short_file_id, get_file_info_by_short_file_id
from utils.utils_files import dict_to_document, dict_to_location, dict_to_contact
from utils.utils_items_db import util_edit_item
from utils.utils_items_reader import get_item
from utils.utils_parse_mode_converter import escape_markdown, markdown_without_code, preformat_text

router = Router()
dp.include_router(router)


@router.callback_query(F.data == "edit_item_files")
async def edit_item_files_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await get_data(user_id)
    item_id = data.get('item_id')

    item: Item = await get_item(user_id, item_id)

    await hide_item_files_handler(call, is_native_call=False)

    buttons = get_edit_item_files_keyboard()
    markup = create_general_reply_markup(buttons)
    await bot.send_message(
        chat_id=user_id, text='_*Редактирование файлов:*_', parse_mode=ParseMode.MARKDOWN_V2, reply_markup=markup
    )
    await show_all_files_edit_mode(user_id, item)
    await state.set_state(states.ItemState.EditFiles)
    await call.answer()


async def show_all_files_edit_mode(user_id, item: Item):
    edit_file_messages = []
    delete_file_ids = {}

    for content_type, files in item.media.items():
        for file_info in files:
            if content_type == 'document':
                file_id = FileFinder.get_file_id(file_info)
                caption = escape_markdown(file_info['caption'])
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_document(
                        chat_id=user_id,
                        document=file_id,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'photo':
                file_id = FileFinder.get_file_id(file_info)
                caption = escape_markdown(file_info['caption'])
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=file_id,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'audio':
                file_id = FileFinder.get_file_id(file_info)
                caption = escape_markdown(file_info['caption'])
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_audio(
                        chat_id=user_id,
                        audio=file_id,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'voice':
                file_id = FileFinder.get_file_id(file_info)
                caption = escape_markdown(file_info['caption'])
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_voice(
                        chat_id=user_id,
                        voice=file_id,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=inline_markup
                    )
                )
                delete_file_ids[file_id[16:24]] = [content_type, False]
            elif content_type == 'video':
                file_id = FileFinder.get_file_id(file_info)
                caption = escape_markdown(file_info['caption'])
                inline_markup = get_edit_file_inline_markup(item.id, content_type, file_id[16:24])
                edit_file_messages.append(
                    await bot.send_video(
                        chat_id=user_id,
                        video=file_id,
                        caption=caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        reply_markup=inline_markup
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

            await asyncio.sleep(0.1)

    data = await get_data(user_id)
    data['edit_file_messages'] = edit_file_messages
    data['delete_file_ids'] = delete_file_ids
    await set_data(user_id, data)


@router.callback_query(MarkFileCallback.filter())
async def mark_file_handler(call: CallbackQuery, state: FSMContext):
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

    data['delete_file_ids'] = delete_file_ids
    inline_markup.inline_keyboard[-1][0] = mark_button
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=inline_markup)
    await call.answer()


@router.callback_query(DeleteFileCallback.filter())
async def pre_delete_file_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data: DeleteFileCallback = DeleteFileCallback.unpack(call.data)
    content_type: ContentType = call_data.type
    inline_markup = get_delete_file_inline_markup(call_data.item_id, content_type, call_data.file_id)
    if file_has_caption(content_type):
        caption = escape_markdown(preformat_text(call.message.caption, call.message.caption_entities)) \
            if call.message.caption else ''
        caption = f'{caption}\n{INVISIBLE_CHAR}\n_*Удалить этот файл?*_'
        await bot.edit_message_caption(
            user_id, call.message.message_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=inline_markup
        )
    else:
        await bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=inline_markup)
    await call.answer()


@router.callback_query(RequestDeleteFileCallback.filter())
async def delete_file_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data: RequestDeleteFileCallback = RequestDeleteFileCallback.unpack(call.data)
    content_type: ContentType = call_data.type
    if call_data.res == 'n':
        data = await get_data(user_id)
        delete_file_ids = data.get('delete_file_ids')
        mark_is_on = delete_file_ids[call_data.file_id][1]
        inline_markup = get_edit_file_inline_markup(call_data.item_id, content_type, call_data.file_id,
                                                    mark_is_on=mark_is_on)
        if file_has_caption(content_type):
            caption = escape_markdown(preformat_text(call.message.caption, call.message.caption_entities))\
                if call.message.caption else ''
            caption = caption.replace('Удалить этот файл?', '').strip()
            await bot.edit_message_caption(
                user_id, call.message.message_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=inline_markup
            )
        else:
            await bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=inline_markup)
    elif call_data.res == 'y':
        item: Item = await get_item(user_id, call_data.item_id)
        del_file_info = await get_file_info_by_short_file_id(item, content_type, call_data.file_id)
        print(f'item.media[content_type] = {item.media[content_type]}')
        delete_file_in_item(item, content_type, del_file_info)

        result = await util_edit_item(user_id, item.id, item)
        if result:
            data = await get_data(user_id)
            for message in data['edit_file_messages']:
                if message.message_id == call.message.message_id:
                    data['edit_file_messages'].remove(message)
                    data['delete_file_ids'].pop(call_data.file_id, None)
                    break
            await bot.delete_message(user_id, call.message.message_id)
            if len(data['edit_file_messages']) == 0:
                await on_cancel_edit_item(user_id, state)

    await call.answer()


def delete_file_in_item(item: Item, content_type: ContentType, del_file_info):
    media: list = item.media[content_type]
    for file_info in media:
        if file_info['file_id'] == del_file_info['file_id']:
            media.remove(file_info)
            item.media[content_type] = media
            break


@router.callback_query(RequestDeleteFilesCallback.filter())
async def delete_files_handler(call: CallbackQuery, state: FSMContext):
    result = is_all = False
    user_id = call.from_user.id
    call_data: RequestDeleteFilesCallback = RequestDeleteFilesCallback.unpack(call.data)
    if call_data.res == 'n':
        await bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        return
    elif call_data.res == 'y':
        result, is_all = await delete_marked_files(user_id, is_all=call_data.is_all)

    await call.answer()
    message_text = 'Файлы удалены ✔️' if result else 'Что то пошло не так при удалении файлов ✖️'
    info_message = await bot.send_message(user_id, message_text)
    await bot.delete_message(user_id, call.message.message_id)
    await asyncio.sleep(1)
    if is_all:
        await on_cancel_edit_item(user_id, state)
    else:
        await bot.delete_message(user_id, info_message.message_id)


async def delete_marked_files(user_id, is_all):
    data = await get_data(user_id)
    edit_file_messages = data.get('edit_file_messages')
    delete_file_ids = data.get('delete_file_ids')
    item: object = None
    to_remove_messages = []
    to_remove_ids = []
    for file_message in edit_file_messages:
        inline_markup = file_message.reply_markup
        mark_button = inline_markup.inline_keyboard[-1][0]
        call_data = MarkFileCallback.unpack(mark_button.callback_data)
        if not item:
            item: Item = await get_item(user_id, call_data.item_id)

        if call_data.file_id in delete_file_ids and (delete_file_ids[call_data.file_id][1] or is_all):
            del_file_info = await get_file_info_by_short_file_id(item, call_data.type, call_data.file_id)
            delete_file_in_item(item, call_data.type, del_file_info)
            await bot.delete_message(user_id, file_message.message_id)
            if not is_all:
                to_remove_ids.append(call_data.file_id)
                to_remove_messages.append(file_message)

    data['edit_file_messages'] = [message for message in edit_file_messages if message not in to_remove_messages]
    for file_id in to_remove_ids:
        delete_file_ids.pop(file_id, None)
    data['delete_file_ids'] = delete_file_ids

    if len(data['edit_file_messages']) == 0:
        is_all = True

    result = await util_edit_item(user_id, item.id, item)

    if is_all:
        data['edit_file_messages'] = None
        data['delete_file_ids'] = None

    await set_data(user_id, data)

    return result, is_all


@router.callback_query(EditFileCaptionCallback.filter())
async def edit_file_caption_handler(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    call_data: EditFileCaptionCallback = EditFileCaptionCallback.unpack(call.data)
    item: Item = await get_item(user_id, call_data.item_id)
    file_info = await get_file_info_by_short_file_id(item, call_data.type, call_data.file_id)

    edit_file_caption_messages = []

    caption = file_info['caption']
    if caption:
        message_text = (f"Нажмите на текущий текст подписи, чтобы скопировать:"
                        f"\n\n`{markdown_without_code(caption)}`\n{INVISIBLE_CHAR}")
        edit_file_caption_messages.append(
            await bot.send_message(chat_id=user_id, text=message_text, parse_mode=ParseMode.MARKDOWN_V2)
        )

    buttons = get_edit_file_caption_keyboard(caption)
    markup = create_general_reply_markup(buttons)
    edit_file_caption_messages.append(
        await bot.send_message(user_id, 'Напишите новый текст подписи к файлу:', reply_markup=markup)
    )

    # data = await get_data(user_id)

    await state.set_state(states.ItemState.EditFileCaption)
    await state.update_data(
        edit_file_message=call.message,
        edit_file_caption_messages=edit_file_caption_messages,
        edit_file_item=item,
        edit_file_type=call_data.type,
        edit_file_info=file_info
    )
    await call.answer()


@router.message(states.ItemState.EditFileCaption)
async def edit_file_caption(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    edit_file_caption_messages = data.get('edit_file_caption_messages')
    # print(f'edit_file_caption_messages count =  {len(edit_file_caption_messages)}')
    for edit_message in edit_file_caption_messages:
        try:
            await bot.delete_message(user_id, edit_message.message_id)
        except:
            pass
    edit_file_caption_messages = []

    buttons = get_edit_item_files_keyboard()
    markup = create_general_reply_markup(buttons)

    await bot.delete_message(user_id, message.message_id)
    if message.text == leave_current_caption_button.text:
        message_text = 'Сохранена текущая подпись ☑️'
    else:
        new_text = message.text
        message_text = 'Сохранена новая подпись ☑️'
        if message.text == remove_current_caption_button.text:
            new_text = ''
            message_text = 'Подпись к файлу удалена ☑️'
        edit_file_message: Message = data.get('edit_file_message')
        item: Item = data.get('edit_file_item')
        content_type: ContentType = data.get('edit_file_type')
        edit_file_info = data.get('edit_file_info')
        caption = preformat_text(new_text, message.entities) if new_text else ''
        this_file_info = {}
        #print(f'caption = {caption}')
        for file_info in item.media[content_type]:
            if file_info['file_id']:
                is_equals_file_info = file_info['file_id'] == edit_file_info['file_id']
            else:
                is_equals_file_info = file_info['fields']['file_id'] == edit_file_info['fields']['file_id']
            if is_equals_file_info:
                this_file_info = file_info
                break
        if new_text != edit_file_message.caption:
            try:
                await bot.edit_message_caption(
                    user_id,
                    edit_file_message.message_id,
                    caption=escape_markdown(caption),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=edit_file_message.reply_markup
                )
                this_file_info['caption'] = caption
                await util_edit_item(user_id, item.id, item)
                data['edit_file_item'] = item
            except Exception as e:
                if "MEDIA_CAPTION_TOO_LONG" in str(e):
                    exception_message_text = "❗ Эта подпись слишком длинная. Придумайте другую:"
                else:
                    exception_message_text = ("❗ Не удалось сохранить эту подпись. "
                                              "Возможно что то не так с ее содержимым. Придумайте другую:")
                buttons = get_edit_file_caption_keyboard(caption)
                markup = create_general_reply_markup(buttons)
                edit_file_caption_messages.append(
                    await bot.send_message(user_id, exception_message_text, reply_markup=markup)
                )
                await state.update_data(edit_file_caption_messages=edit_file_caption_messages)
                return

    info_message = await bot.send_message(message.from_user.id, message_text, reply_markup=markup)
    await state.set_state(states.ItemState.EditFiles)


