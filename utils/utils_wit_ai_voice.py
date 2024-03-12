import os

from aiogram.types import Voice, Message
from pydub import AudioSegment
from load_all import bot, wit_client

notifies = (
    '🎧 Слушаю ваше голосовое...',
    '🤓 Формирую нули и единицы...',
    '👨‍💻 Печатаю текст...',
    '✍️ Расставляю запятые...',
    '👌 Еще совсем немного...',
    '🎨 Последние штрихи...',
    '✨ Почти готово...',
)

# async def get_voice_text(voice: Voice | str):
#     if isinstance(voice, Voice):
#         file_id = voice.file_id
#     else:
#         file_id = voice
#     # Получение информации о файле
#     file_info = await bot.get_file(file_id)
#     file_path = file_info.file_path
#
#     # Скачивание файла
#     file = await bot.download_file(file_path)
#     temp_ogg_path = "voice_message.ogg"
#     temp_mp3_path = "voice_message_converted.mp3"
#
#     # Сохранение файла локально в формате .ogg
#     with open(temp_ogg_path, "wb") as out_file:
#         out_file.write(file.getvalue())
#
#     # Конвертация из .ogg в .mp3
#     audio = AudioSegment.from_ogg(temp_ogg_path)
#     audio.export(temp_mp3_path, format="mp3")
#
#     # Отправка сконвертированного файла в Wit.ai
#     with open(temp_mp3_path, "rb") as audio_file:
#         response = wit_client.speech(audio_file, headers={"Content-Type": "audio/mpeg"})
#
#     # Обработка ответа
#     if response is not None:
#         voice_text = response.get("text", "")
#     else:
#         voice_text = None
#
#     # Удаление временных файлов
#     os.remove(temp_ogg_path)
#     os.remove(temp_mp3_path)
#
#     return voice_text


async def get_voice_text(voice: Voice | str, message: Message = None):
    if isinstance(voice, Voice):
        file_id = voice.file_id
    else:
        file_id = voice
    # Получение информации о файле
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    # Скачивание файла
    file = await bot.download_file(file_path)
    temp_ogg_path = "voice_message.ogg"
    temp_mp3_path = "voice_message_converted.mp3"

    # Сохранение файла локально в формате .ogg
    with open(temp_ogg_path, "wb") as out_file:
        out_file.write(file.getvalue())

    # Конвертация из .ogg в .mp3
    audio = AudioSegment.from_ogg(temp_ogg_path)

    voice_text = ""  # Общий текст из всех частей аудио

    # Проверяем длительность аудио и разбиваем, если необходимо
    max_duration = 19 * 1000  # Максимальная длительность в миллисекундах
    if len(audio) > max_duration:
        message_text = message.text
        parts = len(audio) // max_duration + 1
        for i in range(parts):
            start = i * max_duration
            end = (i + 1) * max_duration if (i + 1) * max_duration < len(audio) else len(audio)
            part = audio[start:end]
            part.export(f"part_{i}.mp3", format="mp3")
            with open(f"part_{i}.mp3", "rb") as part_file:
                response = wit_client.speech(part_file, headers={"Content-Type": "audio/mpeg"})
                # Обработка ответа для каждой части
                if response is not None:
                    part_text = response.get("text", "")
                    voice_text += part_text + " "
                else:
                    print(f"No response for part {i + 1}")
            # Удаление временных файлов
            os.remove(f"part_{i}.mp3")
            if i < len(notifies) - 1:
                message_text = notifies[i + 1]
            else:
                if message_text.find('...') != -1:
                    message_text = notifies[-1][:-1]
                else:
                    message_text += '.'
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=message_text
            )
            #await asyncio.sleep(1)
    else:
        # Конвертируем и отправляем весь файл целиком
        audio.export(temp_mp3_path, format="mp3")
        with open(temp_mp3_path, "rb") as audio_file:
            response = wit_client.speech(audio_file, headers={"Content-Type": "audio/mpeg"})
            # Обработка ответа
            if response is not None:
                voice_text += response.get("text", "")
        # Удаление временных файлов
        os.remove(temp_ogg_path)
        os.remove(temp_mp3_path)

    voice_text = voice_text.strip()
    if voice_text[-1] not in '.?!':
        voice_text += '.'

    return voice_text.strip()  # Убираем возможные лишние пробелы в начале и конце текста