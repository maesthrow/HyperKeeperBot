from typing import List

from enums.enums import GPTModel
from models.base_db_model import BaseDbModel
from models.base_item_model import BaseItem, INVISIBLE_CHAR
from utils.utils_parse_mode_converter import escape_markdown


class Chat(BaseDbModel, BaseItem):
    def __init__(self, id: str, text: List[str] | str, title: str, gpt_model: GPTModel | str):
        super().__init__(id, text, title)
        if isinstance(gpt_model, GPTModel):
            self.gpt_model = gpt_model.value
        else:
            self.gpt_model = gpt_model

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "text": self.text,
            "gpt_model": self.gpt_model
        }

    def get_body_markdown(self, page=0) -> str:
        title = escape_markdown(self.get_title())
        title += '\n' if title[-1] != '\n' else ''
        text = escape_markdown(self.text[page])
        return f"📄 *{title}*\n\n{text}\n{INVISIBLE_CHAR}"

    def get_text_markdown_for_show_chat_history(self, page=0):
        markdown_text = self.get_text_markdown()
        result_markdown_text = (markdown_text
                                .replace('`*', '*').replace('*`', '*')
                                .replace('\n\_', '\n_').replace('\_\n', '_\n'))
        if result_markdown_text[-2:] == '\\_':
            result_markdown_text = result_markdown_text[:-2] + '_'
        return result_markdown_text

    @staticmethod
    def smile():
        return '💬'


class SimpleChat(BaseDbModel):
    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
        }
