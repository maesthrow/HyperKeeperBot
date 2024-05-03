from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from handlers_pack.states import MainMenuState, UserSupportState

from dialogs.user_support.getters import *
from dialogs.user_support.handlers import *

contact_support_window = Window(
    Format("{message_text}"),
    TextInput(
        id="contact_support_text",
        on_success=on_contact_support,
    ),
    Button(id='cancel_contact_support', text=Format('{btn_cancel}'), on_click=cancel_contact_support_handler),
    state=UserSupportState.ContactSupport,
    getter=get_contact_support_data
)

after_contact_support_message_window = Window(
    Format("{message_text}"),
    Button(Const("Ok"), id="after_contact_support_ok", on_click=after_contact_support_ok_handler),
    state=UserSupportState.AfterContactSupport,
    getter=get_after_contact_support_message_text
)


dialog_user_support = Dialog(
    contact_support_window,
    after_contact_support_message_window,
)
