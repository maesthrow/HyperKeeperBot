from aiogram.enums import ParseMode, ContentType
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from dialogs.general_handlers import open_main_menu_handler
from dialogs.giga_chat.getters import *
from dialogs.giga_chat.handlers import *
from dialogs.giga_chat.keyboards import *

from handlers_pack.states import GigaChatState

menu_chats_window = Window(
    Format("{message_text}"),
    Button(id='new_chat', text=Format('{btn_new_chat}'), on_click=new_chat_handler),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=GigaChatState.MenuChats,
    getter=get_menu_chats_data
)

new_chat_window = Window(
    Format("{message_text}"),
    TextInput(
        id="user_first_query_text",
        on_success=on_first_user_query,
    ),
    MessageInput(
        content_types=[ContentType.VOICE, ContentType.VIDEO_NOTE],
        func=on_first_user_voice_query
    ),
    state=GigaChatState.NewChat,
    getter=get_new_chat_data
)

query_window = Window(
    Format("{message_text}"),
    TextInput(
        id="user_query_text",
        on_success=on_user_query,
    ),
    MessageInput(
        content_types=[ContentType.VOICE, ContentType.VIDEO_NOTE],
        func=on_user_voice_query
    ),
    state=GigaChatState.Query,
    getter=get_query_data,
    parse_mode=ParseMode.MARKDOWN_V2
)

dialog_giga_chat = Dialog(
    new_chat_window,
    query_window,
    menu_chats_window,
)
