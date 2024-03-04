import hashlib
from datetime import datetime

from aiogram.enums import ContentType, ParseMode
from aiogram.types import InlineQueryResult, InlineQueryResultDocument, InlineQueryResultPhoto, InputMediaAudio, \
    InlineQueryResultAudio, InlineQueryResultVoice, InlineQueryResultVideo, InlineQueryResultCachedSticker, Location, \
    InlineQueryResultLocation, Contact, InlineQueryResultContact

from load_all import bot
from utils.utils_files import dict_to_location, dict_to_contact


def get_result_id(file_type, file_id):
    return hashlib.md5(f'{file_type}{file_id}{datetime.now()}'.encode()).hexdigest()


async def get_inline_query_result(file_type: ContentType, file_id, file_info, inline_markup_media) -> InlineQueryResult:
    result = InlineQueryResult
    caption = file_info['caption']
    if file_type == 'document':
        file_name = file_info['fields'].get('file_name')
        mime_type = file_info['fields'].get('mime_type')
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultDocument(
            id=result_id,
            title=file_name,
            document_url=file_id,
            caption=caption,
            description=caption,
            mime_type=mime_type,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'photo':
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultPhoto(
            id=result_id,
            photo_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            title=caption,
            caption=caption,
            description=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'audio':
        file: InputMediaAudio = await bot.get_file(file_id)
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultAudio(
            id=result_id,
            audio_url=file_id,
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'voice':
        file = await bot.get_file(file_id)
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultVoice(
            id=result_id,
            voice_url=file_id,
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'video':
        file = await bot.get_file(file_id)
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultVideo(
            id=result_id,
            video_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            mime_type='video/mp4',
            title=file.file_path,
            description=caption,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'video_note':
        file = await bot.get_file(file_id)
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultVideo(
            id=result_id,
            video_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            mime_type='video/mp4',
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'sticker':
        sticker = await bot.get_file(file_id)
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultCachedSticker(
            id=result_id,
            sticker_file_id=sticker.file_id,
            reply_markup=inline_markup_media
        )
    elif file_type == 'location':
        location_dict = file_info['fields']
        location: Location = dict_to_location(location_dict)
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultLocation(
            id=result_id,
            latitude=location.latitude,
            longitude=location.longitude,
            title="📍",
            reply_markup=inline_markup_media
        )
    elif file_type == 'contact':
        contact_dict = file_info['fields']
        contact: Contact = dict_to_contact(contact_dict)
        result_id = get_result_id(file_type, file_id)
        result = InlineQueryResultContact(
            id=result_id,
            phone_number=contact.phone_number,
            first_name=contact.first_name,
            last_name=contact.last_name,
            vcard=contact.vcard,
            reply_markup=inline_markup_media
        )
    return result
