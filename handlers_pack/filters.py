from typing import Union, List

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message
from aiogram_dialog import DialogManager

from handlers_pack import states
from handlers_pack.states import ItemState, FolderControlStates
from utils.data_manager import get_data, set_data


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
        return current_state != ItemState.AddTo.state


class NewItemValidateFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        user_id = message.from_user.id
        current_state = await state.get_state()
        print(f'current_state = {current_state}')
        data = await get_data(user_id)
        any_message_ignore = data.get('any_message_ignore', False)
        result = (
                not any_message_ignore
                and current_state != ItemState.EditFileCaption.state
                and current_state != ItemState.Search.state
                and current_state != ItemState.SearchResults.state
        )
        data['any_message_ignore'] = False
        await set_data(user_id, data)
        return result


class OnlyAddTextToItemFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state != ItemState.ChooseTypeAddTextToNewItem.state and current_state == ItemState.ChooseTypeAddText.state


class ItemAddModeFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state in (states.ItemState.AddTo, states.ItemState.ChooseTypeAddText)


class ItemAllAddModesFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state in (states.ItemState.NewStepAdd, states.ItemState.AddTo)


class FromUserChatConfirmMessageFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        print(message.text)
        return 'доступа?' in message.text
