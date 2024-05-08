from abc import ABC, abstractmethod
from typing import List

from utils.utils_parse_mode_converter import escape_markdown, full_escape_markdown

INVISIBLE_CHAR = "\u00A0"


class BaseItem(ABC):
    def __init__(self, id: str, text: List[str], title=None):
        self.id = id
        self.title = title
        self.text = text

    def get_title(self) -> str:
        title = self.title if self.title else ""
        need_added_chars = 69 - len(title)
        if need_added_chars > 0:
            title += ' ' * need_added_chars
            title += f"\n{INVISIBLE_CHAR}"
        return title

    def get_inline_title(self) -> str:
        return self.title if self.title and self.title != "" else \
            (self.text[0].splitlines()[0] if self.text and self.text[0] != "" else "")

    def get_text(self, page=0) -> str:
        return self.text[page]

    def get_text_markdown(self, page=0) -> str:
        return escape_markdown(self.text[page])

    def get_text_full_markdown(self, page=0) -> str:
        return full_escape_markdown(self.text[page])

    def pages_count(self) -> int:
        return len(self.text)

    def last_page_number(self) -> int:
        return self.pages_count() - 1

    def add_text(self, text_added: str | List[str], on_new_page=False):
        if self.text and not on_new_page:
            if isinstance(text_added, list):
                text_added.insert(0, f'{self.text.pop().replace(INVISIBLE_CHAR, '')}\n')
            else:
                text_added = f'{self.text.pop().replace(INVISIBLE_CHAR, '')}\n\n{text_added}'

        new_pages = self.split_text(text_added)
        if new_pages:
            if self.text and self.text[0] == '':
                self.text.pop()
            self.text.extend(new_pages)

    @staticmethod
    def split_text(text: str | List[str]) -> List[str]:
        print(f'split_text\n{len(text)}')

        BASE_SPLIT_INDEX = 4000
        if isinstance(text, list):
            text = '\n'.join(text)

        text_pages = []
        while text:
            if len(text) <= BASE_SPLIT_INDEX:
                text_pages.append(text.strip())
                break

            split_index = BASE_SPLIT_INDEX
            while ((split_index - 100 > 100) and
                   (len(text[split_index + 1:]) < 100 or
                    ('\n' not in text[split_index + 1:] and '.' not in text[split_index + 1:]))):
                split_index -= 100
            analyze_text = text[split_index - 100:split_index + 1]
            find_index = analyze_text.rfind('\n') if '\n' in analyze_text else \
                analyze_text.rfind('.') if '.' in analyze_text else \
                    analyze_text.rfind(' ')
            if find_index >= 0:
                split_index = split_index - 100 + find_index

            text_pages.append(text[:split_index].strip())
            text = text[split_index + 1:]

        return text_pages

    @abstractmethod
    def get_body_markdown(self, page=0) -> str:
        """ Метод должен быть реализован в подклассах для получения Markdown-форматированного тела страницы """
        pass
