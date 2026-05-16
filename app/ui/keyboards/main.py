from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать отсчёт", callback_data="create_countdown")],
            [InlineKeyboardButton(text="📋 Мои отсчёты", callback_data="list_countdowns")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        ]
    )


def empty_state():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать отсчёт", callback_data="create_countdown")],
        ]
    )
