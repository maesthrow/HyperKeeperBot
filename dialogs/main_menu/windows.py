from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format

from dialogs.general_handlers import open_main_menu_handler
from dialogs.main_menu.getters import *
from dialogs.main_menu.handlers import *
from dialogs.widgets.inline_query_button import InlineQueryButton
from handlers_pack.states import MainMenuState

start_window = Window(
    Format("{start_text}"),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=MainMenuState.Start,
    getter=get_start_data
)

main_menu_window = Window(
    Format("{message_text}"),
    Button(Format('{btn_storage}'), id="open_storage", on_click=open_storage_handler),
    Button(Format('{btn_accesses}'), id="accesses_menu", on_click=accesses_menu_handler),
    Button(Format('{btn_chatgpt}'), id="chatgpt", on_click=chatgpt_new_chat_handler),
    Button(Format('{btn_search}'), id="search_menu", on_click=search_menu_handler),
    Button(Format('{btn_profile}'), id="user_profile", on_click=user_profile_handler),
    Button(Format('{btn_settings}'), id="settings_menu", on_click=settings_menu_handler),
    Button(Format('{btn_help}'), id="help_menu", on_click=help_menu_handler),
    state=MainMenuState.Menu,
    getter=get_main_menu_data
)

quick_search_window = Window(
    Format("{message_text}"),
    InlineQueryButton(
        Format('{btn_general}'),
        id="general_search",
        switch_inline_query_current_chat=Const("")
    ),
    InlineQueryButton(
        Format('{btn_folders}'),
        id="folders_search",
        switch_inline_query_current_chat=Const("folders/")
    ),
    InlineQueryButton(
        Format('{btn_items}'),
        id="items_search",
        switch_inline_query_current_chat=Const("items/")
    ),
    InlineQueryButton(
        Format('{btn_files}'),
        id="files_search",
        switch_inline_query_current_chat=Const("files/")
    ),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=MainMenuState.QuickSearch,
    getter=get_quick_search_data
)

user_profile_window = Window(
    Format("{message_text}"),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=MainMenuState.UserProfile,
    getter=get_user_profile_data
)

help_menu_window = Window(
    Format("{message_text}"),
    Button(text=Format("{btn_contact_support}"), id="contact_support", on_click=contact_support_handler),
    Button(text=Format("{btn_menu}"), id="main_menu", on_click=open_main_menu_handler),
    state=MainMenuState.HelpMenu,
    getter=get_help_menu_data
)


dialog_main_menu = Dialog(
    start_window,
    main_menu_window,
    quick_search_window,
    user_profile_window,
    help_menu_window,
)
