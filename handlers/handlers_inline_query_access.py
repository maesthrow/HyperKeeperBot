import hashlib

from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from load_all import dp, bot
from models.folder_model import Folder
from utils.utils_ import smile_folder
from utils.utils_access import get_user_info
from utils.utils_folders_reader import get_folder

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
        cache_time=60,
    )


async def get_access_results(from_user_id, folder_id):
    access_results = []

    folder: Folder = await get_folder(from_user_id, folder_id)
    user_info = await get_user_info(from_user_id)

    message_content = InputTextMessageContent(
        message_text=f'Вам предоставлен доступ к чтению папки:\n{smile_folder} {folder.name}'
                     f'\n\nОт пользователя:\n{user_info}'
    )
    result_id = hashlib.md5(f'{from_user_id}{folder_id}read'.encode()).hexdigest()
    access_read_folder_result = InlineQueryResultArticle(
        id=result_id,
        title=f'Доступ к чтению папки',
        description=folder.name,
        input_message_content=message_content,
        #reply_markup=inline_markup,
        #thumbnail_url=search_icon_url,
    )
    access_results.append(access_read_folder_result)

    message_content = InputTextMessageContent(
        message_text=f'Вам предоставлен доступ к чтению и изменению папки:\n{smile_folder} {folder.name}'
                     f'\n\nОт пользователя:\n{user_info}'
    )
    result_id = hashlib.md5(f'{from_user_id}{folder_id}write'.encode()).hexdigest()
    access_read_folder_result = InlineQueryResultArticle(
        id=result_id,
        title=f'Доступ к чтению и изменению папки',
        description=folder.name,
        input_message_content=message_content,
        # reply_markup=inline_markup,
        # thumbnail_url=search_icon_url,
    )
    access_results.append(access_read_folder_result)

    return access_results