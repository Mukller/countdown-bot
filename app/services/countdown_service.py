from datetime import date, timedelta
from app.repositories.countdown_repository import CountdownRepository
from app.db.models import Countdown
from app.core.constants import REPEAT_TYPE_YEARLY


class CountdownService:
    def __init__(self, countdown_repo: CountdownRepository):
        self.countdown_repo = countdown_repo

    async def create_countdown(
        self,
        user_id: int,
        title: str,
        emoji: str,
        target_date: date,
        repeat_type: str = "none",
    ) -> Countdown:
        return await self.countdown_repo.create(
            user_id=user_id,
            title=title,
            emoji=emoji,
            target_date=target_date,
            repeat_type=repeat_type,
        )

    async def get_user_countdowns(self, user_id: int) -> list[Countdown]:
        return await self.countdown_repo.get_user_countdowns(user_id)

    async def delete_countdown(self, countdown_id: int) -> bool:
        return await self.countdown_repo.delete(countdown_id)

    def calculate_days(self, target_date: date, today: date | None = None) -> int:
        if today is None:
            today = date.today()
        return (target_date - today).days

    def format_countdown(self, countdown: Countdown, today: date | None = None) -> str:
        if today is None:
            today = date.today()

        days = self.calculate_days(countdown.target_date, today)

        if days == 0:
            status = "Сегодня"
        elif days > 0:
            status = f"Осталось {days} дней"
        else:
            status = f"Прошло {abs(days)} дней"

        repeat_text = "Каждый год" if countdown.repeat_type == REPEAT_TYPE_YEARLY else ""

        card = f"{countdown.emoji} {countdown.title}\n\n"
        card += f"📅 {countdown.target_date.strftime('%d.%m.%Y')}\n"
        card += f"⏳ {status}\n"
        if repeat_text:
            card += f"🔁 {repeat_text}\n"

        return card
