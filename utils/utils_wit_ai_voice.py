import os

from aiogram.enums import ContentType
from aiogram.types import Voice, Message, VideoNote
from pydub import AudioSegment

from load_all import bot, wit_client

start_read_notify = {
    ContentType.VOICE: '🎧 Слушаю ваше голосовое...',
    ContentType.VIDEO_NOTE: '🎧 Слушаю вашу видеозапись...',
}

notifies = (
    '🤖 Перевожу в нули и единицы...',
    '👨‍💻 Печатаю текст...',
    '✍️ Расставляю запятые...',
    '👌 Еще совсем немного...',
    '🎨 Последние штрихи...',
    '✨ Почти готово...',
)

TEMP_FOLDER = "temp_media/"


def get_start_read_notify(content_type: ContentType):
    return start_read_notify.get(content_type, '🎧')


async def get_voice_text(voice: Voice, message: Message):
    user_id = message.from_user.id
    voice_text = await get_media_text(
        voice,
        f"{TEMP_FOLDER}{user_id}voice_message.ogg", message
    )
    return voice_text


async def get_video_note_text(video_note: VideoNote, message: Message):
    user_id = message.from_user.id
    video_note_text = await get_media_text(
        video_note,
        f"{TEMP_FOLDER}{user_id}video_note_message.mp4", message
    )
    return video_note_text


async def get_media_text(audio: Voice | VideoNote, temp_source_path: str, message: Message) -> str:
    temp_mp3_path = f"{temp_source_path.split('.')[0]}_converted.mp3"
    media_text = ''
    audio = await get_audio_from_media(audio, temp_source_path)
    print(f'TEST {temp_mp3_path}')
    if audio:
        media_text = await get_voice_text_from_audio(audio, temp_source_path, temp_mp3_path, message)
    return media_text


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
    with open(temp_source_path, "wb") as out_file:
        out_file.write(file.getvalue())

    if isinstance(media, Voice):
        return AudioSegment.from_ogg(temp_source_path)
    elif isinstance(media, VideoNote):
        return AudioSegment.from_file(temp_source_path, format="mp4")


async def get_voice_text_from_audio(audio, temp_source_path, temp_mp3_path, message: Message):
    voice_text = ""

    user_id = message.from_user.id

    await bot.send_chat_action(message.chat.id, "typing")

    # Проверяем длительность аудио и разбиваем, если необходимо
    max_duration = round(19.9 * 1000)  # Максимальная длительность в миллисекундах
    if len(audio) > max_duration:
        message_text = message.text
        parts_count = len(audio) // max_duration + 1
        for i in range(parts_count):
            start = i * max_duration
            end = (i + 1) * max_duration if (i + 1) * max_duration < len(audio) else len(audio)
            part = audio[start:end]
            try:
                part.export(f"{TEMP_FOLDER}{user_id}_part_{i}.mp3", format="mp3")
                with open(f"{TEMP_FOLDER}{user_id}_part_{i}.mp3", "rb") as part_file:
                    response = wit_client.speech(part_file, headers={"Content-Type": "audio/mpeg"})
                    # Обработка ответа для каждой части
                    if response is not None:
                        part_text = response.get("text", "")
                        voice_text += part_text + " "
                    else:
                        print(f"No response for part {i + 1}")
                remove_temp_file(f"{TEMP_FOLDER}{user_id}_part_{i}.mp3")
            except:
                part_file.close()
                remove_temp_file(f"{TEMP_FOLDER}{user_id}_part_{i}.mp3")
                if i == parts_count - 1:
                    break

            if i < len(notifies):
                message_text = notifies[i]
            else:
                if message_text.find('...') != -1:
                    message_text = notifies[-1][:-1]
                else:
                    message_text += '.'
            try:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    text=message_text
                )
                await bot.send_chat_action(message.chat.id, "typing")
            except:
                pass

        remove_temp_file(temp_source_path)
    else:
        # Конвертируем и отправляем весь файл целиком
        audio.export(temp_mp3_path, format="mp3")
        with open(temp_mp3_path, "rb") as audio_file:
            if audio_file:
                print('pre response')
                try:
                    response = wit_client.speech(audio_file, headers={"Content-Type": "audio/mpeg"})
                finally:
                    audio_file.close()  # Закрыть файл перед удалением
                    remove_temp_file(temp_mp3_path)
                    remove_temp_file(temp_source_path)
                print('post response')
                # Обработка ответа
                if response is not None:
                    voice_text += response.get("text", "")

    if voice_text:
        voice_text = voice_text.strip()
        if voice_text[-1] not in '.?!':
            voice_text += '.'

    return voice_text


# Удаляет временный файл
def remove_temp_file(temp_file_path):
    try:
        os.remove(temp_file_path)
    except Exception as e:
        print(f'Ошибка при попытке удаления временного файла {temp_file_path}: {e}')
