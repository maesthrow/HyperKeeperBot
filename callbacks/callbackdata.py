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
    page: int


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


class VoiceSaveTypeCallback(CallbackData, prefix='voice_save_type'):
    type: str


class ReadVoiceRunCallback(CallbackData, prefix='voice_read_retry'):
    pass


class MessageBoxCallback(CallbackData, prefix='message_box'):
    result: str


class BackToStandardFolderView(CallbackData, prefix='back_to_standard_folder_view'):
    page_folder: int
    page_item: int


class EditFolderCallback(CallbackData, prefix='edit_folder'):
    folder_id: str
    action: str


class StatisticFolderCallback(CallbackData, prefix='statistic_folder'):
    folder_id: str


class SearchInFolderCallback(CallbackData, prefix='search_in_folder'):
    folder_id: str


class PinFolderCallback(CallbackData, prefix='pin_folder'):
    folder_id: str


class PinCodeButtonCallback(CallbackData, prefix='pin_code_button'):
    folder_id: str
    pin: str
    pin_repeat: str
    visible: bool


class NewPinCodeButtonCallback(PinCodeButtonCallback, prefix='new_pin_code'):
    pass


class EnterPinCodeButtonCallback(PinCodeButtonCallback, prefix='enter_pin_code'):
    pass


class PinKeyboardNumberCallback(CallbackData, prefix='pin_keyboard_number'):
    number: int
    folder_id: str


class PinKeyboardButtonCallback(CallbackData, prefix='pin_keyboard_button'):
    action: str
    folder_id: str


class PinControlCallback(CallbackData, prefix='pin_control'):
    action: str
    folder_id: str


class AccessFolderCallback(CallbackData, prefix='access_folder'):
    folder_id: str


class AccessControlCallback(CallbackData, prefix='access_control'):
    folder_id: str
    action: str

