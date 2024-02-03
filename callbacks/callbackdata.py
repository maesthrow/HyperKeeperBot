from aiogram.filters.callback_data import CallbackData

from models.item_model import Item


class FolderCallback(CallbackData, prefix="folder"):
    folder_id: str


class DeleteFolderRequestCallback(CallbackData, prefix="delete_folder_request"):
    is_confirmed: bool


class InlineQueryCallback(CallbackData, prefix="inline_query"):
    action: str
    autor_user_id: int
    item_id: str


class SendItemCallback(CallbackData, prefix="=send_item"):
    author_user_id: int
    item_id: str


class SwitchInlineQueryCallback(CallbackData, prefix="switch_inline_query"):
    author_user_id: int
    item_id: str
    file_id: str