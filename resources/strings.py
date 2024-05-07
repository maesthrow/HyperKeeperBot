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
    'user_profile': {
        Language.RUSSIAN: "👤 Мой профиль",
        Language.ENGLISH: "👤 My profile",
    },
    'help': {
        Language.RUSSIAN: "❔ Помощь",
        Language.ENGLISH: "❔ Help",
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
    'help_commands': {
        Language.RUSSIAN: """<b>Добро пожаловать в раздел помощи Телеграм-бота HyperKeeper 🚀</b>
        
Наш бот разработан для того, чтобы предоставить вам интуитивно понятный и эффективный способ управления вашим личным хранилищем, поиска данных и многого другого. Вот краткое описание основных команд, которое поможет вам начать работу и максимально эффективно использовать доступные функции :

<b>🗂️ Доступ к вашему хранилищу</b>
/storage

Используйте кнопку "🗂️ Открыть хранилище", чтобы открыть и управлять вашим личным пространством хранения.
Внутри хранилища вы можете:
Создавать папки для организации ваших данных.
Сохранять файлы и создавать записи.
Делиться этим с друзьями или предоставлять им доступ к целым папкам.

<b>🔍 Функционал поиска</b>
/search

Выполните глобальный поиск, отправив @{bot_username} <i>ваш_запрос</i> или используя кнопку "🔍 Глобальный поиск 🌐".
Вы можете осуществлять поиск внутри:
Папок, используя @{bot_username} folders/<i>ваш_запрос</i>
Записей, используя @{bot_username} items/<i>ваш_запрос</i>
Файлов, используя @{bot_username} files/<i>ваш_запрос</i>

<b>👤 Управление вашим профилем</b>
/profile

Получите доступ и обновите настройки вашего профиля, нажав на кнопку "👤 Мой профиль".

<b>🔐 Доступ от других пользователей</b>
/access

Просмотрите и управляйте разрешениями доступа, которые другие пользователи вам предоставили, нажав на кнопку "🔐 Доступы от других пользователей".

<b>️⚙️ Настройки</b>
/settings

Настройте свой опыт, изменяя параметры, такие как язык интерфейса и количество папок или записей на странице. Доступ к этому осуществляется через кнопку "⚙️ Настройки".

<b>❔ Нужна дополнительная помощь?</b>
/help

Если у вас есть вопросы или нужна дополнительная помощь, используйте кнопку "💬 Написать в поддержку".

Не стесняйтесь исследовать и использовать функции для улучшения вашего опыта управления данными. Наш бот здесь, чтобы помогать вам на каждом шагу! Приятного использования! ☺️""",
        Language.ENGLISH: """<b>Welcome to the Help Section of Telegram Bot HyperKeeper 🚀</b>

Our bot is designed to provide you with an intuitive and efficient way to manage your personal storage, search data, and much more. Here's a quick commands description to help you get started and make the most of the features available:

<b>🗂️ Accessing Your Storage</b>
/storage

Click on the "🗂️ Open storage" button to open and manage your personal storage space.
Inside the storage, you can:
Create folders to organize your data.
Save files and create records.
Share these with friends or grant them access to entire folders.

<b>🔍 Search Functionality</b>
/search

Perform a Global Search by sending @{bot_username} <i>your_query</i> or by using the "🔍 Global Search 🌐" button.
You can specifically search within:
Folders using @{bot_username} folders/<i>your_query</i>
Records using @{bot_username} items/<i>your_query</i>
Files using @{bot_username} files/<i>your_query</i>

<b>👤 Managing Your Profile</b>
/profile

Access and update your profile settings by clicking on the "👤 My profile" button.

<b>🔐 Access from Other Users</b>
/access

View and manage access permissions that other users have given you by clicking on the "🔐 Access from other users" button.

<b>⚙️ Settings</b>
/settings

Customize your experience by adjusting settings like the interface language and the number of folders or items displayed per page. Access this by clicking the "⚙️ Settings" button.

<b>❔ Need More Help?</b>
/help

If you have any questions or need further assistance, use the "💬 Contact Support" button.

Feel free to explore and utilize the features to enhance your data management experience. Our bot is here to assist you every step of the way! Enjoy using it! ☺️""",
    },

    'empty_access_users_message': {
        Language.RUSSIAN: "В этом разделе будет отображаться список пользователей, "
                          "которые предоставили вам доступ к содержимому их папок."
                          "\n\nЗдесь пока что ничего нет.",
        Language.ENGLISH: "This section will display a list of users who have granted you access "
                          "to the contents of their folders."
                          "\n\nThere is nothing here yet.",
    },

    'contact_support_title': {
        Language.RUSSIAN: "💬 Обращение в службу поддержки",
        Language.ENGLISH: "💬 Contact Support",
    },
    'quick_response': {
        Language.RUSSIAN: "💬 Быстрый ответ",
        Language.ENGLISH: "💬 Quick Response",
    },
    'contact_support_description': {
        Language.RUSSIAN: "Пожалуйста, напишите текст вашего запроса и отправьте его нам в сообщении:",
        Language.ENGLISH: "Please type your inquiry and send us the message:",
    },
    'after_contact_support_text': {
        Language.RUSSIAN: "спасибо за обращение! Мы постараемся связаться с вами в ближайшее время. 🙏",
        Language.ENGLISH: "thank you for reaching out! We will contact you as soon as possible. 🙏",
    },
    'answer_user_contact_support_title': {
        Language.RUSSIAN: "Ответ от службы поддержки по вашему обращению:",
        Language.ENGLISH: "Response from Support Regarding Your Inquiry:",
    },
    'close': {
        Language.RUSSIAN: "Закрыть",
        Language.ENGLISH: "Close",
    },

    'giga_menu_chats_title': {
        Language.RUSSIAN: "🧠 ChatGPT"
                          "\n\nВсе ваши чаты здесь! ☺️"
                          "\n\n<i>Вы можете вернуться к любому из них, либо начать новый:</i>",
        Language.ENGLISH: "🧠 ChatGPT"
                          "\n\nAll your chats are here! ☺️"
                          "\n\n<i>You can return to any of them or start a new one:</i>",
    },
    'giga_new_chat_title': {
        Language.RUSSIAN: "💬 Новый чат",
        Language.ENGLISH: "💬 New Chat",
    },
    'giga_chat_system_message': {
        Language.RUSSIAN: 'Ты эмпатичный вежливый бот-помощник мужского пола, тебя зовут "HyperKeeper🚀". '
                          'Ты помогаешь пользователю решить любые его задачи. '
                          'Ты очень умный и быстро улавливаешь суть контекста и всегда найдешь идеальный ответ.'
                          'Ты всегда рад и готов помочь!',
        Language.ENGLISH: 'You are an empathetic and polite male assistant bot named "HyperKeeper🚀". '
                          'You help users solve any of their tasks. '
                          'You are very intelligent and quickly grasp the essence of the context, '
                          'always finding the perfect answer. '
                          'You are always happy and ready to help!',
    },
    'start_chat_text': {
        Language.RUSSIAN: "Привет! Чем могу помочь?",
        Language.ENGLISH: "Hello! How can I help?",
    },
    'on_close_and_save_chat_text': {
        Language.RUSSIAN: "Сохранил нашу беседу. Был очень рад помочь вам! ☺️ Возвращайтесь скорее!",
        Language.ENGLISH: "I've saved our conversation. I was very glad to help you! ☺️ Hope to see you back soon!",
    },
    'on_close_chat_text': {
        Language.RUSSIAN: "До встречи! ☺️ Был рад помочь вам!",
        Language.ENGLISH: "Goodbye! ☺️ I was glad to help you!",
    },
    'over_limit_giga_chat_text': {
        Language.RUSSIAN: "К сожалению, вы исчерпали свой дневной лимит на обращения к ChatGPT."
                          "\nВозвращайтесь завтра, я буду рад снова вам помочь!",
        Language.ENGLISH: "Unfortunately, you've reached your daily limit for inquiries to ChatGPT."
                          "\nPlease come back tomorrow, I'll be happy to help you again!",
    }
}
