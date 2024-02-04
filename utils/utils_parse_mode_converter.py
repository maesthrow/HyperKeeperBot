from typing import List

from aiogram.types import MessageEntity


def to_markdown_text(text: str, message_entities: List[MessageEntity]) -> str:
    return escape_markdown(preformat_text(text, message_entities))


def to_markdown_text_show(text: str, message_entities: List[MessageEntity]) -> str:
    return escape_markdown(preformat_text(text, message_entities, is_show=True))


def preformat_text(text: str, message_entities: List[MessageEntity], is_show=False) -> str:
    if not message_entities:
        return text
    for entity in message_entities:
        offset = entity.offset
        decr = 1 if offset > 0 else 0
        print(f"offset = {offset}")
        if entity.type == 'pre':
            pre_text = '' if is_show else '\n'
            text = (f"{text[:offset - decr]}"
                    f"{pre_text}```\n{text[offset - decr:offset + entity.length - decr]}"
                    f"```{text[offset + entity.length:]}")
    return text


def escape_markdown(text) -> str:
    """Экранирует специальные символы для использования в разметке Markdown V2."""
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
