import asyncio

from aiogram.enums import ParseMode, ContentType
from aiogram.types import InlineKeyboardMarkup, Location, Contact

from enums.enums import AccessType
from handlers.handlers_folder import show_folders
from handlers.handlers_item import show_item
from load_all import bot
from models.folder_model import Folder
from utils.data_manager import get_data, set_data
from utils.message_box import MessageBox
from utils.utils_ import smile_folder
from utils.utils_access import get_user_info, get_access_str_by_type
from utils.utils_access_folders_reader import get_current_access_type_from_user_folder
from utils.utils_bot import from_url_data
from utils.utils_button_manager import get_access_request_inline_markup, save_file_buttons, \
    get_access_confirm_inline_markup
from utils.utils_file_finder import FileFinder
from utils.utils_files import dict_to_location, dict_to_contact
from utils.utils_folders_reader import get_folder
from utils.utils_folders_writer import edit_folder
from utils.utils_items_reader import get_folder_id
from utils.utils_parse_mode_converter import escape_markdown
from utils.utils_show_item_entities import show_item_full_mode, show_item_page_as_text_only


async def start_url_data_access_provide_handler(message, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        # await start_handler(message, state, tg_user)
        url_data = from_url_data(message.text).split()[1]
        url_data_split = url_data.split('_')
        author_user_id = int(url_data_split[1])
        folder_id = url_data_split[2]
        access_type = AccessType(url_data_split[3])
        token = url_data_split[4]

        if author_user_id == tg_user.id:
            await show_folders(user_id=tg_user.id, current_folder_id=folder_id, need_to_resend=True)
        else:
            author_user_chat_member = await bot.get_chat_member(author_user_id, author_user_id)
            print(f'author_user = {author_user_chat_member.user}')
            user_info = await get_user_info(str(tg_user.id))
            author_user_info = await get_user_info(str(author_user_id))

            folder: Folder = await get_folder(author_user_id, folder_id)
            is_valid_token = folder.use_token(token)
            if is_valid_token:
                await edit_folder(author_user_id, folder)
                # inline_markup = get_access_request_inline_markup(author_user_id, folder_id)
                inline_markup = get_access_confirm_inline_markup(str(tg_user.id), folder_id, access_type)
                if folder:
                    folder_full_name = await folder.get_full_name()
                    folder_full_name = escape_markdown(folder_full_name)
                    access_str = get_access_str_by_type(access_type)

                    current_access_type_folder = await get_current_access_type_from_user_folder(
                        tg_user.id, author_user_id, folder_id
                    )
                    print(f'current_access_type_folder.value = {current_access_type_folder.value}')
                    print(f'access_type.value = {access_type.value}')
                    if current_access_type_folder.value >= access_type.value:
                        author_user_message_text = (
                            f"\n\nПользователь {user_info} "
                            f"уже имеет доступ {access_str} вашей папки:"
                        )
                        author_user_message_text = escape_markdown(author_user_message_text)
                        author_user_message_text += (f"\n\n*{folder_full_name} {escape_markdown('...')}*"
                                                     f"\n\nВы можете менять это в настройках доступа папки 🔐")
                        await MessageBox.show(author_user_id, author_user_message_text, parse_mode=ParseMode.MARKDOWN_V2)

                        message_text = (
                            f"Пользователь {author_user_info} "
                            f"ранее уже предоставил вам доступ {access_str} его папки:"                            
                            f"\n\n<b>{smile_folder} {folder.name}</b>"                           
                            f"\n\nВы можете найти папку в разделе главного <b>Меню</b>:"
                            f"\n🔐 <i>доступы от других пользователей</i>"
                        )
                        await MessageBox.show(tg_user.id, message_text)

                    else:
                        author_user_message_text = (
                            f"\n\nПользователь {user_info} "
                            f"запрашивает доступ {access_str} вашей папки:"
                        )
                        author_user_message_text = escape_markdown(author_user_message_text)
                        author_user_message_text += (f"\n\n*{folder_full_name} {escape_markdown('...')}*"
                                         f"\n\n_Подтверждаете предоставление доступа?_ 🔐")

                        await bot.send_message(
                            chat_id=author_user_id,
                            text=author_user_message_text,
                            parse_mode=ParseMode.MARKDOWN_V2,
                            reply_markup=inline_markup
                        )

                        message_text = (
                            f"\n\nПользователю {author_user_info} "
                            f"отправлен запрос на подтверждение доступа {access_str} его папки:"
                            f"\n\n<b>{smile_folder} {folder.name}</b>"
                            f"\n\nВы получите доступ сразу после его подтверждения ✅"
                            f"\nЯ обязательно пришлю вам уведомление🔔️"
                        )
                        await MessageBox.show(tg_user.id, message_text)

            elif not is_valid_token:
                await MessageBox.show(
                    user_id=tg_user.id,
                    message_text=f'⚠️ Запрос на доступ к папке по этому предложению уже был отправлен '
                                 f'пользователю {author_user_info}'
                                 f'\n\nПожалуйста, дождитесь подтверждения или нового предложения.')

        data = await get_data(tg_user.id)
        await asyncio.sleep(0.5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)

    else:
        await bot.delete_message(tg_user.id, message.message_id)


async def start_url_data_folder_handler(message, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        # await start_handler(message, state, tg_user)
        url_data = from_url_data(message.text).split()[1]
        url_data_split = url_data.split('_')
        author_user_id = int(url_data_split[0])
        folder_id = url_data_split[1]

        if author_user_id == tg_user.id:
            await show_folders(user_id=tg_user.id, current_folder_id=folder_id, need_to_resend=True)
        else:
            author_user_chat_member = await bot.get_chat_member(author_user_id, author_user_id)
            print(f'author_user = {author_user_chat_member.user}')
            inline_markup = get_access_request_inline_markup(author_user_id, folder_id)
            author_user_info = await get_user_info(str(author_user_id))
            await bot.send_message(
                chat_id=tg_user.id,
                text=f"*У вас нет доступа* 🙅‍♂️"
                     f"\n\nПапка, которую вы пытаетесь открыть, "
                     f"принадлежит пользователю {author_user_info}"
                     f"\n\n_Вы можете запросить у него доступ_ 🔐",
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=inline_markup
            )

        data = await get_data(tg_user.id)
        await asyncio.sleep(0.5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)

    else:
        await bot.delete_message(tg_user.id, message.message_id)


async def start_url_data_item_handler(message, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        # await start_handler(message, state, tg_user)
        url_data = from_url_data(message.text).split()[1]
        url_data_split = url_data.split('_')
        author_user_id = int(url_data_split[1])
        item_id = url_data_split[2]
        page = int(url_data_split[3])
        if page == -1:
            if author_user_id != tg_user.id:
                await show_item_full_mode(
                    user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id
                )
            else:
                folder_id = get_folder_id(item_id)
                await show_folders(user_id=tg_user.id, current_folder_id=folder_id, need_to_resend=True)
                await show_item(tg_user.id, item_id)
        else:
            await show_item_page_as_text_only(
                user_id=message.from_user.id, author_user_id=author_user_id, item_id=item_id, page=page
            )

        data = await get_data(tg_user.id)
        await asyncio.sleep(0.5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)

    else:
        await bot.delete_message(tg_user.id, message.message_id)


async def start_url_data_file_handler(message, state, tg_user):
    await asyncio.sleep(0.3)
    data = await get_data(tg_user.id)
    author_user_id = data.get('author_user_id', None)
    print(f"author_user_id {author_user_id}")
    if not author_user_id:
        data['author_user_id'] = author_user_id
        await set_data(user_id=tg_user.id, data=data)
        # await start_handler(message, state, tg_user)

        url_data = from_url_data(message.text).split()[1]
        print(f"url_data = {url_data}")
        url_data_split = url_data.split('_')

        author_user_id = int(url_data_split[1])
        item_id = url_data_split[2]
        page = int(url_data_split[3])
        short_file_id = url_data[-8:]
        str_content_type = url_data[:-8].split('_')[-2]
        if str_content_type == 'video-note':
            str_content_type = 'video_note'
        file_type: ContentType = ContentType(str_content_type)
        file_info = await FileFinder.get_file_info_in_item_by_short_file_id(author_user_id, item_id, file_type,
                                                                            short_file_id)
        file_id = FileFinder.get_file_id(file_info)
        caption = file_info['caption']

        inline_markup = InlineKeyboardMarkup(inline_keyboard=save_file_buttons)

        if file_type == 'document':
            await bot.send_document(chat_id=tg_user.id, document=file_id, caption=caption,
                                    parse_mode=ParseMode.MARKDOWN_V2, reply_markup=inline_markup)
        elif file_type == 'photo':
            await bot.send_photo(chat_id=tg_user.id, photo=file_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2,
                                 reply_markup=inline_markup)
        elif file_type == 'audio':
            await bot.send_audio(chat_id=tg_user.id, audio=file_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2,
                                 reply_markup=inline_markup)
        elif file_type == 'voice':
            await bot.send_voice(chat_id=tg_user.id, voice=file_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2,
                                 reply_markup=inline_markup)
        elif file_type == 'video':
            await bot.send_video(chat_id=tg_user.id, video=file_id, caption=caption, parse_mode=ParseMode.MARKDOWN_V2,
                                 reply_markup=inline_markup)
        elif file_type == 'video_note':
            await bot.send_video_note(chat_id=tg_user.id, video_note=file_id, reply_markup=inline_markup)
        elif file_type == 'sticker':
            await bot.send_sticker(chat_id=tg_user.id, sticker=file_id, reply_markup=inline_markup)
        elif file_type == 'location':
            location: Location = dict_to_location(file_info['fields'])
            await bot.send_location(
                chat_id=tg_user.id,
                latitude=location.latitude,
                longitude=location.longitude,
                horizontal_accuracy=location.horizontal_accuracy,
                live_period=location.live_period,
                heading=location.heading,
                proximity_alert_radius=location.proximity_alert_radius,
                reply_markup=inline_markup
            )
        elif file_type == 'contact':
            contact: Contact = dict_to_contact(file_info['fields'])
            await bot.send_contact(
                chat_id=tg_user.id,
                phone_number=contact.phone_number,
                first_name=contact.first_name,
                last_name=contact.last_name,
                vcard=contact.vcard,
                reply_markup=inline_markup
            )
            # await bot.send_contact(chat_id=tg_user.id, latitude=None, longitude=None, reply_markup=inline_markup)

        await asyncio.sleep(0.5)
        data['author_user_id'] = None
        await set_data(user_id=tg_user.id, data=data)
    else:
        await bot.delete_message(tg_user.id, message.message_id)
