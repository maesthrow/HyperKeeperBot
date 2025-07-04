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
                          "\n\n✅ Делитесь с друзьями своим контентом или предоставляйте им доступ сразу к целым папкам!"
                          "\n\nВсе основные команды вы найдете в главном <b>Меню</b> ⬇️"
                          "\n\nПриятного использования! ☺️",
        Language.ENGLISH: "\n\nA personal storage space has been created for you. To access it, use the command /storage"
                          "\n\nManage your data 💼:"
                          "\n\n✅ Create folders 🗂️ and entries 📄"
                          "\n\n✅ Save any files 🗃️"
                          "\n\n✅ Share your content with friends, or grant them access to entire folders!"
                          "\n\nYou can find all the main commands in the main <b>Menu</b> ⬇️"
                          "\n\nEnjoy using it! ☺️",
    },
    'start': {
        Language.RUSSIAN: f"\n\nЧтобы открыть ваше персональное хранилище, используйте команду "
                          f"\n/storage"
                          f"\n\nУправляйте вашими данными 💼:"
                          f"\n\n✅ Создавайте папки 🗂️ и записи 📄"
                          f"\n\n✅ Сохраняйте любые файлы 🗃️"
                          f"\n\n✅ Делитесь с друзьями своим контентом или предоставляйте им доступ сразу к целым папкам!"
                          f"\n\nВсе основные команды вы найдете в главном <b>Меню</b> ⬇️"
                          f"\n\nПриятного использования! ☺️",
        Language.ENGLISH: "\n\nTo open your personal storage, use the command"
                          "\n/storage"
                          "\n\nManage your data 💼:"
                          "\n\n✅ Create folders 🗂️ and entries 📄"
                          "\n\n✅ Save any files 🗃️"
                          "\n\n✅ Share your content with friends, or grant them access to entire folders!"
                          "\n\nAll main commands can be found in the main <b>Menu</b> ⬇️"
                          "\n\nEnjoy using it! ☺️"
        ,
    },
    'you': {
        Language.RUSSIAN: "Вы",
        Language.ENGLISH: "You",
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
    'quick_search_title': {
        Language.RUSSIAN: "🔍 <b>Быстрый поиск</b>",
        Language.ENGLISH: "🔍 <b>Quick search</b>",
    },
    'quick_search_prompt_text_template': {
        Language.RUSSIAN:
            "\n\n<i>Вводите поисковый запрос из любого чата, упоминая бота:</i>\
            \n\nОбщий поиск 🌐\
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
            \n\nGeneral Search 🌐\
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
        
Наш бот разработан для того, чтобы предоставить вам интуитивно понятный и эффективный способ управления вашим личным хранилищем, поиска данных и многого другого.
Вот краткое описание основных команд, которое поможет вам начать работу и максимально эффективно использовать доступные функции:

<b>🗂️ Доступ к вашему хранилищу</b>
/storage

Используйте кнопку "🗂️ Открыть хранилище", чтобы управлять вашим личным пространством хранения.
Внутри хранилища вы можете:
 ✅ Создавать папки для организации ваших данных.
 ✅ Сохранять файлы и создавать записи.
 ✅ Делиться этим с друзьями или предоставлять им доступ к своим папкам.

<b>🧠 ChatGPT</b>
/gpt

Общайтесь с ChatGPT с возможностью сохранять ваши диалоги в отдельные чаты, к которым вы сможете вернуться, чтобы в любой момент продолжить беседу.
Используйте для этого кнопку "🧠 ChatGPT".

<b>🔐 Доступы от других пользователей</b>
/access

Просматаривайте контент, который другие пользователи предоставили вам.
Используйте для этого кнопку "🔐 Доступы от других пользователей".

<b>🔍 Функционал быстрого поиска</b>
/search

Используйте кнопки для общего поиска в вашем хранилище, а так же поиска папок, записей или файлов.

<b>👤 Ваш личный профиль</b>
/profile

Управляйте вашей подпиской и персональными данными, используя кнопку "👤 Мой профиль".

<b>️⚙️ Настройки</b>
/settings

Настройте свой опыт, изменяя параметры, такие как язык интерфейса и количество папок или записей на странице, используя кнопку "⚙️ Настройки".

<b>❔ Нужна дополнительная помощь?</b>
/help

Если у вас есть вопросы или нужна дополнительная помощь, используйте кнопку "💬 Написать в поддержку".

Не стесняйтесь исследовать и использовать функции для улучшения вашего опыта управления данными.
Наш бот создан, чтобы ежедневно помогать вам!
Приятного использования! ☺️""",

        Language.ENGLISH: """<b>Welcome to the help section of the HyperKeeper Telegram bot 🚀</b>

Our bot is designed to provide you with an intuitive and effective way to manage your personal storage, search for data, and much more.
Here's a brief overview of the main commands to help you get started and make the most of the available features:

<b>🗂️ Access to your storage</b>
/storage

Use the "🗂️ Open Storage" button to manage your personal storage space.
Inside the storage, you can:
 ✅ Create folders to organize your data.
 ✅ Save files and create records.
 ✅ Share this with friends or grant them access to your folders.

<b>🧠 ChatGPT</b>
/gpt

Communicate with ChatGPT with the option to save your dialogs in separate chats, which you can return to at any time to continue the conversation.
Use the "🧠 ChatGPT" button for this.

<b>🔐 Access from other users</b>
/access

View content that other users have shared with you.
Use the "🔐 Access from other users" button for this.

<b>🔍 Quick search functionality</b>
/search

Use buttons for general search in your storage, as well as for searching folders, records, or files.

<b>👤 Your personal profile</b>
/profile

Manage your subscription and personal data using the "👤 My Profile" button.

<b>️⚙️ Settings</b>
/settings

Customize your experience by changing settings such as interface language and the number of folders or records per page, using the "⚙️ Settings" button.

<b>❔ Need additional help?</b>
/help

If you have questions or need additional help, use the "💬 Contact Support" button.

Feel free to explore and use features to enhance your data management experience.
Our bot is created to help you every day!
Enjoy using it! ☺️""",
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
        Language.RUSSIAN: "<b>🧠 ChatGPT</b>"
                          "\n\nВсе ваши чаты здесь! ☺️"
                          "\n\n<i>Вы можете вернуться к любому из них, либо начать новый:</i>",
        Language.ENGLISH: "<b>🧠 ChatGPT</b>"
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
    },
    'gpt_make_title_chat_command': {
        Language.RUSSIAN: "Придумай и напиши краткий заголовок по теме и содержимому "
                          "этой беседы без учета этого сообщения и без каких либо пояснений, "
                          "что это заголовок, а так же без кавычек. "
                          "Длина заголовка должна быть не более 42 символов.",
        Language.ENGLISH: "Create and write a brief title for this chat based on its theme and content, "
                          "excluding this message and without any explanations that it is a title, "
                          "also without quotations. The title length should not exceed 42 characters.",

    },
    'delete_chat_question': {
        Language.RUSSIAN: "Хотите удалить этот чат?",
        Language.ENGLISH: "Do you want to delete this chat?",
    },
    'clear_chats_history_question': {
        Language.RUSSIAN: "Хотите очистить историю ваших чатов? Содержимое всех чатов будет удалено.",
        Language.ENGLISH: "Do you want to clear your chat history? The contents of all chats will be deleted.",
    },
    'chat_content_text': {
        Language.RUSSIAN: "📑 Содержание чата",
        Language.ENGLISH: "📑 Chat Content",
    },
    'delete_last_pair_chat_messages': {
        Language.RUSSIAN: "⌫ Удалить последнюю пару Запрос-Ответ", # ➿ 🗯️ ⌫ 🚮
        Language.ENGLISH: "⌫ Delete the last Question-Answer pair",
    },
}
