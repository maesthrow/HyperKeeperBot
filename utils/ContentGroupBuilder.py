from aiogram import types
from aiogram.types import Location, Sticker, Document


class ContentGroupBuilder:
    def     __init__(self, caption=''):
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

    def add_photo(self, file_id):
        self.check_caption()
        media = types.InputMediaPhoto(media=file_id, caption=self.caption)
        self._media.append(media)

    def add_video(self, file_id):
        self.check_caption()
        media = types.InputMediaVideo(media=file_id, caption=self.caption)
        self._media.append(media)

    def add_audio(self, file_id):
        self.check_caption()
        media = types.InputMediaAudio(media=file_id, caption=self.caption)
        self._media.append(media)

    def add_document(self, document: Document):
        self.check_caption()
        media = document
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
        media = location #  latitude=latitude, longitude=longitude, title=self.caption)
        self._media.append(media)

    def add_contact(self, phone_number, first_name):
        self.check_caption()
        media = types.Contact(phone_number=phone_number, first_name=first_name, vcard=None)
        self._media.append(media)

    def add_sticker(self, sticker: Sticker):
        self.check_caption()
        media = sticker
        self._media.append(media)

    def build(self):
        return self._media
