from typing import Any, Union, Dict, List

from aiogram.filters import Filter
from aiogram.types import KeyboardButton, Message


class InButtonsFilter(Filter):
    def __init__(self, buttons: List[Union[KeyboardButton, List[KeyboardButton]]]):
        self.buttons = buttons

    async def __call__(self, message: Message) -> bool:
        return await self.contains(message)

    async def contains(self, message: Message) -> bool:
        # Преобразовать список списков кнопок в плоский список кнопок
        flat_buttons = [button for sublist in self.buttons for button in
                        (sublist if isinstance(sublist, list) else [sublist])]
        # Проверить, содержится ли текст сообщения в тексте любой кнопки
        return message.text in [button.text for button in flat_buttons]


class NotInButtonsFilter(InButtonsFilter):

    async def __call__(self, message: Message) -> bool:
        return not await InButtonsFilter.contains(self, message)


