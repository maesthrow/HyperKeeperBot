import asyncio

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode

from callbacks.callbackdata import AccessConfirmCallback, AccessConfirmOkCallback, AccessConfirmRejectCallback
from enums.enums import AccessType
from handlers.states import FolderControlStates
from load_all import dp, bot
from models.access_folder_model import AccessFolder
from models.folder_model import Folder
from utils.data_manager import get_data, set_data
from utils.message_box import MessageBox
from utils.utils_ import smile_folder
from utils.utils_access import get_user_info, get_access_str_by_type
from utils.utils_accesses_folders_db import util_access_add_from_user_folder
from utils.utils_button_manager import get_simple_inline_markup
from utils.utils_folders_reader import get_folder, get_folders_in_folder
from utils.utils_folders_writer import edit_folder
from utils.utils_parse_mode_converter import escape_markdown

router = Router()
dp.include_router(router)


# @router.callback_query(AccessConfirmCallback.filter())
# async def access_folder_handler(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
#     print(f'access_folder_handler state = {await state.get_state()}')
#     #await state.set_state(state=None)
#
#     from_user_id = call.from_user.id
#     user_info = await get_user_info(str(from_user_id))
#     call_data = AccessConfirmCallback.unpack(call.data)
#     accessing_user_id = int(call_data.acc_user_id)
#     accessing_user_info = await get_user_info(str(accessing_user_id))
#     folder_id = call_data.folder_id
#     folder: Folder = await get_folder(from_user_id, folder_id)
#     folder_full_name = await folder.get_full_name()
#     folder_full_name = escape_markdown(folder_full_name)
#     access_type = AccessType(call_data.type)
#     access_str = get_access_str_by_type(access_type)
#     result = call_data.res
#     # if result:
#     #     access_to_user_added = await util_access_add_from_user_folder(
#     #         accessing_user_id, from_user_id, folder_id, access_type
#     #     )
#     #     user_to_access_added = False
#     #     if access_to_user_added:
#     #         user_to_access_added = await add_user_to_folder_access(accessing_user_id, folder, access_type)
#     #     if access_to_user_added and user_to_access_added:
#     #         message_text = f'✅ Пользователю {accessing_user_info} предоставлен доступ {access_str} вашей папки:'
#     #         message_text = escape_markdown(message_text)
#     #         message_text += (f'\n\n*{folder_full_name} {escape_markdown('...')}*'
#     #                          f'\n\nВы можете отменить это действие в любой момент в настройках доступа папки 🔐')
#     #
#     #         accessing_user_message_text = (
#     #             f"✅ Пользователь {user_info} подтвердил ваш доступ {access_str} его папки:"
#     #             f"\n\n<b>{smile_folder} {folder.name}</b>"
#     #             f"\n\nТеперь она доступна в разделе главного <b>Меню</b>:"
#     #             f"\n🔐 <i>доступы от других пользователей</i>"
#     #         )
#     #     else:
#     #         message_text = (f'❌ Не удалось предоставить доступ пользователю '
#     #                         f'{accessing_user_info} {access_str} вашей папки:')
#     #         message_text = escape_markdown(message_text)
#     #         message_text += f'\n\n*{folder_full_name} {escape_markdown('...')}*'
#     #
#     #         accessing_user_message_text = (
#     #             f"❌ Пользователю {user_info} не удалось предоставить вам доступ {access_str} его папки:"
#     #             f"\n\n<b>{smile_folder} {folder.name}</b>"
#     #             f"\n\nДля повторного запроса вы должны получить новое предложение от этого пользователя 👤"
#     #         )
#     #
#     # else:
#     #     message_text = f'❌ Вы отклонили запрос пользователя {accessing_user_info} на доступ {access_str} вашей папки:'
#     #     message_text = escape_markdown(message_text)
#     #     message_text += f'\n\n*{folder_full_name} {escape_markdown('...')}*'
#     #
#     #     accessing_user_message_text = (
#     #         f"❌ Пользователь {user_info} отклонил ваш запрос на доступ {access_str} его папки:"
#     #         f"\n\n<b>{smile_folder} {folder.name}</b>"
#     #         f"\n\nДля повторного запроса вы должны получить новое предложение от этого пользователя 👤"
#     #     )
#
#     # bot.delete_message(
#     #     chat_id=from_user_id,
#     #     message_id=call.message.message_id,
#     # ),
#
#     if result:
#         from_user_message_text, accessing_user_message_text = await get_texts_access_folder_confirm_ok(
#             accessing_user_id, from_user_id, folder_id, access_type
#         )
#     else:
#         from_user_message_text, accessing_user_message_text = await get_texts_access_folder_confirm_reject(
#             accessing_user_id, from_user_id, folder_id, access_type
#         )
#
#     # dialog_manager.current_context().dialog_data["message_text"] = 'test'
#     # dialog_manager.dialog_data["message_text"] = 'test'
#
#     data = await get_data(from_user_id)
#     data["access_confirm_message_text"] = from_user_message_text
#     await set_data(from_user_id, data)
#     await dialog_manager.start(
#         state=FolderControlStates.AccessConfirm,
#         #data={'message_text': 'test'},
#         show_mode=ShowMode.EDIT
#     )
#
#     inline_markup = get_simple_inline_markup('✔️ OK')
#     await asyncio.gather(
#         # bot.edit_message_text(
#         #     chat_id=from_user_id,
#         #     message_id=call.message.message_id,
#         #     text=message_text,
#         #     parse_mode=ParseMode.MARKDOWN_V2,
#         #     reply_markup=inline_markup
#         # ),
#         # bot.delete_message(
#         #     chat_id=from_user_id,
#         #     message_id=call.message.message_id,
#         # ),
#         bot.send_message(
#             chat_id=accessing_user_id,
#             text=accessing_user_message_text,
#             parse_mode=ParseMode.HTML,
#             reply_markup=inline_markup
#         )
#     )
#
#     await call.answer()


@router.callback_query(AccessConfirmCallback.filter())
async def access_folder_handler(call: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    await call.answer()
    from_user_id = call.from_user.id
    call_data = AccessConfirmCallback.unpack(call.data)
    accessing_user_id = int(call_data.acc_user_id)
    folder_id = call_data.folder_id
    access_type = AccessType(call_data.type)
    result = call_data.res
    if result:
        from_user_message_text, accessing_user_message_text = await get_texts_access_folder_confirm_ok(
            accessing_user_id, from_user_id, folder_id, access_type
        )
    else:
        from_user_message_text, accessing_user_message_text = await get_texts_access_folder_confirm_reject(
            accessing_user_id, from_user_id, folder_id, access_type
        )

    await dialog_manager.start(
        state=FolderControlStates.AccessConfirm,
        show_mode=ShowMode.EDIT,
        data={"message_text": from_user_message_text}
    )
    await sent_message_to_accessing_user(accessing_user_id, accessing_user_message_text)


async def sent_message_to_accessing_user(accessing_user_id, message_text):
    inline_markup = get_simple_inline_markup('✔️ OK')
    await bot.send_message(
        chat_id=accessing_user_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_markup=inline_markup
    )


async def get_texts_access_folder_confirm_ok(accessing_user_id, from_user_id, folder_id, access_type: AccessType):
    user_info = await get_user_info(str(from_user_id))
    accessing_user_info = await get_user_info(str(accessing_user_id))
    folder: Folder = await get_folder(from_user_id, folder_id)
    folder_full_name = await folder.get_full_name()
    access_str = get_access_str_by_type(access_type)

    access_to_user_added = await util_access_add_from_user_folder(
        accessing_user_id, from_user_id, folder_id, access_type
    )
    user_to_access_added = False
    if access_to_user_added:
        user_to_access_added = await add_user_to_folder_access(accessing_user_id, folder, access_type)
    if access_to_user_added and user_to_access_added:
        message_text = f'✅ Пользователю {accessing_user_info} предоставлен доступ {access_str} вашей папки:'
        message_text += (f'\n\n<b>{folder_full_name} ...</b>'
                         f'\n\nВы можете отменить это действие в любой момент в настройках доступа папки 🔐')

        accessing_user_message_text = (
            f"✅ Пользователь {user_info} подтвердил ваш доступ {access_str} его папки:"
            f"\n\n<b>{smile_folder} {folder.name}</b>"
            f"\n\nТеперь она доступна в разделе главного <b>Меню</b>:"
            f"\n🔐 <i>доступы от других пользователей</i>"
        )
    else:
        message_text = (f'❌ Не удалось предоставить доступ пользователю '
                        f'{accessing_user_info} {access_str} вашей папки:')
        message_text += f'\n\n<v>{folder_full_name} ...</b>'

        accessing_user_message_text = (
            f"❌ Пользователю {user_info} не удалось предоставить вам доступ {access_str} его папки:"
            f"\n\n<b>{smile_folder} {folder.name}</b>"
            f"\n\nДля повторного запроса вы должны получить новое предложение от этого пользователя 👤"
        )
    return message_text, accessing_user_message_text


async def get_texts_access_folder_confirm_reject(accessing_user_id, from_user_id, folder_id, access_type: AccessType):
    user_info = await get_user_info(str(from_user_id))
    accessing_user_info = await get_user_info(str(accessing_user_id))
    folder: Folder = await get_folder(from_user_id, folder_id)
    folder_full_name = await folder.get_full_name()
    access_str = get_access_str_by_type(access_type)

    message_text = f'❌ Вы отклонили запрос пользователя {accessing_user_info} на доступ {access_str} вашей папки:'
    message_text += f'\n\n<b>{folder_full_name} ...</b>'

    accessing_user_message_text = (
        f"❌ Пользователь {user_info} отклонил ваш запрос на доступ {access_str} его папки:"
        f"\n\n<b>{smile_folder} {folder.name}</b>"
        f"\n\nДля повторного запроса вы должны получить новое предложение от этого пользователя 👤"
    )
    return message_text, accessing_user_message_text


# async def get_access_confirm_ok_messages(from_user_id):
#     data = await get_data(from_user_id)
#     access_folder_confirm: AccessFolder = data.get('access_folder_confirm', None)
#     if access_folder_confirm:
#         from_user_message_text, accessing_user_message_text = await get_texts_access_folder_confirm_ok(
#             access_folder_confirm.user_id,
#             access_folder_confirm.from_user_id,
#             access_folder_confirm.folder_id,
#             access_folder_confirm.get_access_type()
#         )
#         return from_user_message_text, accessing_user_message_text
#     return None
#
#
# async def get_access_confirm_reject_messages(from_user_id):
#     data = await get_data(from_user_id)
#     access_folder_confirm: AccessFolder = data.get('access_folder_confirm', None)
#     if access_folder_confirm:
#         from_user_message_text, accessing_user_message_text = await get_texts_access_folder_confirm_reject(
#             access_folder_confirm.user_id,
#             access_folder_confirm.from_user_id,
#             access_folder_confirm.folder_id,
#             access_folder_confirm.get_access_type()
#         )
#         return from_user_message_text, accessing_user_message_text
#     return None
#
#
# @router.callback_query(AccessConfirmOkCallback.filter())
# async def access_confirm_ok_handler(call: CallbackQuery, state: FSMContext):
#     user_id = call.from_user.id
#     from_user_message_text, accessing_user_message_text = await get_access_confirm_ok_messages(user_id)
#     await call.answer()
#     await MessageBox.show(user_id, from_user_message_text, edit_message_id=call.message.message_id)
#
#
# @router.callback_query(AccessConfirmRejectCallback.filter())
# async def access_confirm_reject_handler(call: CallbackQuery, state: FSMContext):
#     user_id = call.from_user.id
#     from_user_message_text, accessing_user_message_text = await get_access_confirm_reject_messages(user_id)
#     await call.answer()
#     await MessageBox.show(user_id, from_user_message_text, edit_message_id=call.message.message_id)


async def add_user_to_folder_access(user_id, folder: Folder, access_type: AccessType) -> bool:
    folder.add_access_user(user_id, access_type)
    return await edit_folder(folder.author_user_id, folder)


async def edit_user_to_folder_access(user_id, folder: Folder, access_type: AccessType) -> bool:
    folder.edit_access_user(user_id, access_type)
    return await edit_folder(folder.author_user_id, folder)


async def delete_user_from_folder_access(user_id, folder: Folder) -> bool:
    folder.delete_access_user(user_id)
    return await edit_folder(folder.author_user_id, folder)






