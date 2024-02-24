from aiogram import types
from aiogram.types import Location, Sticker, Document, Contact


class ContentGroupBuilder:
    def     __init__(self, caption=None):
        self._media = []
        self.caption = caption

    def add(self, media_type, file_id, *args, **kwargs):
        if len(self._media) > 0:
            self.caption = None

        add_method = getattr(self, f"add_{media_type.lower()}", None)
        if add_method:
            add_method(file_id, *args, **kwargs)
        else:
            raise ValueError(f"Unsupported media type: {media_type}")

    def check_caption(self):
        self.caption = None if len(self._media) else self.caption

    def add_photo(self, file_id, caption=None):
        caption = self.caption if not caption else caption
        media = types.InputMediaPhoto(media=file_id, caption=caption)
        self._media.append(media)

    def add_video(self, file_id, caption=None):
        caption = self.caption if not caption else caption
        media = types.InputMediaVideo(media=file_id, caption=caption)
        self._media.append(media)

    def add_audio(self, file_id, caption=None):
        caption = self.caption if not caption else caption
        media = types.InputMediaAudio(media=file_id, caption=caption)
        self._media.append(media)

    def add_document(self, document: Document, caption=None):
        caption = self.caption if not caption else caption
        #media = document
        media = types.InputMediaDocument(media=document.file_id, caption=caption)
        self._media.append(media)

    def add_voice(self, file_id):
        self.check_caption()
        media = file_id
        self._media.append(media)

    def add_video_note(self, file_id):
        self.check_caption()
        media = file_id
        self._media.append(media)

    def add_location(self, location: Location):
        self.check_caption()
        self._media.append(location)

    def add_contact(self, contact: Contact):
        self.check_caption()
        self._media.append(contact)

    def add_sticker(self, sticker: Sticker):
        self.check_caption()
        self._media.append(sticker)

    def build(self):
        return self._media
