from aiogram.dispatcher.filters.state import State, StatesGroup


class ViewValentineState(StatesGroup):
    GetValentines = State()
    GetAnAnswer = State()
    ViewValentine = State()


class SendValentineState(StatesGroup):
    GetPublish = State()
    GetUsername = State()
    GetText = State()
    GetPhotoAnswer = State()
    GetPhoto = State()
