from aiogram.dispatcher.filters.state import StatesGroup, State


class GetDataEasy(StatesGroup):
    me = State()


class GetDataBirthDay(StatesGroup):
    me = State()


class GetDataHard(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    birth_day = State()


class Change(StatesGroup):
    first_name = State()
    last_name = State()
    phone = State()
    birth_day = State()
