import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from handlers_pack.states import MainMenuState
from load_all import bot


async def open_main_menu_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    start_data = dialog_manager.current_context().start_data
    start_message: Message = start_data.get('start_message', None) if start_data else None
    tasks = [
        dialog_manager.start(MainMenuState.Menu),  # , show_mode=ShowMode.EDIT)
        try_delete_message(start_message)
    ]
    await asyncio.gather(*tasks)


async def try_delete_message(delete_message: Message):
    if delete_message:
        try:
            await bot.delete_message(delete_message.chat.id, delete_message.message_id)
        except:
            pass