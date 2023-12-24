from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup


class Item:
    def __init__(self, text, title=None, date_created=None, date_modified=None):
        self.title = title
        self.text = text
        self.date_created = date_created or datetime.now()
        self.date_modified = date_modified or self.date_created

    def to_dict(self):
        return {
            "title": self.title,
            "text": self.text,
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

    def __str__(self):
        return f"{self.title} ({self.date_created.strftime('%Y-%m-%d %H:%M:%S')})"
