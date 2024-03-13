import os

from aiogram.enums import ContentType
from aiogram.types import Voice, Message, VideoNote
from pydub import AudioSegment
from wit import Wit

from config import WIT_AI_TOKEN
from load_all import bot

start_read_notify = {
    ContentType.VOICE: '🎧 Слушаю ваше голосовое...',
    ContentType.VIDEO_NOTE: '🎧 Слушаю вашу видеозапись...',
}

notifies = (
    #'🎧 Слушаю ваше голосовое...',
    '🤓 Формирую нули и единицы...',
    '👨‍💻 Печатаю текст...',
    '✍️ Расставляю запятые...',
    '👌 Еще совсем немного...',
    '🎨 Последние штрихи...',
    '✨ Почти готово...',
)


def get_start_read_notify(content_type: ContentType):
    return start_read_notify.get(content_type, '🎧')


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
    temp_ogg_path = "voice_message.ogg"
    temp_mp3_path = "voice_message_converted.mp3"
    voice_text = ''
    audio = await get_audio_from_media(voice, temp_ogg_path)
    if audio:
        voice_text = await get_voice_text_from_audio(audio, temp_ogg_path, temp_mp3_path, message)
    return voice_text


async def get_video_note_text(video_note: VideoNote | str, message: Message = None):
    temp_mp4_path = "video_note_message.mp4"
    temp_mp3_path = "video_note_message_converted.mp3"
    video_note_text = ''
    audio = await get_audio_from_media(video_note, temp_mp4_path)
    if audio:
        video_note_text = await get_voice_text_from_audio(audio, temp_mp4_path, temp_mp3_path, message)
    return video_note_text


async def get_audio_from_media(media: Voice | VideoNote, temp_source_path: str):
    if isinstance(media, Voice):
        file_id = media.file_id
    elif isinstance(media, VideoNote):
        file_id = media.file_id
    else:
        return None

    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path

    file = await bot.download_file(file_path)

    # Сохранение файла локально в формате .ogg
    with open(temp_source_path, "wb") as out_file:
        out_file.write(file.getvalue())

    if isinstance(media, Voice):
        return AudioSegment.from_ogg(temp_source_path)
    elif isinstance(media, VideoNote):
        return AudioSegment.from_file(temp_source_path, format="mp4")


async def get_voice_text_from_audio(audio, temp_source_path, temp_mp3_path, message: Message):
    voice_text = ""  # Общий текст из всех частей аудио

    wit_client = Wit(WIT_AI_TOKEN)

    # Проверяем длительность аудио и разбиваем, если необходимо
    max_duration = 19 * 1000  # Максимальная длительность в миллисекундах
    if len(audio) > max_duration:
        message_text = message.text
        parts_count = len(audio) // max_duration + 1
        for i in range(parts_count):
            start = i * max_duration
            end = (i + 1) * max_duration if (i + 1) * max_duration < len(audio) else len(audio)
            part = audio[start:end]
            try:
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
            except:
                if i == parts_count - 1:
                    break

            if i < len(notifies):
                message_text = notifies[i]
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
            # await asyncio.sleep(1)
    else:
        # Конвертируем и отправляем весь файл целиком
        audio.export(temp_mp3_path, format="mp3")
        with open(temp_mp3_path, "rb") as audio_file:
            if audio_file:
                print('pre response')
                response = wit_client.speech(audio_file, headers={"Content-Type": "audio/mpeg"})
                print('post response')
                # Обработка ответа
                if response is not None:
                    voice_text += response.get("text", "")

    try:
        # Удаление временных файлов
        os.remove(temp_source_path)
        os.remove(temp_mp3_path)
    except Exception as e:
        print(f'Ошибка при попытке удаления временных файлов {e}')

    if voice_text:
        voice_text = voice_text.strip()
        if voice_text[-1] not in '.?!':
            voice_text += '.'

    return voice_text
