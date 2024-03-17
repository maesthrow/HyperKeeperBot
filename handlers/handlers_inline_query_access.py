import hashlib

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from load_all import dp, bot
from models.folder_model import Folder
from models.item_model import INVISIBLE_CHAR
from utils.utils_ import smile_folder
from utils.utils_access import get_user_info, get_access_str_by_type
from utils.utils_bot import get_bot_link, get_bot_name
from utils.utils_button_manager import get_access_provide_inline_markup
from utils.utils_folders_reader import get_folder
from utils.utils_folders_writer import edit_folder

router = Router()
dp.include_router(router)


@router.inline_query(lambda query: query.query.startswith('access_'))
async def inline_query_search_folders(query: InlineQuery):
    query_data = query.query
    query_user_id = query.from_user.id
    print(f'query_user_id {query_user_id}')
    from_user_id, folder_id = query_data.split('_')[1:]
    print(f'from_user_id {from_user_id}')
    print(f'folder_id {folder_id}')
    search_results_folders = await get_access_results(from_user_id, folder_id)
    await bot.answer_inline_query(
        query.id,
        results=search_results_folders,
        cache_time=0,
    )


async def get_access_results(from_user_id, folder_id):
    access_results = []

    folder: Folder = await get_folder(from_user_id, folder_id)
    token = folder.new_token()
    result = await edit_folder(from_user_id, folder)
    if not result:
        print('edit_folder failed')
        return access_results
    else:
        print('edit_folder success')

    message_text = await get_notify_message_text(from_user_id, folder.name, 'read')
    message_content = InputTextMessageContent(
        message_text=message_text
    )
    bot_link = await get_bot_link()
    inline_markup = get_access_provide_inline_markup(from_user_id, folder_id, 'read', token, bot_link)
    #url = 'https://www.pngfind.com/pngs/m/418-4184626_unlock-your-phone-for-free-unlock-cell-phone.png'
    url = 'https://clickfraud.ru/wp-content/uploads/2023/09/alex-chumak-zguburggmdy-unsplash-scaled-1-1024x612.jpg'
    result_id = hashlib.md5(f'{from_user_id}{folder_id}read'.encode()).hexdigest()
    access_read_folder_result = InlineQueryResultArticle(
        id=result_id,
        description=f'Доступ к просмотру содержимого папки 👓',
        title=f'{smile_folder} {folder.name}',
        input_message_content=message_content,
        thumbnail_url=url,
        reply_markup=inline_markup,
        #thumbnail_url=search_icon_url,
    )
    access_results.append(access_read_folder_result)

    message_text = await get_notify_message_text(from_user_id, folder.name, 'write')
    message_content = InputTextMessageContent(
        message_text=message_text
    )
    inline_markup = get_access_provide_inline_markup(from_user_id, folder_id, 'write', token, bot_link)
    url = 'https://besthqwallpapers.com/Uploads/24-7-2020/138345/thumb2-digital-technology-background-with-zeros-and-ones-digital-blue-background-binary-code-background-digital-data-binary-code-texture.jpg'
    result_id = hashlib.md5(f'{from_user_id}{folder_id}write'.encode()).hexdigest()
    access_write_folder_result = InlineQueryResultArticle(
        id=result_id,
        description=f'Доступ к просмотру и изменению содержимого папки 👓🖊️',
        title=f'{smile_folder} {folder.name}',
        input_message_content=message_content,
        thumbnail_url=url,
        reply_markup=inline_markup,
        # thumbnail_url=search_icon_url,
    )
    access_results.append(access_write_folder_result)

    return access_results


async def get_notify_message_text(from_user_id, folder_name: str, access_type: str) -> str:
    access_str = get_access_str_by_type(access_type)
    user_info = await get_user_info(from_user_id)
    bot_name = await get_bot_name()
    message_text = (f'Вас приветствует бот {bot_name}'
                    f'\n\nПользователь {user_info} хочет предоставить вам доступ {access_str} его папки:'
                    f'\n\n<b>{smile_folder} {folder_name}</b>\n{INVISIBLE_CHAR}')
    return message_text
