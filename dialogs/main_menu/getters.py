from aiogram_dialog import DialogManager

from models.item_model import INVISIBLE_CHAR
from utils.utils_ import smile_folder, smile_item, smile_file


async def get_start_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user = dialog_manager.event.from_user
    start_data = dialog_manager.current_context().start_data
    is_first_connect = start_data.get('is_first_connect', False) if start_data else False
    if is_first_connect:
        start_text = (f"👋 Привет, {user.first_name}, давайте начнем! 🚀️"
                      f"\n\nДля вас создано персональное хранилище. Чтобы открыть его - используйте команду /storage"
                      f"\n\nУправляйте вашими данными 💼:"
                      f"\n\n✅ Создавайте папки 🗂️ и записи 📄"
                      f"\n\n✅ Сохраняйте любые файлы 🗃️"
                      f"\n\n✅ Делитесь с друзьями своими записями и файлами или предоставляйте им доступ сразу к целым папкам!"
                      f"\n\nВсе основные команды вы найдете в главном <b>Меню</b>"
                      f"\n\nПриятного использования! ☺️")
    else:
        start_text = (f"👋 Привет, {user.first_name}, давайте начнем! 🚀️"
                      f"\n\nЧтобы открыть ваше персональное хранилище, используйте команду "
                      f"\n/storage"
                      f"\n\nУправляйте вашими данными 💼:"
                      f"\n\n✅ Создавайте папки 🗂️ и записи 📄"
                      f"\n\n✅ Сохраняйте любые файлы 🗃️"
                      f"\n\n✅ Делитесь с друзьями своими записями и файлами или предоставляйте им доступ сразу к целым папкам!"
                      f"\n\nВсе основные команды вы найдете в главном <b>Меню</b>"
                      f"\n\nПриятного использования! ☺️")

    data['start_text'] = start_text
    return data


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    return {
        'message_text': f'<b>☰ Меню</b>' # {INVISIBLE_CHAR * 40}'
    }


async def get_live_search_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.current_context().dialog_data
    live_search_title = f"🔍 <b>Live-поиск</b>"
    if not data:
        bot_username = (await dialog_manager.event.bot.get_me()).username
        prompt_text = f"{live_search_title}" \
                      "\n\n<i>Вводите поисковый запрос из любого чата, упоминая бота:</i>" \
                      "\n\nГлобальный поиск 🌐" \
                      f"\n'@{bot_username} <i>ваш_запрос'</i>" \
                      f"\n\nПоиск папок {smile_folder}" \
                      f"\n'@{bot_username} folders/<i>ваш_запрос</i>'" \
                      f"\n\nПоиск записей {smile_item}" \
                      f"\n'@{bot_username} items/<i>ваш_запрос</i>'" \
                      f"\n\nПоиск файлов {smile_file}" \
                      f"\n'@{bot_username} files/<i>ваш_запрос</i>'" \
                      "\n\n<i>Либо используйте кнопки</i> ⬇️"
    else:
        prompt_text = f"{live_search_title}{INVISIBLE_CHAR*20}"
    data = {'message_text': prompt_text}
    dialog_manager.current_context().dialog_data = data
    return data
