from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup

from dialogs import general_keyboards
from dialogs.giga_chat import keyboards
from models.chat_model import Chat
from mongo_db.mongo_collection_chats import add_user_chats
from resources.text_getter import get_text
from utils.data_manager import set_any_message_ignore
from utils.utils_chats_reader import get_simple_chats, get_chat, get_chat_from_chat_data
from utils.utils_data import get_current_lang


async def get_menu_chats_data(dialog_manager: DialogManager, **kwargs):
    # Добавляем коллекцию чатов в БД (для старых пользователей)
    await add_user_chats(dialog_manager.event.from_user)

    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    giga_menu_chats_title = await get_text(user.id, 'giga_menu_chats_title')
    message_text = giga_menu_chats_title

    chats = [chat.to_dict() for chat in await get_simple_chats(user.id)]
    sorted_chats = sorted(chats, key=lambda chat: chat['date_modified'], reverse=True)
    dialog_manager.current_context().dialog_data = {'chats': sorted_chats}
    print(sorted_chats)
    return {
        'message_text': message_text,
        'btn_new_chat': keyboards.BUTTONS['new_chat'].get(language),
        'btn_clear_chats_history': keyboards.BUTTONS['clear_chats_history'].get(language),
        'btn_menu': general_keyboards.BUTTONS['menu'].get(language),
        'chats': sorted_chats
    }


async def get_selected_chat_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    data = dialog_manager.current_context().start_data
    chat_data = data.get('chat')
    chat: Chat = await get_chat(user.id, chat_data.get('id'))

    chat_content_text = await get_text(user.id, 'chat_content_text')
    new_chat_text = await get_text(user.id, 'giga_new_chat_title')
    delete_last_pair_chat_messages_text = await get_text(user.id, 'delete_last_pair_chat_messages')

    text_pages = await chat.get_pages_text_markdown_for_show_chat_history(user_id=user.id)
    last_page = len(text_pages) - 1

    dialog_data = dialog_manager.current_context().dialog_data
    if dialog_data:
        current_page = dialog_data.get('page', last_page)
    else:
        current_page = last_page
    message_text = text_pages[current_page]
    chat_pages = [
        {
            'page': n, 'text': [page_text], 'delete_last_pair_chat_messages_text': delete_last_pair_chat_messages_text
        }
        for n, page_text in enumerate(text_pages)
    ]
    scrolling_group: ScrollingGroup = dialog_manager.find('chat_text_pages_scroll')
    scrolling_group.set_widget_data(dialog_manager, current_page)

    dialog_manager.current_context().dialog_data = {'chat_pages': chat_pages}

    return {
        'message_text': message_text,
        'chat_pages': chat_pages,
        'page': current_page
    }


async def get_new_chat_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    start_text = await get_text(user.id, 'start_chat_text')
    message_text = start_text
    return {
        'message_text': message_text,
    }


async def get_query_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    language = await get_current_lang(user.id)
    response_text = dialog_manager.current_context().dialog_data.get('response_text')
    if not response_text:
        response_text = dialog_manager.current_context().start_data.get('response_text')
    message_text = response_text
    return {
        'message_text': message_text,
    }


async def get_delete_chat_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    await set_any_message_ignore(user.id, True)
    language = await get_current_lang(user.id)
    message_text = await get_text(user.id, 'delete_chat_question')
    return {
        'message_text': message_text,
        'btn_confirm_delete_chat': keyboards.BUTTONS['confirm_delete_chat'].get(language),
        'btn_cancel_delete_chat': keyboards.BUTTONS['cancel_delete_chat'].get(language),
    }


async def get_clear_chats_history_data(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.event.from_user
    await set_any_message_ignore(user.id, True)
    language = await get_current_lang(user.id)
    message_text = await get_text(user.id, 'clear_chats_history_question')
    return {
        'message_text': message_text,
        'btn_confirm_clear_chats_history': keyboards.BUTTONS['confirm_clear_chats_history'].get(language),
        'btn_cancel_clear_chats_history': keyboards.BUTTONS['cancel_clear_chats_history'].get(language),
    }
