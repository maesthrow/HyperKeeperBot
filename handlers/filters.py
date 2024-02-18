from typing import Any, Union, Dict, List

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import KeyboardButton, Message

from handlers import states
from handlers.states import Item


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
        return not await self.contains(message)


class NotAddToFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state != Item.AddTo.state


class ItemAddModeFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state in (states.Item.AddTo, states.Item.ChooseTypeAddText)
