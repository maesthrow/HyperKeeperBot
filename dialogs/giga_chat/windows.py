import operator

from aiogram.enums import ParseMode, ContentType
from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Row
from aiogram_dialog.widgets.text import Format

from dialogs.general_handlers import open_main_menu_handler
from dialogs.giga_chat.getters import *
from dialogs.giga_chat.handlers import *
from dialogs.giga_chat.keyboards import *
from dialogs.widgets.custom_scrolling_group import CustomScrollingGroup

from handlers_pack.states import GigaChatState, GigaChatResumeState

menu_chats_window = Window(
    Format("{message_text}"),
    Button(id='new_chat', text=Format('{btn_new_chat}'), on_click=new_chat_handler),
    CustomScrollingGroup(
        Select(
            Format("{item[title]}"),
            id='chats_select',
            item_id_getter=operator.itemgetter('id'),
            items='chats',
            on_click=chat_selected_handler
        ),
        id='chats_scroll',
        height=5,
        width=1,
        hide_on_single_page=True
    ),
    Button(
        id='clear_chats_history',
        text=Format('{btn_clear_chats_history}'),
        on_click=clear_chats_history_handler,
        when=user_have_chats
    ),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=GigaChatState.MenuChats,
    getter=get_menu_chats_data
)

selected_chat_window = Window(
    Format("{message_text}"),
    CustomScrollingGroup(
        Select(
            Format("{item[delete_last_pair_chat_messages_text]}"),
            id='chat_text_page',
            item_id_getter=operator.itemgetter('page'),
            items='chat_pages',
            on_click=on_page_click,
        ),
        id='chat_text_pages_scroll',
        height=1,
        width=1,
        on_page_changed=on_page_changed,
        hide_on_single_page=True,
    ),
    TextInput(
        id="user_query_text",
        on_success=on_resume_chat_user_query,
    ),
    MessageInput(
        content_types=[ContentType.VOICE, ContentType.VIDEO_NOTE],
        func=on_resume_chat_user_voice_query
    ),
    state=GigaChatState.SelectedChat,
    getter=get_selected_chat_data,
    parse_mode=ParseMode.MARKDOWN_V2
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

delete_chat_window = Window(
    Format("{message_text}"),
    Row(
        Button(
            id='confirm_delete_chat',
            text=Format('{btn_confirm_delete_chat}'),
            on_click=confirm_delete_chat_handler
        ),
        Button(
            id='cancel_delete_chat',
            text=Format('{btn_cancel_delete_chat}'),
            on_click=cancel_delete_chat_handler
        ),
    ),
    state=GigaChatState.DeleteChat,
    getter=get_delete_chat_data
)

clear_chats_history_window = Window(
    Format("{message_text}"),
    Row(
        Button(
            id='confirm_clear_chats_history',
            text=Format('{btn_confirm_clear_chats_history}'),
            on_click=confirm_clear_chats_history_handler
        ),
        Button(
            id='cancel_clear_chats_history',
            text=Format('{btn_cancel_clear_chats_history}'),
            on_click=cancel_clear_chats_history_handler
        ),
    ),
    state=GigaChatState.ClearChatsHistory,
    getter=get_clear_chats_history_data
)

dialog_giga_chat = Dialog(
    new_chat_window,
    query_window,
    menu_chats_window,
    selected_chat_window,
    delete_chat_window,
    clear_chats_history_window,
)


