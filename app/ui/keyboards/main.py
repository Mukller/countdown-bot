from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать таймер", callback_data="create_countdown")],
            [InlineKeyboardButton(text="📋 Мои таймеры", callback_data="list_countdowns")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        ]
    )


def empty_state():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Создать таймер", callback_data="create_countdown")],
        ]
    )
