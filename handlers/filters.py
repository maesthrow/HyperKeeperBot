from typing import Any, Union, Dict, List

from aiogram.filters import Filter
from aiogram.types import KeyboardButton, Message


class InButtonsFilter(Filter):
    def __init__(self, buttons: List[KeyboardButton]) -> None:
        self.buttons = buttons

    async def __call__(self, message: Message) -> bool:
        return message.text in [button.text for button in self.buttons]


class NotInButtonsFilter(Filter):
    def __init__(self, buttons: List[KeyboardButton]) -> None:
        self.buttons = buttons

    async def __call__(self, message: Message) -> bool:
        return message.text not in [button.text for button in self.buttons]