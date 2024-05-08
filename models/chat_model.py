from typing import List

from enums.enums import GPTModel
from models.base_db_model import BaseDbModel
from models.base_item_model import BaseItem, INVISIBLE_CHAR
from utils.utils_parse_mode_converter import escape_markdown


class Chat(BaseDbModel, BaseItem):
    def __init__(self, id: str, text: List[str], title: str = None, gpt_model: GPTModel = GPTModel.GIGA):
        super().__init__(id, text, title)
        self.gpt_model = gpt_model

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "text": self.text,
            "model": self.gpt_model
        }

    def get_body_markdown(self, page=0) -> str:
        title = escape_markdown(self.get_title())
        title += '\n' if title[-1] != '\n' else ''
        text = escape_markdown(self.text[page])
        return f"📄 *{title}*\n\n{text}\n{INVISIBLE_CHAR}"



