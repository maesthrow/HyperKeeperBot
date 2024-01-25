from aiogram.filters.callback_data import CallbackData


class FolderCallback(CallbackData, prefix="folder"):
    folder_id: str


class DeleteFolderRequest(CallbackData, prefix="delete_folder_request"):
    is_confirmed: bool