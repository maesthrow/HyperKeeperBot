from enums.enums import AccessType


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
        self.access_type = access_type.value
        self.pin = pin

    def get_access_type(self) -> AccessType:
        return AccessType(self.access_type)

    def to_dict(self) -> dict:
        return {
            "access_type": self.access_type,
            "pin": self.pin,
        }

    @staticmethod
    def get_dict_by_properties(access_type: AccessType, pin: str = None):
        return {
            "access_type": access_type.value,
            "pin": pin
        }

