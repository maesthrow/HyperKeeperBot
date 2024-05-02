from enums.enums import Language

STRINGS = {
    'empty_param': {
        Language.RUSSIAN: "empty_param",
        Language.ENGLISH: "empty_param",
    },
    'start_hello': {
        Language.RUSSIAN: "👋 Привет, {user_first_name}, давайте начнем! 🚀️",
        Language.ENGLISH: "👋 Hello, {user_first_name}, let's get started! 🚀️",
    },
    'lets_get_started': {
        Language.RUSSIAN: "давайте начнем",
        Language.ENGLISH: "let's get started",
    },
    'start_first': {
        Language.RUSSIAN: "\n\nДля вас создано персональное хранилище. Чтобы открыть его - используйте команду /storage"
                          "\n\nУправляйте вашими данными 💼:"
                          "\n\n✅ Создавайте папки 🗂️ и записи 📄"
                          "\n\n✅ Сохраняйте любые файлы 🗃️"
                          "\n\n✅ Делитесь с друзьями своими записями и файлами или предоставляйте им доступ сразу к целым папкам!"
                          "\n\nВсе основные команды вы найдете в главном <b>Меню</b>"
                          "\n\nПриятного использования! ☺️",
        Language.ENGLISH: "\n\nA personal storage space has been created for you. To access it, use the command /storage"
                          "\n\nManage your data 💼:"
                          "\n\n✅ Create folders 🗂️ and entries 📄"
                          "\n\n✅ Save any files 🗃️"
                          "\n\n✅ Share your entries and files with friends, or grant them access to entire folders!"
                          "\n\nYou can find all the main commands in the main <b>Menu</b>"
                          "\n\nEnjoy using it! ☺️",
    },
    'start': {
        Language.RUSSIAN: f"\n\nЧтобы открыть ваше персональное хранилище, используйте команду "
                          f"\n/storage"
                          f"\n\nУправляйте вашими данными 💼:"
                          f"\n\n✅ Создавайте папки 🗂️ и записи 📄"
                          f"\n\n✅ Сохраняйте любые файлы 🗃️"
                          f"\n\n✅ Делитесь с друзьями своими записями и файлами или предоставляйте им доступ сразу к целым папкам!"
                          f"\n\nВсе основные команды вы найдете в главном <b>Меню</b>"
                          f"\n\nПриятного использования! ☺️",
        Language.ENGLISH: "\n\nTo open your personal storage, use the command"
                          "\n/storage"
                          "\n\nManage your data 💼:"
                          "\n\n✅ Create folders 🗂️ and entries 📄"
                          "\n\n✅ Save any files 🗃️"
                          "\n\n✅ Share your entries and files with friends, or grant them access to entire folders!"
                          "\n\nAll main commands can be found in the main <b>Menu</b>"
                          "\n\nEnjoy using it! ☺️"
        ,
    },
    'menu': {
        Language.RUSSIAN: "Меню",
        Language.ENGLISH: "Menu",
    },
    'accesses_title': {
        Language.RUSSIAN: "🔐 <b>Доступы от других пользователей</b>",
        Language.ENGLISH: "🔐 <b>Access from other users</b>",
    },
    'language_title_text': {
        Language.RUSSIAN: "🌐 Язык интерфейса",
        Language.ENGLISH: "🌐 Interface Language",
    },
    'folders_on_page_count_title_text': {
        Language.RUSSIAN: "🗂️ Количество папок на странице",
        Language.ENGLISH: "🗂️ Number of Folders per Page",
    },
    'items_on_page_count_title_text': {
        Language.RUSSIAN: "📄 Количество записей на странице",
        Language.ENGLISH: "📄 Number of Items per Page",
    },
    'settings': {
        Language.RUSSIAN: "Настройки",
        Language.ENGLISH: "Settings",
    },
    'live_search_title': {
        Language.RUSSIAN: "🔍 <b>Live-поиск</b>",
        Language.ENGLISH: "🔍 <b>Live-search</b>",
    },
    'live_search_prompt_text_template': {
        Language.RUSSIAN:
            "\n\n<i>Вводите поисковый запрос из любого чата, упоминая бота:</i>\
            \n\nГлобальный поиск 🌐\
            \n'@{bot_username} <i>ваш_запрос</i>'\
            \n\nПоиск папок {smile_folder}\
            \n'@{bot_username} folders/<i>ваш_запрос</i>'\
            \n\nПоиск записей {smile_item}\
            \n'@{bot_username} items/<i>ваш_запрос</i>'\
            \n\nПоиск файлов {smile_file}\
            \n'@{bot_username} files/<i>ваш_запрос</i>'\
            \n\n<i>Либо используйте кнопки</i> ⬇️",
        Language.ENGLISH:
            "\n\n<i>Enter your search query from any chat by mentioning the bot:</i>\
            \n\nGlobal Search 🌐\
            \n'@{bot_username} <i>your_query</i>'\
            \n\nFolder Search {smile_folder}\
            \n'@{bot_username} folders/<i>your_query</i>'\
            \n\nRecord Search {smile_item}\
            \n'@{bot_username} items/<i>your_query</i>'\
            \n\nFile Search {smile_file}\
            \n'@{bot_username} files/<i>your_query</i>'\
            \n\n<i>Or use the buttons below</i> ⬇️",
    },
    'storage_empty_message': {
        Language.RUSSIAN: "В вашем Хранилище пока что ничего нет."
                          "\n\n❇️ Создайте собственное дерево папок, используя кнопки на клавиатуре в нижней части экрана."
                          "\n\n❇️ А для создания записи просто отправьте в чат сообщение с любым содержимым, "
                          "и я сохраню ваш контент в выбранную папку. "
                          "\n\nВперед! 🚀️",
        Language.ENGLISH: "Your Storage is currently empty."
                          "\n\n❇️ Create your own folder tree using the buttons on the keyboard at the bottom of the screen."
                          "\n\n❇️ To create a record, simply send a message with any content in the chat, "
                          "and I will save your content in the selected folder. "
                          "\n\nGo ahead! 🚀",
    },
}
