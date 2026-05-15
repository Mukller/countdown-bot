from datetime import date
from calendar import monthrange, month_name
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class CalendarService:
    @staticmethod
    def get_calendar(year: int, month: int, today: date | None = None) -> InlineKeyboardMarkup:
        if today is None:
            today = date.today()

        keyboard = []

        # Header
        month_name_ru = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ][month - 1]

        header = [
            InlineKeyboardButton(text="<", callback_data=f"cal:{year}:{month-1 if month > 1 else 12}:{year if month > 1 else year-1}"),
            InlineKeyboardButton(text=f"{month_name_ru} {year}", callback_data="noop"),
            InlineKeyboardButton(text=">", callback_data=f"cal:{year}:{month+1 if month < 12 else 1}:{year if month < 12 else year+1}"),
        ]
        keyboard.append(header)

        # Days of week
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        keyboard.append([InlineKeyboardButton(text=day, callback_data="noop") for day in days_of_week])

        # Days
        first_day_weekday, days_in_month = monthrange(year, month)
        first_day_weekday = (first_day_weekday + 1) % 7

        days = []
        # Previous month days
        prev_month_days = monthrange(year, month - 1)[1] if month > 1 else monthrange(year - 1, 12)[1]
        for i in range(first_day_weekday, 0, -1):
            days.append(prev_month_days - i + 1)

        # Current month days
        for i in range(1, days_in_month + 1):
            days.append(i)

        # Next month days
        remaining = 42 - len(days)
        for i in range(1, remaining + 1):
            days.append(i)

        # Create calendar grid
        for i in range(0, len(days), 7):
            week = []
            for j in range(7):
                idx = i + j
                day = days[idx]

                if idx < first_day_weekday or idx >= first_day_weekday + days_in_month:
                    # Grayed out day
                    week.append(InlineKeyboardButton(text=" ", callback_data="noop"))
                else:
                    current_date = date(year, month, day)
                    is_today = current_date == today
                    text = f"●{day}" if is_today else str(day)
                    week.append(
                        InlineKeyboardButton(
                            text=text,
                            callback_data=f"calday:{year}:{month}:{day}"
                        )
                    )
            keyboard.append(week)

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
