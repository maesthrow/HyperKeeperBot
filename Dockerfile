FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала зависимости
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Потом код
COPY . .

CMD ["python", "app.py"]
