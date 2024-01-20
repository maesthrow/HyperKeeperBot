from aiogram.filters.callback_data import CallbackData


class CallbackFolder(CallbackData, prefix="folder"):
    folder_id: str