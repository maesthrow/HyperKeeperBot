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
    # item_text: str
    # item_title: str
    # item_media_photo: str
    # item_media_video: str
    # item_media_audio: str
    # item_media_document: str
    # item_media_voice: str
    # item_media_video_note: str
    # item_media_location: str
    # item_media_contact: str
    # item_media_sticker: str