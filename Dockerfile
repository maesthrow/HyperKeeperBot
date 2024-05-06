FROM python:3.12-slim

# Установка ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

#RUN apt-get update && apt-get install build-essential


WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
