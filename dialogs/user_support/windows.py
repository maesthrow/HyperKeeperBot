from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Format, Const

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


answer_user_contact_support_window = Window(
    Format("{message_text}"),
    TextInput(
        id="answer_user_contact_support_text",
        on_success=on_answer_user_contact_support,
    ),
    Button(
        id='cancel_answer_user_contact_support',
        text=Format('{btn_cancel}'),
        on_click=cancel_answer_user_contact_support_handler
    ),
    state=UserSupportState.AnswerUserContactSupport,
    getter=get_answer_user_contact_support_data
)

after_answer_user_contact_support_message_window = Window(
    Format("{message_text}"),
    Button(Const("Ok"), id="after_answer_user_contact_support_ok", on_click=after_answer_user_contact_support_ok_handler),
    state=UserSupportState.AfterAnswerUserContactSupport,
    getter=get_after_answer_user_contact_support_message_text
)

dialog_user_support = Dialog(
    contact_support_window,
    after_contact_support_message_window,
    answer_user_contact_support_window,
    after_answer_user_contact_support_message_window,
)
