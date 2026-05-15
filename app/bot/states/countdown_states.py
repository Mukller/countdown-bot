from aiogram.fsm.state import State, StatesGroup


class CountdownStates(StatesGroup):
    title = State()
    emoji = State()
    date = State()
    repeat = State()


class SettingsStates(StatesGroup):
    notification_time = State()
