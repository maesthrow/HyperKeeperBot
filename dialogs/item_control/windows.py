from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.text import Format

from dialogs.item_control.getters import get_show_item_data
from dialogs.widgets.inline_query_button import InlineQueryButton
from handlers_pack.states import ItemControlState

from dialogs.item_control.handlers import *

show_item_window = Window(
    Format("{message_text}"),
    InlineQueryButton(Format('{btn_share}'), id="item_share"),
    Button(Format('{btn_close}'), id="item_close", on_click=item_close_handler),
    Button(Format('{btn_add}'), id="item_add", on_click=item_add_handler),
    Button(Format('{btn_edit}'), id="item_edit", on_click=item_edit_handler),
    Button(Format('{btn_move}'), id="item_move", on_click=item_move_handler),
    Button(Format('{btn_delete}'), id="item_delete", on_click=item_delete_handler),
    state=ItemControlState.ShowItem,
    getter=get_show_item_data
)


dialog_item_control = Dialog(
    show_item_window,
)
