import asyncio

from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from dialogs.handlers import try_delete_message
from handlers_pack.states import MainMenuState, AccessesStates
from load_all import bot


async def open_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    start_data = dialog_manager.current_context().start_data
    start_message: Message = start_data.get('start_message', None) if start_data else None
    tasks = [
        dialog_manager.start(MainMenuState.Menu),  # , show_mode=ShowMode.EDIT)
        try_delete_message(start_message)
    ]
    await asyncio.gather(*tasks)


async def close_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await callback.message.delete()


async def open_storage_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def accesses_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    start_message = await bot.send_message(dialog_manager.event.from_user.id, '🔐', reply_markup=ReplyKeyboardRemove())
    await dialog_manager.start(
        AccessesStates.UsersMenu,
        show_mode=ShowMode.DELETE_AND_SEND,
        data={
            'start_message': start_message,
        }
    )


async def search_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MainMenuState.LiveSearch)


async def user_profile_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def settings_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def help_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass
