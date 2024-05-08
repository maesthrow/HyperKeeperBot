from aiogram.filters.state import StatesGroup, State


class MainMenuState(StatesGroup):
    Start = State()
    Menu = State()
    LiveSearch = State()
    UserProfile = State()
    HelpMenu = State()


class SettingsMenuState(StatesGroup):
    Menu = State()
    Language = State()
    FoldersOnPageCount = State()
    ItemsOnPagesCount = State()


class StorageState(StatesGroup):
    OpenStorage = State()


class FolderState(StatesGroup):
    NewName = State()
    EditName = State()
    Delete = State()
    EnterPin = State()


class ItemState(StatesGroup):
    NewStepTitle = State()
    NewStepFolder = State()
    NewStepAdd = State()
    AddTo = State()
    ChooseTypeAddTextToNewItem = State()
    ChooseTypeAddText = State()
    EditTitle = State()
    EditText = State()
    EditFiles = State()
    EditFileCaption = State()
    Search = State()
    SearchResults = State()


class FileProcess(State):
    pass


class FolderControlState(StatesGroup):
    MainMenu = State()
    InfoMessage = State()
    StatisticMenu = State()
    DeleteAllItemsQuestion = State()
    Rename = State()
    Delete = State()
    AfterDelete = State()
    AccessMenu = State()
    AccessConfirm = State()
    AccessUserSelected = State()
    InfoMessageAccessUserSelected = State()
    StopAllUsersAccess = State()
    AfterStopAllUsersAccess = State()


class AccessesState(StatesGroup):
    UsersMenu = State()
    ShowUserFolders = State()
    ShowSelectedUserFolder = State()


class ItemControlState(StatesGroup):
    ShowItem = State()


class UserSupportState(StatesGroup):
    ContactSupport = State()
    AfterContactSupport = State()
    AnswerUserContactSupport = State()
    AfterAnswerUserContactSupport = State()


class GigaChatState(StatesGroup):
    MenuChats = State()
    SelectedChat = State()
    NewChat = State()
    Query = State()
