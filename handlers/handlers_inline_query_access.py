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
        message_text=f'Вам предоставлен доступ к просмотру папки:\n{smile_folder} {folder.name}'
                     f'\n\nОт пользователя:\n{user_info}'
    )
    #url = 'https://www.pngfind.com/pngs/m/418-4184626_unlock-your-phone-for-free-unlock-cell-phone.png'
    url = 'https://thumbs.dreamstime.com/b/%D0%BF%D1%80%D0%B5%D0%B4%D0%BE%D1%81%D1%82%D0%B0%D0%B2%D0%BB%D0%B5%D0%BD-%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF-%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D0%BE%D0%BD%D0%BD%D0%BE%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B5-%D0%BD%D0%B0-%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B5-172455026.jpg'
    result_id = hashlib.md5(f'{from_user_id}{folder_id}read'.encode()).hexdigest()
    access_read_folder_result = InlineQueryResultArticle(
        id=result_id,
        title=f'Доступ к просмотру папки',
        description=f'{smile_folder} {folder.name}',
        input_message_content=message_content,
        thumbnail_url=url
        #reply_markup=inline_markup,
        #thumbnail_url=search_icon_url,
    )
    access_results.append(access_read_folder_result)

    message_content = InputTextMessageContent(
        message_text=f'Вам предоставлен доступ к просмотру и изменению папки:\n{smile_folder} {folder.name}'
                     f'\n\nОт пользователя:\n{user_info}'
    )
    url = 'https://img3.stockfresh.com/files/s/sdecoret/m/76/6339547_stock-photo-green-binary-code.jpg'
    result_id = hashlib.md5(f'{from_user_id}{folder_id}write'.encode()).hexdigest()
    access_read_folder_result = InlineQueryResultArticle(
        id=result_id,
        title=f'Доступ к просмотру и изменению папки',
        description=f'{smile_folder} {folder.name}',
        input_message_content=message_content,
        thumbnail_url=url
        # reply_markup=inline_markup,
        # thumbnail_url=search_icon_url,
    )
    access_results.append(access_read_folder_result)

    return access_results