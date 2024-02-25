from aiogram.enums import ContentType
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


class ShowItemFilesCallback(CallbackData, prefix="show_item_files"):
    type: str


class HideItemFilesCallback(CallbackData, prefix="hide_item_files"):
    type: str


class TextPagesCallback(CallbackData, prefix="text_pages"):
    author_user_id: int
    item_id: str
    action: str
    page: int


class RemoveTextPageCallback(TextPagesCallback, prefix="remove_text_page"):
    pass


class ChooseTypeAddText(CallbackData, prefix='choose_type_add_text'):
    type: str


class SaveItemCallback(CallbackData, prefix="=save_item"):
    author_user_id: int
    item_id: str


class ItemShowCallback(CallbackData, prefix="=item_show"):
    author_user_id: int
    item_id: str
    with_folders: bool


class EditFileCaptionCallback(CallbackData, prefix="edit_file_capt"):
    item_id: str
    type: ContentType
    file_id: str


class MarkFileCallback(CallbackData, prefix="mark_file"):
    item_id: str
    type: ContentType
    file_id: str


class DeleteFileCallback(CallbackData, prefix="delete_file"):
    item_id: str
    type: ContentType
    file_id: str


class RequestDeleteFileCallback(CallbackData, prefix="req_del_file"):
    item_id: str
    type: ContentType
    file_id: str
    res: str


class RequestDeleteFilesCallback(CallbackData, prefix="req_del_files"):
    item_id: str
    res: str
    is_all: bool
