from typing import Optional

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager, ShowMode, Data, StartMode, ChatEvent, BaseDialogManager
from aiogram_dialog.manager.manager import ManagerImpl

from utils.data_manager import get_data, set_data


class DialogData:
    @staticmethod
    async def get_manager(user_id: int) -> ManagerImpl:
        data = await get_data(user_id)
        dialog_manager = data.get('dialog_manager', None)
        return dialog_manager

    @staticmethod
    async def set_manager(user_id: int, dialog_manager: ManagerImpl | None):
        print(f'set_manager')
        data = await get_data(user_id)
        data['dialog_manager'] = dialog_manager
        await set_data(user_id, data)
        print(f'set_manager dialog_manager {dialog_manager}')

    @staticmethod
    async def clear_manager(user_id: int):
        await DialogData.set_manager(user_id, None)


# class DialogMan(ManagerImpl):
#     @staticmethod
#     async def set_manager(user_id, dialog_manager: DialogManager):
#         if not user_id:
#             return
#         data = await get_data(user_id)
#         data['dialog_manager'] = dialog_manager
#         await set_data(user_id, data)
#         print(f'DialogMan data = {data}')
#
#     @staticmethod
#     async def get_manager(user_id) -> DialogManager:
#         data = await get_data(user_id)
#         dialog_manager = data.get('dialog_manager', None)
#         return dialog_manager
#
#     async def start(
#             self,
#             state: State,
#             data: Data = None,
#             mode: StartMode = StartMode.NORMAL,
#             show_mode: Optional[ShowMode] = None,
#             user_id: int = None,
#     ) -> None:
#         await super().start(state, data, mode, show_mode)
#         await self.set_manager(user_id, self)
#
#     async def switch_to(
#             self,
#             state: State,
#             show_mode: Optional[ShowMode] = None,
#             user_id: int = None,
#     ) -> None:
#         await super().switch_to(state, show_mode)
#         await self.set_manager(user_id, self)


