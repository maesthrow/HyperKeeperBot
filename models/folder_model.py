class Folder:
    def __init__(
            self,
            folder_id: str,
            name: str,
            access: {} = None,
            folders: {} = None,
            items: {} = None
    ):
        self.folder_id = folder_id
        self.name = name
        self.access = access
        self.folders = folders
        self.items = items

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "access": self.access,
            "folders": self.folders,
            "items": self.items,
        }

    def get_pin(self):
        return self.access.get('pin', '') if self.access else ''
