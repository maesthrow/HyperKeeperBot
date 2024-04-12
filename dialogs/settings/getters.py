from aiogram_dialog import DialogManager


async def get_language_data(dialog_manager: DialogManager, **kwargs):
    language = 'ru'
    if dialog_manager.find('ru').is_checked():
        language = 'ru'
    elif dialog_manager.find('en').is_checked():
        language = 'en'
    elif dialog_manager.find('es').is_checked():
        language = 'es'
    elif dialog_manager.find('fr').is_checked():
        language = 'fr'
    return {'language': language}