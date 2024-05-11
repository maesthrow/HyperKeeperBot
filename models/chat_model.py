from typing import List

from aiogram.types import DateTime
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage

from enums.enums import GPTModel
from models.base_db_model import BaseDbModel
from models.base_item_model import BaseItem, INVISIBLE_CHAR
from resources.text_getter import get_text
from utils.utils_parse_mode_converter import escape_markdown


CHAT_MESSAGE_TYPE = {
    AIMessage: 'ai',
    HumanMessage: 'hu',
    SystemMessage: 'sy',
}

PAGE_LEN = 3000


class Chat(BaseDbModel):
    def __init__(
            self,
            id: str,
            title: str,
            messages: List[dict],
            gpt_model: GPTModel | str,
            date_modified: DateTime
    ):
        self.id = id
        self.title = title
        self.messages = messages
        if isinstance(gpt_model, GPTModel):
            self.gpt_model = gpt_model.value
        else:
            self.gpt_model = gpt_model
        self.date_modified = date_modified

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "messages": self.messages,
            "gpt_model": self.gpt_model,
            "date_modified": self.date_modified
        }

    def to_dict_with_id(self) -> dict:
        chat_dict = self.to_dict()
        chat_dict['id'] = self.id
        return chat_dict

    def is_valid(self):
        return (self.id
                and self.title
                and self.messages
                and self.gpt_model
                and self.date_modified)

    async def get_pages_text_markdown_for_show_chat_history(self, user_id):
        full_text = await self.get_text_markdown_for_show_chat_history(user_id)
        messages = full_text.split("\n\n")
        pages = ['']
        page = 0
        for message in messages:
            if len(pages[page]) < PAGE_LEN and (len(message) + len(pages[page]) < PAGE_LEN):
                pages[page] += f'\n\n{message}'
            else:
                page += 1
                pages.append(message)
        return pages

    async def get_text_markdown_for_show_chat_history(self, user_id):
        you_text = await get_text(user_id, 'you')
        markdown_text = self._make_text_for_chat(you_text)
        return markdown_text

    def _make_text_for_chat(self, you_text) -> str:
        result = []
        for message in self.messages:
            if message['type'] == CHAT_MESSAGE_TYPE[AIMessage]:
                result.append(f'*🧠 GPT*\n{escape_markdown(message['text'])}')
            elif message['type'] == CHAT_MESSAGE_TYPE[HumanMessage]:
                result.append(f'*👤 {you_text}:*\n_{escape_markdown(message['text'])}_')
        return '\n\n'.join(result)

    def get_giga_chat_messages(self) -> List[BaseMessage]:
        result = []
        for message in self.messages:
            if message['type'] == CHAT_MESSAGE_TYPE[SystemMessage]:
                result.append(SystemMessage(content=message['text']))
            elif message['type'] == CHAT_MESSAGE_TYPE[AIMessage]:
                result.append(AIMessage(content=message['text']))
            elif message['type'] == CHAT_MESSAGE_TYPE[HumanMessage]:
                result.append(HumanMessage(content=message['text']))
        return result

    def delete_last_pair_messages(self):
        if len(self.messages) > 2:
            self.messages = self.messages[:-2]
            return True
        return False

    @staticmethod
    def smile():
        return '💬'


class SimpleChat(BaseDbModel):
    def __init__(
            self,
            id: str,
            title: str,
            date_modified: DateTime
    ):
        self.id = id
        self.title = title
        self.date_modified = date_modified

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "date_modified": self.date_modified,
        }
