from aiogram.filters.state import StatesGroup, State


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


class FolderControlStates(StatesGroup):
    MainMenu = State()
    InfoMessage = State()
    StatisticMenu = State()
    DeleteAllItemsQuestion = State()
    Rename = State()
    Delete = State()
    AfterDelete = State()
    AccessMenu = State()
    AccessConfirm = State()
    AccessChooseUsers = State()

