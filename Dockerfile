FROM python:3.12-slim

# Обновление списка пакетов и установка ffmpeg и инструментов для сборки
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    build-essential

# Установка рабочей директории
WORKDIR /app

# Копирование файла зависимостей и установка зависимостей
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Команда для запуска приложения
CMD ["python", "app.py"]