from enums.enums import AccessType
from models.folder_model import Folder
from utils.utils_ import smile_folder
from utils.utils_folders_reader import get_folder_name


class AccessFolder:
    def __init__(
            self,
            user_id: int,
            from_user_id: int,
            folder_id: str,
            access_type: AccessType,
            pin: str = None,
    ):
        self.user_id = user_id
        self.from_user_id = from_user_id
        self.folder_id = folder_id
        self.access_type_value = access_type.value if isinstance(access_type, AccessType) else access_type
        self.pin = pin

    def get_access_type(self) -> AccessType:
        return AccessType(self.access_type_value)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "from_user_id": self.from_user_id,
            "folder_id": self.folder_id,
            "access_type": self.access_type_value,
            "pin": self.pin,
        }

    async def to_dict_with_folder_name_and_smile_folder(self) -> dict:
        result = self.to_dict()
        folder_name = await get_folder_name(self.from_user_id, self.folder_id)
        smile_access = '👁️' if self.get_access_type() == AccessType.READ else '✏️'
        folder_name = f"{smile_access} {smile_folder} {folder_name}"
        result['folder_name'] = folder_name
        return result

    @staticmethod
    def get_dict_by_properties(access_type: AccessType, pin: str = None):
        return {
            "access_type": access_type.value,
            "pin": pin
        }

