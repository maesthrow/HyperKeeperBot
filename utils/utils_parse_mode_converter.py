from typing import List

from aiogram.types import MessageEntity


def to_markdown_text(text: str, message_entities: List[MessageEntity]) -> str:
    return escape_markdown(preformat_text(text, message_entities))


def preformat_text(text: str, message_entities: List[MessageEntity], is_show=False, is_double=False) -> str:
    if not message_entities:
        return text
    for entity in message_entities:
        offset = entity.offset
        while offset > 1 and text[offset - 1] != "\n":
            offset -= 1
        if entity.type == 'pre':
            text = (f"{text[:offset]}"
                    f"```\n{text[offset:offset + entity.length]}"
                    f"```{text[offset + entity.length:]}")
    return text


def escape_markdown(text) -> str:
    """Экранирует специальные символы для использования в разметке Markdown V2."""
    if not text:
        return text
    escape_chars = '\\*_[]()<>#+-=|{}.!'
    escaped_text = ''
    can_edit = True
    for char in text:
        if char == '`':
            can_edit = not can_edit
        if char in escape_chars and can_edit:
            escaped_text += '\\' + char
        else:
            escaped_text += char
    return escaped_text


def full_escape_markdown(text) -> str:
    if not text:
        return text
    text = text.replace("```", "")
    escape_chars = '\\*_[]()<>#+-=|{}.!'
    escaped_text = ''
    for char in text:
        if char in escape_chars:
            escaped_text += '\\' + char
        else:
            escaped_text += char
    return escaped_text


def markdown_without_code(text) -> str:
    return text.replace("```", "````").strip()
