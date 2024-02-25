import asyncio
from typing import List

from aiogram.enums import ParseMode
from aiogram.types import Location, Contact, InputFile, Sticker, Document
from aiogram.utils.media_group import MediaGroupBuilder

from load_all import bot
from models.item_model import Item
from utils.ContentGroupBuilder import ContentGroupBuilder
from utils.data_manager import get_data, set_data
from utils.utils_files import dict_to_location, dict_to_contact, dict_to_sticker, dict_to_document
from utils.utils_parse_mode_converter import markdown_without_code, escape_markdown, full_escape_markdown


async def show_item_files(user_id, item: Item):
    if item.files_count() > 0:
        media_group_audio_builders = [MediaGroupBuilder()]
        media_group_photo_video_builders = [MediaGroupBuilder()] # caption=item.get_body_markdown()[:1000]
        media_group_voice_builders = [MediaGroupBuilder()]
        media_group_video_note_builders = [MediaGroupBuilder()]
        document_builders = [ContentGroupBuilder()]
        location_builders = [ContentGroupBuilder()]
        contact_builders = [ContentGroupBuilder()]
        sticker_builders = [ContentGroupBuilder()]
        await fill_builders(
            item=item,
            media_group_audio_builders=media_group_audio_builders,
            media_group_photo_video_builders=media_group_photo_video_builders,
            media_group_voice_builders=media_group_voice_builders,
            media_group_video_note_builders=media_group_video_note_builders,
            document_builders=document_builders,
            location_builders=location_builders,
            contact_builders=contact_builders,
            sticker_builders=sticker_builders
        )

        item_files_messages = []
        await send_media_group(user_id, media_group_photo_video_builders, item_files_messages)
        await send_media_group(user_id, media_group_video_note_builders, item_files_messages)
        await send_media_group(user_id, media_group_audio_builders, item_files_messages)
        await send_media_group(user_id, media_group_voice_builders, item_files_messages)
        await send_document(user_id, document_builders, item_files_messages)
        await send_locations(user_id, location_builders, item_files_messages)
        await send_contacts(user_id, contact_builders, item_files_messages)
        await send_stickers(user_id, sticker_builders, item_files_messages)

        await update_data(user_id, item_files_messages)


async def update_data(user_id, item_files_messages):
    data = await get_data(user_id)
    data['item_files_messages'] = item_files_messages
    await set_data(user_id, data)


async def send_media_group(user_id, media_group_builders, item_files_messages):
    for mg_builder in media_group_builders:
        media_group = mg_builder.build()
        if len(media_group) > 0:
            await asyncio.sleep(0.25)
            item_files_messages.append(
                await bot.send_media_group(chat_id=user_id, media=media_group)
            )


async def send_document(user_id, document_builders, item_files_messages):
    for d_builder in document_builders:
        documents = d_builder.build()
        if len(documents) > 0:
            for document in documents:
                await asyncio.sleep(0.25)
                item_files_messages.append(
                    await bot.send_document(
                        chat_id=user_id, document=document.media,
                        caption=escape_markdown(document.caption),
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                )


async def send_locations(user_id, location_builders, item_files_messages):
    for l_builder in location_builders:
        locations = l_builder.build()
        if len(locations) > 0:
            for location in locations:
                await asyncio.sleep(0.25)
                item_files_messages.append(
                    await bot.send_location(
                        chat_id=user_id,
                        latitude=location.latitude,
                        longitude=location.longitude,
                        horizontal_accuracy=location.horizontal_accuracy,
                        live_period=location.live_period,
                        heading=location.heading,
                        proximity_alert_radius=location.proximity_alert_radius
                    )
                )


async def send_contacts(user_id, contact_builders, item_files_messages):
    for c_builder in contact_builders:
        contacts = c_builder.build()
        if len(contacts) > 0:
            for contact in contacts:
                await asyncio.sleep(0.25)
                item_files_messages.append(
                    await bot.send_contact(
                        chat_id=user_id,
                        phone_number=contact.phone_number,
                        first_name=contact.first_name,
                        last_name=contact.last_name,
                        vcard=contact.vcard
                    )
                )


async def send_stickers(user_id, sticker_builders, item_files_messages):
    for s_builder in sticker_builders:
        stickers = s_builder.build()
        if len(stickers) > 0:
            for sticker in stickers:
                await asyncio.sleep(0.25)
                item_files_messages.append(
                    await bot.send_sticker(
                        chat_id=user_id,
                        sticker=sticker.file_id
                    )
                )


async def fill_builders(
        item: Item,
        media_group_audio_builders,
        media_group_photo_video_builders,
        media_group_voice_builders,
        media_group_video_note_builders,
        document_builders,
        location_builders,
        contact_builders,
        sticker_builders):

    #tasks = []

    media_group_ids = {
        'audio': None,
        'photo_video': None,
    }

    for content_type, files in item.media.items():
        for file_info in files:
            if content_type == 'document':
                document: Document = dict_to_document(file_info['fields'])
                caption = file_info['caption']
                await process_document_group(document, caption, document_builders)
            elif content_type == 'location':
                location: Location = dict_to_location(file_info['fields'])
                await process_location_group(location, location_builders)
            elif content_type == 'contact':
                contact: Contact = dict_to_contact(file_info['fields'])
                await process_contact_group(contact, contact_builders)
            elif content_type == 'sticker':
                sticker = dict_to_sticker(file_info['fields'])
                await process_sticker_group(sticker, sticker_builders)
            elif content_type == 'voice':
                await process_media_voice_group(
                    content_type='audio',
                    file_id=file_info['file_id'],
                    media_group_voice_builders=media_group_voice_builders
                )
            elif content_type == 'video_note':
                await process_media_video_note_group(
                    content_type='video',
                    file_id=file_info['file_id'],
                    media_group_video_note_builders=media_group_video_note_builders
                )
            elif content_type == 'audio':
                await process_media_audio_group(
                    content_type=content_type,
                    file_id=file_info['file_id'],
                    media_group_id=file_info['media_group_id'],
                    media_group_ids=media_group_ids,
                    caption=file_info['caption'],
                    media_group_audio_builders=media_group_audio_builders
                )
            else:
                await process_media_photo_video_group(
                    content_type=content_type,
                    file_id=file_info['file_id'],
                    media_group_id=file_info['media_group_id'],
                    media_group_ids=media_group_ids,
                    caption=file_info['caption'],
                    media_group_photo_video_builders=media_group_photo_video_builders
                )

                # tasks.append(process_media_group(content_type, file_id, media_group_builders))

    # await asyncio.gather(*tasks)


async def process_media_audio_group(
        content_type,
        file_id,
        caption,
        media_group_id,
        media_group_ids,
        media_group_audio_builders):

    last_builder = media_group_audio_builders[-1]
    if len(last_builder._media) >= 10\
            or (media_group_ids['audio'] != media_group_id
                and len(last_builder._media) > 0):
                # and caption != last_builder._media[0].caption):
        media_group_audio_builders.append(MediaGroupBuilder())

    media_group_ids['audio'] = media_group_id
    media_group_audio_builders[-1].add(type=content_type, media=str(file_id), caption=caption)


async def process_media_photo_video_group(
        content_type,
        file_id,
        media_group_id,
        media_group_ids,
        caption,
        media_group_photo_video_builders):

    last_builder = media_group_photo_video_builders[-1]
    if len(last_builder._media) >= 10\
            or (media_group_ids['photo_video'] != media_group_id
                and len(last_builder._media) > 0):
                #and caption != last_builder._media[0].caption):
        media_group_photo_video_builders.append(MediaGroupBuilder())

    media_group_ids['photo_video'] = media_group_id

    caption = escape_markdown(caption) if caption else caption
    if content_type == 'photo':
        media_group_photo_video_builders[-1].add_photo(
            media=str(file_id), caption=caption, parse_mode=ParseMode.MARKDOWN_V2
        )
    elif content_type == 'video':
        media_group_photo_video_builders[-1].add_video(
            media=str(file_id), caption=caption, parse_mode=ParseMode.MARKDOWN_V2
        )


async def process_media_voice_group(content_type, file_id, media_group_voice_builders):
    if len(media_group_voice_builders[-1]._media) >= 10:
        media_group_voice_builders.append(MediaGroupBuilder())
    media_group_voice_builders[-1].add(type=content_type, media=str(file_id))


async def process_media_video_note_group(content_type, file_id, media_group_video_note_builders):
    if len(media_group_video_note_builders[-1]._media) >= 10:
        media_group_video_note_builders.append(MediaGroupBuilder())
    media_group_video_note_builders[-1].add(type=content_type, media=str(file_id))


async def process_document_group(document: Document, caption, document_builders: List[ContentGroupBuilder]):
    if len(document_builders[-1]._media) >= 10:
        document_builders.append(ContentGroupBuilder())
    document_builders[-1].add('document', document, caption=caption)


async def process_location_group(location: Location, location_builders):
    if len(location_builders[-1]._media) >= 10:
        location_builders.append(ContentGroupBuilder())
    location_builders[-1].add_location(location)


async def process_contact_group(contact: Contact, contact_builders):
    if len(contact_builders[-1]._media) >= 10:
        contact_builders.append(ContentGroupBuilder())
    contact_builders[-1].add_contact(contact)


async def process_sticker_group(sticker: Sticker, sticker_builders):
    if len(sticker_builders[-1]._media) >= 10:
        sticker_builders.append(ContentGroupBuilder())
    sticker_builders[-1].add_sticker(sticker)
