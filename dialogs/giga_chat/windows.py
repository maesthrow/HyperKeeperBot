from aiogram.enums import ParseMode
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from dialogs.giga_chat.getters import *
from dialogs.giga_chat.handlers import *

from handlers_pack.states import GigaChatState

new_chat_window = Window(
    Format("{message_text}"),
    TextInput(
        id="user_first_request_text",
        on_success=on_first_user_request,
    ),
    Button(id='stop_chat', text=Format('{btn_stop_chat}'), on_click=stop_chat_handler),
    #Button(id='back_contact_support', text=Format('{btn_back}'), on_click=back_contact_support_handler),
    state=GigaChatState.NewChat,
    getter=get_new_chat_data
)

request_window = Window(
Format("{message_text}"),
    TextInput(
        id="user_request_text",
        on_success=on_user_request,
    ),
    Button(id='stop_chat', text=Format('{btn_stop_chat}'), on_click=stop_chat_handler),
    state=GigaChatState.Request,
    getter=get_request_data,
    parse_mode=ParseMode.MARKDOWN_V2
)

dialog_giga_chat = Dialog(
    new_chat_window,
    request_window,
)
