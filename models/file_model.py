from aiogram.enums import ContentType


class File:
    def __init__(
            self,
            file_id: str,
            content_type: ContentType,
            file_name: str = None,
            caption: str = None,
            item_id: str = None
    ):
        self.file_id = file_id
        self.content_type = content_type
        self.file_name = file_name
        self.caption = caption
        self.item_id = item_id
