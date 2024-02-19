import copy
import json
from datetime import datetime
from typing import List, Union

from utils.utils_parse_mode_converter import escape_markdown

INVISIBLE_CHAR = "\u00A0"


class Item:
    default_media = {
        "photo": [],
        "video": [],
        "audio": [],
        "document": [],
        "voice": [],
        "video_note": [],
        "location": [],
        "contact": [],
        "sticker": [],
    }

    def __init__(self, id: str, text: List[str], title=None, media: dict = None, date_created=None, date_modified=None):
        self.id = id
        self.title = title
        self.text = text
        if not media:
            self.media = copy.deepcopy(self.default_media)
        else:
            self.media = media
        self.date_created = date_created or datetime.now()
        self.date_modified = date_modified or self.date_created

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "text": self.text,
            "media": self.media,
            "date_created": self.date_created,
            "date_modified": self.date_modified
        }

    def to_json(self) -> str:
        item_dict = self.to_dict()
        item_dict['date_created'] = serialize_datetime(item_dict['date_created'])
        item_dict['date_modified'] = serialize_datetime(item_dict['date_modified'])
        item_json = json.dumps(item_dict).replace(':', '>').replace("sep", ">")
        return item_json

    def get_all_media_values(self):
        all_values = []
        for key, value in self.media.items():
            all_values.extend(value)
        return all_values

    def files_count(self):
        return len(self.get_all_media_values())

    def get_title(self):
        title = self.title if self.title else ""
        need_added_chars = 70 - len(title)
        if need_added_chars > 0:
            for i in range(need_added_chars):
                title += ' '
            title += f"\n{INVISIBLE_CHAR}"
        return title

    def get_inline_title(self):
        return self.title if self.title and self.title != "" else \
            (self.text[0].splitlines()[0] if self.text and self.text[0] != "" else "")

    def get_inline_page_text(self, page):
        return self.text[page].splitlines()[0]

    def get_body(self, page=0):
        title = self.get_title()
        display_page = page + 1
        page_info = f'{display_page} из {len(self.text)}\n\n' if (len(self.text) > 1) else ''
        return f"📄 <b>{title}</b>\n{page_info}{self.text[page]}\n{INVISIBLE_CHAR}"

    def get_body_markdown(self, page=0):
        title = escape_markdown(self.get_title())
        title += '\n' if title[-1] != '\n' else ''
        display_page = page + 1
        page_info = f'_*{display_page} из {len(self.text)}*_\n\n' if (len(self.text) > 1) else ''
        text = escape_markdown(self.text[page])
        return f"📄 *{title}*{page_info}{text}\n{INVISIBLE_CHAR}"

    def get_text(self, page=0):
        return self.text[page]

    def page_not_empty(self, page=0):
        return self.text[page] and self.text[page] != INVISIBLE_CHAR

    def get_text_markdown(self, page=0):
        return escape_markdown(self.text[page])

    def pages_count(self):
        return len(self.text)

    def last_page_number(self):
        return self.pages_count() - 1

    def add_text(self, text_added: str | List[str], on_new_page=False):
        if len(self.text) > 0 and not on_new_page:
            if isinstance(text_added, list):
                text_added.insert(0, f'{self.text.pop().replace(INVISIBLE_CHAR, '')}\n')
            else:
                text_added = f'{self.text.pop().replace(INVISIBLE_CHAR, '')}\n\n{text_added}'

        new_pages = Item.split_text(text_added)
        if len(new_pages) > 0:
            if len(self.text) > 0 and self.text[0] == '':
                self.text.pop()
            self.text.extend(new_pages)

    def insert_text(self, page: int, text_inserted: str | List[str], rewrite_page: bool):
        if not rewrite_page and self.pages_count() > page:
            if isinstance(text_inserted, list):
                text_inserted.insert(0, f'{self.text.pop(page).replace(INVISIBLE_CHAR, '')}')
            else:
                text_inserted = f'{self.text.pop(page).replace(INVISIBLE_CHAR, '')}\n\n{text_inserted}'

        new_pages = Item.split_text(text_inserted)
        if len(text_inserted) > 0:
            inserted = new_pages + self.text[page + 1:] if page < self.pages_count() - 1 else new_pages
            self.text = self.text[:page] + inserted

    def insert_page(self, page_index: int):
        self.text.insert(page_index, INVISIBLE_CHAR)

    def clear_text(self):
        self.text = [INVISIBLE_CHAR]

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
            while True:
                if ((split_index - 100 > 100) and
                        (len(text[split_index + 1:]) < 100 or
                         ('\n' not in text[split_index + 1:] and '.' not in text[split_index + 1:]))):
                    split_index -= 100
                else:
                    break
            analyze_text = text[split_index - 100:split_index + 1]
            find_index = analyze_text.rfind('\n') if '\n' in analyze_text else analyze_text.rfind(
                '.') if '.' in analyze_text else analyze_text.rfind(' ')
            if find_index >= 0:
                split_index = split_index - 100 + find_index

            text_pages.append(text[:split_index].strip())
            text = text[split_index + 1:]

        return text_pages

    def remove_page(self, page: int):
        self.text.pop(page)

    # def get_short_parse_title(self):
    #     urls = re.findall(r'https?://[^\s]+', self.text)
    #
    #     if not urls:
    #         words = self.text.split()
    #         short_title = " ".join(words[:3])
    #         if len(words) > 3:
    #             short_title = short_title + "..."
    #         return short_title
    #
    #     for url in urls:
    #         print(url)
    #     # Берем первый найденный URL
    #     url = urls[0]
    #
    #     # Отправляем запрос на получение HTML-кода страницы
    #     response = requests.get(url)
    #     html_code = response.text
    #
    #     # Используем BeautifulSoup для парсинга HTML-кода
    #     soup = BeautifulSoup(html_code, 'html.parser')
    #
    #     # Получаем текст заголовка страницы
    #     try:
    #         short_title = soup.title.string
    #     except:
    #         words = self.text.split()
    #         short_title = " ".join(words[:3])
    #         if len(words) > 3:
    #             short_title = short_title + "..."
    #         return short_title
    #
    #     return short_title

    def select_search_text(self, search_text: str, left_teg: str = '<b><i><u>', right_teg: str = '</u></i></b>'):
        self.title = get_selected_search_text(self.title, search_text, left_teg, right_teg)
        for page in range(len(self.text)):
            self.text[page] = get_selected_search_text(self.text[page], search_text, left_teg, right_teg)

    def __str__(self):
        return f"{self.id} {self.get_inline_title()} ({self.date_created.strftime('%Y-%m-%d %H:%M:%S')})"


# Функция для сериализации объекта datetime в строку формата ISO 8601
def serialize_datetime(dt):
    if dt is None:
        return None
    return dt.isoformat()


def get_selected_search_text(text: str, search_text: str, left_teg: str = '<b><i><u>', right_teg: str = '</u></i></b>'):
    # Ищем все вхождения search_text в тексте
    if text:
        start_index = text.lower().find(search_text.lower())
    else:
        return text

    while start_index != -1:
        # Формируем подстроку до первого вхождения
        prefix = text[:start_index]

        # Формируем подстроку с тегами <u> </u>
        underlined_text = f'{left_teg}{text[start_index: start_index + len(search_text)]}{right_teg}'

        # Формируем подстроку после первого вхождения
        suffix = text[start_index + len(search_text):]

        # Объединяем все три подстроки
        text = f"{prefix}{underlined_text}{suffix}"

        if text:
            #Ищем следующее вхождение search_text, исключая уже найденный текст
            start_index = text.lower().find(search_text.lower(), start_index + len(underlined_text))
        else:
            start_index = -1

    return text
