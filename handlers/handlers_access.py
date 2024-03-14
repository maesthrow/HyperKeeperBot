from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from callbacks.callbackdata import AccessConfirmCallback
from load_all import dp, bot
from models.folder_model import Folder
from utils.utils_ import smile_folder
from utils.utils_folders_reader import get_folder
from utils.utils_parse_mode_converter import escape_markdown

router = Router()
dp.include_router(router)


@router.callback_query(AccessConfirmCallback.filter())
async def access_folder_handler(call: CallbackQuery):
    # user_id = call.from_user.id
    # call_data = AccessConfirmCallback.unpack(call.data)
    # folder_id = call_data.folder_id
    # folder: Folder = await get_folder(user_id, folder_id)
    # users_info = await folder.get_users_info() or 'Ничего не найдено.'
    # users_info = escape_markdown(users_info)
    # message_text = (f'🔐 *Управление доступом к папке*'
    #                 f'\n\n{smile_folder} {folder.name}'
    #                 f'\n\n_Пользователи, которым вы предоставили доступ:_'
    #                 f'\n\n{users_info}')
    # inline_markup = get_access_control_inline_markup(user_id, folder_id, folder.has_users())
    # await bot.send_message(
    #     chat_id=user_id, text=message_text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=inline_markup
    # )
    await call.answer()