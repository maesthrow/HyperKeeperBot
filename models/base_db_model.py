from abc import ABC, abstractmethod


class BaseDbModel(ABC):

    @abstractmethod
    def to_dict(self) -> dict:
        pass
