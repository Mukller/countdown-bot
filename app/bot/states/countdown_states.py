from aiogram.fsm.state import State, StatesGroup


class CountdownStates(StatesGroup):
    title = State()
    emoji = State()
    year = State()
    month = State()
    date = State()
    repeat = State()


class SettingsStates(StatesGroup):
    notification_time = State()
