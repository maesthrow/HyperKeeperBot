from aiogram_dialog import DialogManager


async def get_start_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    user = dialog_manager.event.from_user
    start_data = dialog_manager.current_context().start_data
    is_first_connect = start_data['is_first_connect']
    if is_first_connect:
        start_text = (f"👋 Привет, {user.first_name}, давайте начнем! 🚀️"
                      f"\n\nДля вас создано персональное хранилище. Чтобы открыть его - используйте команду /storage"
                      f"\n\nУправляйте вашими данными 💼:"
                      f"\n\n✅ Создавайте папки 🗂️ и записи 📄"
                      f"\n\n✅ Сохраняйте любые файлы 🗃️"
                      f"\n\n✅ Делитесь с друзьями своими записями и файлами или предоставляйте им доступ сразу к целым папкам!"
                      f"\n\nВсе основные команды вы найдете в <b>Главном меню</b>"
                      f"\n\nПриятного использования! ☺️")
    else:
        start_text = (f"👋 Привет, {user.first_name}, давайте начнем! 🚀️"
                      f"\n\nЧтобы открыть ваше персональное хранилище, используйте команду "
                      f"\n/storage"
                      f"\n\nУправляйте вашими данными 💼:"
                      f"\n\n✅ Создавайте папки 🗂️ и записи 📄"
                      f"\n\n✅ Сохраняйте любые файлы 🗃️"
                      f"\n\n✅ Делитесь с друзьями своими записями и файлами или предоставляйте им доступ сразу к целым папкам!"
                      f"\n\nВсе основные команды вы найдете в <b>Главном меню</b>"
                      f"\n\nПриятного использования! ☺️")

    data['start_text'] = start_text
    return data


async def get_main_menu_data(dialog_manager: DialogManager, **kwargs):
    data = {}
    return data
