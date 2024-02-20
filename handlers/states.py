from aiogram.filters.state import StatesGroup, State


class Folder(StatesGroup):
    NewName = State()
    EditName = State()
    Delete = State()


class Item(StatesGroup):
    NewStepTitle = State()
    NewStepFolder = State()
    NewStepAdd = State()
    AddTo = State()
    ChooseTypeAddTextToNewItem = State()
    ChooseTypeAddText = State()
    EditTitle = State()
    EditText = State()
    Search = State()


class FileProcess(State):
    pass
