import asyncio

from aiogram.types import Location
from aiogram.utils.media_group import MediaGroupBuilder

from load_all import bot
from models.item_model import Item
from utils.ContentGroupBuilder import ContentGroupBuilder
from utils.data_manager import get_data, set_data
from utils.utils_files import dict_to_location


async def show_item_files(user_id, item: Item):
    media_files = await item.get_all_media_values()
    if len(media_files) > 0:
        media_group_builders = [MediaGroupBuilder()]
        location_builders = [ContentGroupBuilder()]
        await fill_builders(
            item=item,
            media_group_builders=media_group_builders,
            location_builders=location_builders
        )

        item_files_messages = []
        await send_media_group(user_id, media_group_builders, item_files_messages)
        await send_locations(user_id, location_builders, item_files_messages)

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


async def send_video_notes(user_id, video_note_builders, item_files_messages):
    for vn_builder in video_note_builders:
        video_notes = vn_builder.build()
        if len(video_notes) > 0:
            for video_note in video_notes:
                await asyncio.sleep(0.25)
                item_files_messages.append(
                    await bot.send_video_note(chat_id=user_id, video_note=video_note)
                )


async def fill_builders(item: Item, media_group_builders, location_builders):
    tasks = []
    for content_type, files in item.media.items():
        for file_id in files:
            if content_type == 'location':
                location: Location = dict_to_location(file_id)
                await process_location_group(location, location_builders)
            else:
                if content_type == 'voice':
                    content_type = 'audio'
                elif content_type == 'video_note':
                    content_type = 'video'
                await process_media_group(content_type, file_id, media_group_builders)

                # tasks.append(process_media_group(content_type, file_id, media_group_builders))

    # await asyncio.gather(*tasks)


async def process_media_group(content_type, file_id, media_group_builders):
    if len(media_group_builders[-1]._media) >= 10:
        media_group_builders.append(MediaGroupBuilder())
    media_group_builders[-1].add(type=content_type, media=str(file_id))


async def process_location_group(location: Location, location_builders):
    if len(location_builders[-1]._media) >= 10:
        location_builders.append(ContentGroupBuilder())
    location_builders[-1].add_location(location)


async def process_video_note(file_id, video_note_builders):
    if len(video_note_builders[-1]._media) >= 10:
        video_note_builders.append(MediaGroupBuilder())
    video_note_builders[-1].add_video_note(file_id)
