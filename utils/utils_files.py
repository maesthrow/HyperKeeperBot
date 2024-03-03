import hashlib

from aiogram.types import Message, Location, Contact, Document, Sticker, Audio

from utils.utils_parse_mode_converter import preformat_text


def get_file_info_by_content_type(message: Message, page: int = -1):
    content_type = message.content_type
    file_info = {
        'file_id': None,
        'media_group_id': message.media_group_id,
        'fields': None,
        'caption': preformat_text(message.caption, message.caption_entities),
        'page': page
    }
    print(f'file_info[caption] = {file_info['caption']}')
    if content_type == 'photo':
        file_info['file_id'] = message.photo[-1].file_id
    elif content_type == 'video':
        file_info['file_id'] = message.video.file_id
    elif content_type == 'audio':
        file_info['fields'] = audio_to_dict(message.audio)
    elif content_type == 'document':
        file_info['fields'] = document_to_dict(message.document)
    elif content_type == 'voice':
        file_info['file_id'] = message.voice.file_id
    elif content_type == 'video_note':
        file_info['file_id'] = message.video_note.file_id
    elif content_type == 'location':
        longitude = message.location.longitude
        latitude = message.location.latitude
        file_info['file_id'] = hashlib.md5(f'{longitude}{latitude}'.encode()).hexdigest()
        file_info['fields'] = location_to_dict(message.location)
    elif content_type == 'contact':
        contact = message.contact
        file_info['file_id'] = hashlib.md5(f'{contact.user_id}'.encode()).hexdigest()
        file_info['fields'] = contact_to_dict(message.contact)
    elif content_type == 'sticker':
        file_info['fields'] = sticker_to_dict(message.sticker)
        # print(f"message.sticker.file_id {file_info}")
    return file_info


def document_to_dict(document: Document):
    return {
        'file_id': document.file_id,
        'file_unique_id': document.file_unique_id,
        'file_name': document.file_name,
        'mime_type': document.mime_type
    }


def dict_to_document(document_dict: dict):
    return Document(**document_dict)


def audio_to_dict(audio: Audio):
    return {
        'file_id': audio.file_id,
        'file_unique_id': audio.file_unique_id,
        'duration': audio.duration,
        'performer': audio.performer,
        'title': audio.title,
        'file_name': audio.file_name,
        'mime_type': audio.mime_type,
        'file_size': audio.file_size,
        'thumbnail': audio.thumbnail
    }


def dict_to_audio(audio_dict: dict):
    audio: Audio = Audio(
        file_id=audio_dict['file_id'],
        file_unique_id=audio_dict['file_unique_id'],
        duration=audio_dict['duration'],
        performer=audio_dict['performer'],
        title=audio_dict['title'],
        file_name=audio_dict['file_name'],
        mime_type=audio_dict['mime_type'],
        file_size=audio_dict['file_size'],
    )
    return audio


def location_to_dict(location: Location):
    return {
        "longitude": location.longitude,
        "latitude": location.latitude,
        "horizontal_accuracy": location.horizontal_accuracy,
        "live_period": location.live_period,
        "heading": location.heading,
        "proximity_alert_radius": location.proximity_alert_radius
    }


def dict_to_location(location_dict: dict):
    return Location(**location_dict)


def contact_to_dict(contact: Contact):
    return {
        'phone_number': contact.phone_number,
        'first_name': contact.first_name,
        'last_name': contact.last_name,
        'user_id': contact.user_id,
        'vcard': contact.vcard
    }


def dict_to_contact(contact_dict: dict):
    return Contact(**contact_dict)


def sticker_to_dict(sticker: Sticker):
    return {
        "file_id": sticker.file_id,
        "file_unique_id": sticker.file_unique_id,
        "type": sticker.type,
        "width": sticker.width,
        "height": sticker.height,
        "is_animated": sticker.is_animated,
        "is_video": sticker.is_video,
        "emoji": sticker.emoji,
        "set_name": sticker.set_name,
        "custom_emoji_id": sticker.custom_emoji_id,
        "needs_repainting": sticker.needs_repainting,
        "file_size": sticker.file_size
    }


def dict_to_sticker(sticker_dict: dict):
    return Sticker(**sticker_dict)
