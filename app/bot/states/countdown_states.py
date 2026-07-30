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

# Author: Anton Petnitsky
# GitHub: https://github.com/Mukller/countdown-bot
# Last modified: 2026-05-16 01:00:49 +0300
