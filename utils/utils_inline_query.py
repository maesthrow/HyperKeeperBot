import hashlib

from aiogram.enums import ContentType, ParseMode
from aiogram.types import InlineQueryResult, InlineQueryResultDocument, InlineQueryResultPhoto, InputMediaAudio, \
    InlineQueryResultAudio, InlineQueryResultVoice, InlineQueryResultVideo, InlineQueryResultCachedSticker, Location, \
    InlineQueryResultLocation, Contact, InlineQueryResultContact

from load_all import bot
from utils.utils_files import dict_to_location, dict_to_contact


async def get_inline_query_result(file_type: ContentType, file_id, file_info, inline_markup_media) -> InlineQueryResult:
    result = InlineQueryResult
    caption = file_info['caption']
    if file_type == 'document':
        file_name = file_info['fields'].get('file_name')
        mime_type = file_info['fields'].get('mime_type')
        result = InlineQueryResultDocument(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            title=file_name,
            document_url=file_id,
            caption=caption,
            description=caption,
            mime_type=mime_type,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'photo':
        result = InlineQueryResultPhoto(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            photo_url=file_id,
            thumb_url=file_id,
            thumbnail_url=file_id,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'audio':
        file: InputMediaAudio = await bot.get_file(file_id)
        result = InlineQueryResultAudio(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            audio_url=file_id,
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'voice':
        file = await bot.get_file(file_id)
        result = InlineQueryResultVoice(
            id=hashlib.md5(file_id.encode()).hexdigest(),
            voice_url=file_id,
            title=file.file_path,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=inline_markup_media
        )
    elif file_type == 'video':
        file = await bot.get_file(file_id)
        result = InlineQueryResultVideo(
            id=hashlib.md5(file_id.encode()).hexdigest(),
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
        result = InlineQueryResultVideo(
            id=hashlib.md5(file_id.encode()).hexdigest(),
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
        result = InlineQueryResultCachedSticker(
            id=hashlib.md5(sticker.file_id.encode()).hexdigest(),
            sticker_file_id=sticker.file_id,
            reply_markup=inline_markup_media
        )
    elif file_type == 'location':
        location_dict = file_info['fields']
        location: Location = dict_to_location(location_dict)
        result = InlineQueryResultLocation(
            id=hashlib.md5((str(location.latitude) + str(location.longitude)).encode()).hexdigest(),
            latitude=location.latitude,
            longitude=location.longitude,
            title="📍",
            reply_markup=inline_markup_media
        )
    elif file_type == 'contact':
        contact_dict = file_info['fields']
        contact: Contact = dict_to_contact(contact_dict)
        result = InlineQueryResultContact(
            id=hashlib.md5(contact.phone_number.encode()).hexdigest(),
            phone_number=contact.phone_number,
            first_name=contact.first_name,
            last_name=contact.last_name,
            vcard=contact.vcard,
            reply_markup=inline_markup_media
        )
    return result
