from aiogram.types import Message, Location, Contact, Document, Sticker


def get_file_id_by_content_type(message: Message):
    content_type = message.content_type
    file_id = None
    if content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif content_type == 'video':
        file_id = message.video.file_id
    elif content_type == 'audio':
        file_id = message.audio.file_id
    elif content_type == 'document':
        file_id = document_to_dict(message.document)
    elif content_type == 'voice':
        file_id = message.voice.file_id
    elif content_type == 'video_note':
        file_id = message.video_note.file_id
    elif content_type == 'location':
        file_id = location_to_dict(message.location)
    elif content_type == 'contact':
        file_id = contact_to_dict(message.contact)
    elif content_type == 'sticker':
        file_id = sticker_to_dict(message.sticker)
        print(f"message.sticker.file_id {file_id}")
    return file_id


def document_to_dict(document: Document):
    return {
        'file_id': document.file_id,
        'file_name': document.file_name,
        'mime_type': document.mime_type
    }


def dict_to_document(document_dict: dict):
    return Document(**document_dict)


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