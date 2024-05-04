import copy

from aiogram.enums import ContentType
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from callbacks.callbackdata import TextPagesCallback, SaveItemCallback, \
    EditFileCaptionCallback, MarkFileCallback, DeleteFileCallback, RequestDeleteFileCallback, \
    RequestDeleteFilesCallback, MessageBoxCallback, EditFolderCallback, StatisticFolderCallback, SearchInFolderCallback, \
    PinFolderCallback, PinKeyboardNumberCallback, PinKeyboardButtonCallback, NewPinCodeButtonCallback, \
    EnterPinCodeButtonCallback, PinControlCallback, AccessFolderCallback, AccessControlCallback, VoiceSaveTypeCallback, \
    ReadVoiceRunCallback, AccessRequestCallback, AccessConfirmCallback, AnswerUserAfterContactSupportCallback, \
    AnswerAdminAfterAnswerUserContactSupportCallback
from models.item_model import Item, INVISIBLE_CHAR
from mongo_db.mongo_collection_folders import ROOT_FOLDER_ID
from resources.text_getter import get_text
from utils.utils_access import AccessType
from utils.utils_bot import to_url_data
from utils.utils_files import file_has_caption

cancel_button = KeyboardButton(text="️🚫 Отменить")

complete_edit_item_button = KeyboardButton(text="✔️ Завершить редактирование")  # ❎
clean_title_buttons = [
    KeyboardButton(text="🪧 Сделать пустой заголовок"),
    KeyboardButton(text="💾 Сохранить без заголовка"),
]

# delete_page_button = KeyboardButton(text="🗑 Удалить текущую страницу")
insert_page_inline_button = InlineKeyboardButton(text="↔️ Вставить страницу", callback_data="insert_page")
delete_page_inline_button = InlineKeyboardButton(text="🗑 Удалить страницу", callback_data="remove_page")

clean_text_buttons = [
    KeyboardButton(text="🧹 Очистить весь текст записи и сохранить"),
    KeyboardButton(text="💾 Сохранить без текста"),
]

general_buttons_folder = [
    [KeyboardButton(text="➕ Новая папка"), KeyboardButton(text="🔍 Поиск")],
    [KeyboardButton(text="️📊 Статистика"), KeyboardButton(text="️🧹 Удалить все записи в папке")],
    [KeyboardButton(text="✏️ Переименовать папку"), KeyboardButton(text="🗑 Удалить папку")]
]

current_folder_control_button = KeyboardButton(text=f"🛠 Управление текущей папкой")  # 🛠 ⚡️ 👨‍🔧👨‍🔬
new_general_buttons_folder = [
    [
        KeyboardButton(text=f"➕ Новая папка"),
        current_folder_control_button
    ]
]

general_buttons_folder_show_all = [
    [KeyboardButton(text="➕ Новая папка"), KeyboardButton(text="️📊 Статистика")],
]

general_buttons_items_show_all = [
    [KeyboardButton(text="🔍 Поиск"), KeyboardButton(text="️📊 Статистика")],
    [KeyboardButton(text="️🧹 Удалить все записи в папке")],
    [KeyboardButton(text="↪️ Перейти к общему виду папки 🗂️📄")]
]

general_buttons_edit_item_files = [
    [
        KeyboardButton(text="☑️ Выбрать все"),
        KeyboardButton(text="✖️ Отменить выбор")
    ],
    [
        KeyboardButton(text="🗑 Удалить выбранные ☑️"),
        KeyboardButton(text="🧹 Удалить все файлы 🗃️")
    ],
    [
        complete_edit_item_button
    ],
]

leave_current_caption_button = KeyboardButton(text="☑️ Оставить текущую подпись")
remove_current_caption_button = KeyboardButton(text="🧹 Удалить подпись")

general_buttons_edit_file_caption = [
    [
        remove_current_caption_button,
        leave_current_caption_button
    ],
    [
        complete_edit_item_button
    ],
]

cancel_add_mode_button = KeyboardButton(text="️🚫 Отменить дополнение записи")
general_buttons_add_mode = [
    [
        cancel_add_mode_button
    ],
]

without_title_button = KeyboardButton(text="💾 Сохранить без заголовка")
add_to_item_button = KeyboardButton(text="❇️ Дополнить")
cancel_save_new_item_button = KeyboardButton(text="✖️ Не сохранять запись") # ✖️ ❌

general_new_item_buttons = [
    [
        without_title_button,
    ],
    [
        add_to_item_button,
        cancel_save_new_item_button
    ],
]

general_add_to_new_item_mode_buttons = [
    [
        cancel_add_mode_button,
        cancel_save_new_item_button,
    ],
]

general_buttons_movement_item = [
    [KeyboardButton(text="🔀 Переместить в текущую папку")],
    [KeyboardButton(text="️🚫 Отменить перемещение")],
]

general_buttons_search_items = [
    [KeyboardButton(text="🔄 Новый поиск 🔍️")],
    [KeyboardButton(text="❎ Завершить режим поиска 🔍️")],
]

general_buttons_statistic_folder = [
    [KeyboardButton(text="️↩️ Назад к папке")],
]

ok_info_button = InlineKeyboardButton(text="👌 Понятно", callback_data="ok_info")
skip_enter_item_title_button = InlineKeyboardButton(text="Без заголовка", callback_data="skip_enter_item_title")
cancel_add_new_item_button = InlineKeyboardButton(text="Не добавлять запись", callback_data="cancel_add_new_item")

text_pages_buttons = [
    InlineKeyboardButton(text="◀️", callback_data="prev_text_page"),
    InlineKeyboardButton(text="", callback_data="all_text_pages"),
    InlineKeyboardButton(text="▶️", callback_data="next_text_page"),
]

item_inline_buttons = [
    # text_pages_buttons,
    [
        InlineKeyboardButton(text="Поделиться", switch_inline_query="none"),
        InlineKeyboardButton(text="✖️ Закрыть", callback_data="close_item"),

    ],
    [
        InlineKeyboardButton(text="❇️ Дополнить", callback_data="add_to_item"),
        InlineKeyboardButton(text="📝 Редактировать", callback_data="edit_item"),

    ],

    [
        InlineKeyboardButton(text="🔀 Переместить", callback_data="move_item"),
        InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_item"),

    ]
]

show_smile = "📤"
hide_smile = "📥"

show_item_files_button = InlineKeyboardButton(text=f"📖Открыть файлы", callback_data="show_item_files")
hide_item_files_button = InlineKeyboardButton(text=f"📨 Скрыть файлы", callback_data="hide_item_files")


class FilesButtons:

    @staticmethod
    def get_button(button_source: InlineKeyboardButton, files_count):
        button = button_source.model_copy()
        button.text = f"{button.text} ({files_count})"
        return button

    @staticmethod
    def get_show_button(files_count):
        return FilesButtons.get_button(show_item_files_button, files_count)

    @staticmethod
    def get_hide_button(files_count):
        return FilesButtons.get_button(hide_item_files_button, files_count)


item_inline_buttons_with_files = [
    # text_pages_buttons,
    [
        InlineKeyboardButton(text="Поделиться", switch_inline_query="none"),
        InlineKeyboardButton(text="✖️ Закрыть", callback_data="close_item"),
    ],
    [
        InlineKeyboardButton(text="❇️", callback_data="add_to_item"),
        InlineKeyboardButton(text="📝", callback_data="edit_item"),
        InlineKeyboardButton(text="🔀", callback_data="move_item"),
        InlineKeyboardButton(text="🗑", callback_data="delete_item"),
    ],
    [
        InlineKeyboardButton(text="🧐 Обзор контента", switch_inline_query_current_chat="none"),
        show_item_files_button,
    ],
    # show_item_files_buttons
]

item_edit_buttons = [
    [
        InlineKeyboardButton(text="✏️ Заголовок", callback_data="edit_item_title"),
        InlineKeyboardButton(text="📝 Текст", callback_data="edit_item_text"),
        InlineKeyboardButton(text="🗃️ Файлы", callback_data="edit_item_files"),
    ],
    [
        InlineKeyboardButton(text="↩️ Назад", callback_data="edit_item_back")
    ]
]

save_file_buttons = [
    [
        InlineKeyboardButton(text="💾 Сохранить", callback_data="save_file"),
        InlineKeyboardButton(text="✖️ Закрыть", callback_data="close_entity"),
    ]
]

save_page_buttons = [
    [
        InlineKeyboardButton(text="💾 Сохранить", callback_data="save_text_page"),
        InlineKeyboardButton(text="✖️ Закрыть", callback_data="close_entity"),
    ]
]

save_item_full_mode_button = InlineKeyboardButton(text="💾 Сохранить", callback_data="save_item")


# Определяем функцию для создания разметки ответа для общего использования
def create_general_reply_markup(buttons):
    markup = ReplyKeyboardMarkup(keyboard=[*buttons], resize_keyboard=True, row_width=3)
    return markup


def check_button_exists(keyboard: ReplyKeyboardMarkup, button_text: str) -> bool:
    if not keyboard:
        return False
    for row in keyboard.keyboard:
        for button in row:
            if button.text.lower() == button_text.lower():
                return True
    return False


def check_button_exists_part_of_text(keyboard: ReplyKeyboardMarkup, button_text: str) -> bool:
    if not keyboard:
        return False
    for row in keyboard.keyboard:
        for button in row:
            if button_text.lower() in button.text.lower():
                return True
    return False


def get_folders_with_items_inline_markup(folders_inline_markup, items_inline_markup):
    return merge_keyboards(folders_inline_markup, items_inline_markup)


def merge_keyboards(*markups):
    keyboard_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for markup in markups:
        keyboard_builder.attach(InlineKeyboardBuilder.from_markup(markup))
    return keyboard_builder.as_markup()


def get_edit_item_title_keyboard(item_title: str):
    if item_title:
        return [
            [clean_title_buttons[0]],
            [complete_edit_item_button],
        ]
    else:
        return [
            [clean_title_buttons[1]],
            [complete_edit_item_button],
        ]


def get_edit_item_text_keyboard(item: Item):
    if item.pages_count() > 1 or item.page_not_empty(0):
        buttons = [
            [clean_text_buttons[0]],
            [complete_edit_item_button],
        ]
        # if len(item_text) > 1:
        #     buttons.insert(0, [delete_page_button])
    else:
        buttons = [
            [clean_text_buttons[1]],
            [complete_edit_item_button],
        ]
    return buttons


def get_edit_item_files_keyboard():
    return general_buttons_edit_item_files


def get_edit_file_caption_keyboard(caption: str):
    buttons = copy.deepcopy(general_buttons_edit_file_caption)
    if not caption:
        buttons[0].pop(0)
    return buttons


def get_text_pages_buttons(author_user_id: int, item: Item, page_number: int, mode='show'):
    pages_buttons = text_pages_buttons.copy()
    display_page_number = page_number + 1
    pages_buttons[1].text = f'{display_page_number} из {len(item.text)}'

    prev_page = page_number - 1 if page_number - 1 >= 0 else len(item.text) - 1
    next_page = page_number + 1 if page_number + 1 < len(item.text) else 0
    pages_buttons[0].callback_data = TextPagesCallback(
        author_user_id=author_user_id, item_id=item.id, action=f'prev{mode}', page=prev_page).pack()
    pages_buttons[1].callback_data = TextPagesCallback(
        author_user_id=author_user_id, item_id=item.id, action=f'all{mode}', page=page_number).pack()
    pages_buttons[2].callback_data = TextPagesCallback(
        author_user_id=author_user_id, item_id=item.id, action=f'next{mode}', page=next_page).pack()

    return pages_buttons


def get_edit_page_buttons():
    return [
        insert_page_inline_button,
        delete_page_inline_button
    ]


def get_repost_button_in_markup(inline_markup: InlineKeyboardMarkup):
    for keyboard in inline_markup.inline_keyboard:
        for button in keyboard:
            btn: InlineKeyboardButton = button
            if btn.text == 'Поделиться' and btn.switch_inline_query:
                return btn


def get_save_button_in_markup(inline_markup: InlineKeyboardMarkup):
    for keyboard in inline_markup.inline_keyboard:
        for button in keyboard:
            btn: InlineKeyboardButton = button
            if SaveItemCallback.__prefix__ in btn.callback_data:
                return btn


def get_voice_save_inline_markup(content_type: ContentType):
    builder = InlineKeyboardBuilder()
    if content_type == ContentType.VOICE:
        builder.button(
            text='🗣️ Голос',
            callback_data=VoiceSaveTypeCallback(type='voice').pack()
        )
    elif content_type == ContentType.VIDEO_NOTE:
        builder.button(
            text='📹 Видео',
            callback_data=VoiceSaveTypeCallback(type='video_note').pack()
        )
    builder.button(
        text='📃 Текст',
        callback_data=VoiceSaveTypeCallback(type='text').pack()
    )
    builder.button(
        text='🔄 Повторить',
        callback_data=ReadVoiceRunCallback().pack()
    )
    builder.button(
        text='✖️ Не сохранять',
        callback_data=MessageBoxCallback(result='close').pack()
    )
    builder.adjust(2, 2)
    return builder.as_markup()


def get_voice_read_inline_markup(content_type: ContentType, is_retry=False):
    read_voice_text = '📃 Распознать текст' if not is_retry else '🔄 Повторить'  # ⌨️📃
    cancel_text = '✖️ Отменить' if not is_retry else '✖️ Не сохранять'
    builder = InlineKeyboardBuilder()
    if content_type == ContentType.VOICE:
        builder.button(
            text='🗣️ Сохранить голос',
            callback_data=VoiceSaveTypeCallback(type='voice').pack()
        )
    elif content_type == ContentType.VIDEO_NOTE:
        builder.button(
            text='📹 Сохранить видео',
            callback_data=VoiceSaveTypeCallback(type='video_note').pack()
        )
    builder.button(
        text=read_voice_text,
        callback_data=ReadVoiceRunCallback().pack()
    )
    builder.button(
        text=cancel_text,
        callback_data=MessageBoxCallback(result='close').pack()
    )
    builder.adjust(2, 1)
    return builder.as_markup()


file_mark_on = '☑️'  # '🔴' # '✔️' # '✅' # '☑️'
file_mark_off = '◻️'  # '🔘' # '🔲' #'Выбрать'


def get_edit_file_inline_markup(item_id: str, content_type: ContentType, file_id, mark_is_on=False):
    mark = file_mark_on if mark_is_on else file_mark_off
    builder = InlineKeyboardBuilder()
    if file_has_caption(content_type):
        builder.button(
            text='✏️ Редактировать подпись',
            callback_data=EditFileCaptionCallback(item_id=item_id, type=content_type, file_id=file_id).pack()
        )
    builder.button(
        text=mark,
        callback_data=MarkFileCallback(item_id=item_id, type=content_type, file_id=file_id).pack()
    )
    builder.button(
        text='🗑 Удалить',
        callback_data=DeleteFileCallback(item_id=item_id, type=content_type, file_id=file_id).pack()
    )
    if file_has_caption(content_type):
        builder.adjust(1, 2)
    else:
        builder.adjust(2)
    return builder.as_markup()


def get_delete_file_inline_markup(item_id: str, content_type: ContentType, file_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='✔️Да, удалить',
        callback_data=RequestDeleteFileCallback(item_id=item_id, type=content_type, file_id=file_id, res='y').pack()
    )
    builder.button(
        text='✖️Не удалять',
        callback_data=RequestDeleteFileCallback(item_id=item_id, type=content_type, file_id=file_id, res='n').pack()
    )
    builder.adjust(2)
    return builder.as_markup()


def get_delete_files_inline_markup(item_id: str, is_all=False):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='✔️Да, удалить',
        callback_data=RequestDeleteFilesCallback(item_id=item_id, res='y', is_all=is_all).pack()
    )
    builder.button(
        text='✖️Не удалять',
        callback_data=RequestDeleteFilesCallback(item_id=item_id, res='n', is_all=is_all).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


def get_folder_control_inline_markup(user_id, folder_id):
    sizes = []
    builder = InlineKeyboardBuilder()
    builder.button(
        text='🔑 PIN-код',
        callback_data=PinFolderCallback(folder_id=folder_id).pack()
    )
    builder.button(
        text='🔐 Настроить доступ',
        callback_data=AccessFolderCallback(folder_id=folder_id).pack()
    )
    sizes.append(2)
    builder.button(
        text='📊 Статистика',
        callback_data=StatisticFolderCallback(folder_id=folder_id).pack()
    )
    builder.button(
        text='🧹Удалить все записи',
        callback_data=EditFolderCallback(folder_id=folder_id, action='delete_all_items').pack()
    )
    sizes.append(2)
    if folder_id != ROOT_FOLDER_ID:
        builder.button(
            text='✏️ Переименовать',
            callback_data=EditFolderCallback(folder_id=folder_id, action='rename').pack()
        )
        builder.button(
            text='🗑 Удалить папку',
            callback_data=EditFolderCallback(folder_id=folder_id, action='delete').pack()
        )
        sizes.append(2)
    builder.button(
        text='🔍 Поиск в папке и вложенных папках',
        callback_data=SearchInFolderCallback(folder_id=folder_id).pack()
    )
    sizes.append(1)
    builder.button(
        text='✖️ Закрыть меню',
        callback_data=MessageBoxCallback(result='close').pack()
    )
    sizes.append(1)
    builder.adjust(*sizes)
    return builder.as_markup()


def get_folder_pin_inline_markup(user_id, folder_id=None, pin: str = None):
    if not folder_id:
        folder_id = ROOT_FOLDER_ID

    if pin:
        pin_button_data = EnterPinCodeButtonCallback(folder_id=folder_id, pin=pin, pin_repeat='', visible=False).pack()
    else:
        pin_button_data = NewPinCodeButtonCallback(folder_id=folder_id, pin='', pin_repeat='', visible=False).pack()

    builder = InlineKeyboardBuilder()
    builder.button(
        text=str(INVISIBLE_CHAR * 7) + '➖ ➖ ➖ ➖   🫣',  # 👁️
        callback_data=pin_button_data
    )
    for n in range(1, 10):
        builder.button(
            text=str(n),
            callback_data=PinKeyboardNumberCallback(number=n, folder_id=folder_id).pack()
        )
    builder.button(
        text='×',
        callback_data=PinKeyboardButtonCallback(action='close', folder_id=folder_id).pack()
    )
    builder.button(
        text='0',
        callback_data=PinKeyboardNumberCallback(number=0, folder_id=folder_id).pack()
    )
    builder.button(
        text='«',
        callback_data=PinKeyboardButtonCallback(action='backspace', folder_id=folder_id).pack()
    )
    if pin:
        builder.button(
            text='🤯 Забыли PIN-код?',
            callback_data=PinKeyboardButtonCallback(action='forgot', folder_id=folder_id).pack()
        )
    builder.adjust(1, 3, 3, 3, 3)
    return builder.as_markup()


def get_pin_control_inline_markup(folder_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='🔄 Сменить PIN-код',
        callback_data=PinControlCallback(action='change', folder_id=folder_id).pack()
    )
    builder.button(
        text='🧹 Удалить PIN-код',
        callback_data=PinControlCallback(action='remove', folder_id=folder_id).pack()
    )
    builder.button(
        text='✖️ Закрыть',
        callback_data=MessageBoxCallback(result='close').pack()
    )
    builder.adjust(2, 1)
    return builder.as_markup()


def get_access_control_inline_markup(user_id, folder_id: str, has_users: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text='➕ Добавить пользователя',
        #callback_data=AccessControlCallback(action='add_user', folder_id=folder_id).pack()
        switch_inline_query=f'access_{user_id}_{folder_id}'
    )
    if has_users:
        builder.button(
            text='👥 Выбрать пользователя', # 👤
            callback_data=AccessControlCallback(action='select_user', folder_id=folder_id).pack()
        )
        builder.button(
            text='🚫 Приостановить доступ для всех',
            callback_data=AccessControlCallback(action='add_user', folder_id=folder_id).pack()
        )
    builder.button(
        text='✖️ Закрыть',
        callback_data=MessageBoxCallback(result='close').pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def get_access_provide_inline_markup(
        from_user_id,
        folder_id: str,
        access_type: AccessType,
        token: str,
        bot_link: str
) -> InlineKeyboardMarkup:

    folder_info = to_url_data(f'ap_{from_user_id}_{folder_id}_{access_type.value}_{token}')
    folder_info = folder_info[:64]
    print(f'folder_info = {folder_info}')
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'✅ Принять 🚀️',
        url=f'{bot_link}?start={folder_info}',
    )
    builder.adjust(1)
    return builder.as_markup()


def get_access_request_inline_markup(from_user_id, folder_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'Запросить доступ на просмотр папки 👓',
        callback_data=AccessRequestCallback(
            author_user_id=str(from_user_id), folder_id=folder_id, type=AccessType.READ.value
        ).pack()
    )
    builder.button(
        text=f'Запросить доступ на изменение cодержимого🖊️️',
        callback_data=AccessRequestCallback(
            author_user_id=str(from_user_id), folder_id=folder_id, type=AccessType.WRITE.value
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


def get_access_confirm_inline_markup(accessing_user_id: str, folder_id: str, access_type: AccessType):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='✔️ Подтвердить',
        callback_data=AccessConfirmCallback(acc_user_id=accessing_user_id, folder_id=folder_id, type=access_type.value, res=True).pack()
        #callback_data='access_confirm_ok'
    )
    builder.button(
        text='✖️ Отклонить',
        callback_data=AccessConfirmCallback(acc_user_id=accessing_user_id, folder_id=folder_id, type=access_type.value, res=False).pack()
        #callback_data='access_confirm_reject'
    )
    builder.adjust(2)
    return builder.as_markup()


def get_simple_inline_markup(button_text: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=button_text,
        callback_data=MessageBoxCallback(result='ok').pack()
    )
    return builder.as_markup()


def get_contact_support_admin_markup(button_answer_user_text: str, contact_user_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=button_answer_user_text,
        callback_data=AnswerUserAfterContactSupportCallback(contact_user_id=contact_user_id).pack()
    )
    builder.button(
        text='Закрыть',
        callback_data=MessageBoxCallback(result='close').pack(),
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_contact_support_user_markup(button_answer_admin_text: str, contact_user_id: str) -> InlineKeyboardMarkup:
    btn_close_text = await get_text(contact_user_id, 'close')
    builder = InlineKeyboardBuilder()
    builder.button(
        text=button_answer_admin_text,
        callback_data=AnswerAdminAfterAnswerUserContactSupportCallback().pack()
    )
    builder.button(
        text=btn_close_text,
        callback_data=MessageBoxCallback(result='close').pack(),
    )
    builder.adjust(1)
    return builder.as_markup()
