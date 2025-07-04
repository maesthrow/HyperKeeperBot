from aiogram.types import InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.kbd import ScrollingGroup


class CustomScrollingGroup(ScrollingGroup):
    async def _render_pager(
            self,
            pages: int,
            manager: DialogManager,
    ) -> RawKeyboard:
        if self.hide_pager:
            return []
        if pages == 0 or (pages == 1 and self.hide_on_single_page):
            return []

        last_page = pages - 1
        current_page = min(last_page, await self.get_page(manager))
        next_page = min(last_page, current_page + 1)
        prev_page = max(0, current_page - 1)

        return [
            [
                InlineKeyboardButton(
                    text="1", callback_data=self._item_callback_data("0"),
                ),
                InlineKeyboardButton(
                    text="◀️",
                    callback_data=self._item_callback_data(prev_page),
                ),
                InlineKeyboardButton(
                    text=str(current_page + 1),
                    callback_data=self._item_callback_data(current_page),
                ),
                InlineKeyboardButton(
                    text="▶️",
                    callback_data=self._item_callback_data(next_page),
                ),
                InlineKeyboardButton(
                    text=str(last_page + 1),
                    callback_data=self._item_callback_data(last_page),
                ),
            ],
        ]

    def get_page_count_public(self) -> int:
        return len(self.buttons) // self.height + bool(len(self.buttons) % self.height)
