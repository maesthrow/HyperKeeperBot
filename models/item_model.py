from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup


class Item:
    def __init__(self, text: str, title=None, media: dict = None, date_created=None, date_modified=None):
        self.title = title
        self.text = text
        self.media = media
        self.date_created = date_created or datetime.now()
        self.date_modified = date_modified or self.date_created

    def to_dict(self):
        return {
            "title": self.title,
            "text": self.text,
            "media": self.media,
            "date_created": self.date_created,
            "date_modified": self.date_modified
        }

    def get_short_title(self):
        return self.text.splitlines()[0]

    def get_short_parse_title(self):
        urls = re.findall(r'https?://[^\s]+', self.text)

        if not urls:
            words = self.text.split()
            short_title = " ".join(words[:3])
            if len(words) > 3:
                short_title = short_title + "..."
            return short_title

        for url in urls:
            print(url)
        # Берем первый найденный URL
        url = urls[0]

        # Отправляем запрос на получение HTML-кода страницы
        response = requests.get(url)
        html_code = response.text

        # Используем BeautifulSoup для парсинга HTML-кода
        soup = BeautifulSoup(html_code, 'html.parser')

        # Получаем текст заголовка страницы
        try:
            short_title = soup.title.string
        except:
            words = self.text.split()
            short_title = " ".join(words[:3])
            if len(words) > 3:
                short_title = short_title + "..."
            return short_title

        return short_title

    def select_search_text(self, search_text: str, left_teg: str = '<b><i><u>', right_teg: str = '</u></i></b>'):
        self.title = get_selected_search_text(self.title, search_text, left_teg, right_teg)
        self.text = get_selected_search_text(self.text, search_text, left_teg, right_teg)

    def __str__(self):
        return f"{self.title} ({self.date_created.strftime('%Y-%m-%d %H:%M:%S')})"


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
