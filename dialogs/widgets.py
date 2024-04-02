from aiogram.types import InlineKeyboardButton
from aiogram_dialog.api.internal import RawKeyboard
from aiogram_dialog.widgets.kbd import Keyboard
from aiogram_dialog import DialogManager
from typing import Optional, Dict

from aiogram_dialog.widgets.text import Text


class InlineQueryButton(Keyboard):
    def __init__(self, text: Text, switch_inline_query: Text, id: Optional[str] = None):
        super().__init__(id=id)
        self.text = text
        self.switch_inline_query = switch_inline_query

    async def _render_keyboard(
            self,
            data: Dict,
            manager: DialogManager,
    ) -> RawKeyboard:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    switch_inline_query=await self.switch_inline_query.render_text(data, manager)
                ),
            ],
        ]
