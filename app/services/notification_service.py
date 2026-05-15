from datetime import date, datetime, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from app.db.models import User, Countdown
from app.db.session import async_session
from app.core.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_daily_digest(self):
        """Send daily digest to all users whose notification time matches current time"""
        async with async_session() as session:
            current_time = datetime.now().time()
            current_date = date.today()

            # Get all users with notification_time matching current minute (with 1-minute tolerance)
            users = await session.execute(
                select(User).filter(
                    User.notification_time <= current_time
                )
            )
            users_list = users.scalars().all()

            for user in users_list:
                try:
                    # Get user's countdowns
                    countdowns = await session.execute(
                        select(Countdown).where(Countdown.user_id == user.id)
                    )
                    countdowns_list = countdowns.scalars().all()

                    if not countdowns_list:
                        continue

                    message = self._build_digest(countdowns_list, current_date)

                    await self.bot.send_message(
                        chat_id=user.telegram_id,
                        text=message,
                        parse_mode="Markdown"
                    )

                    logger.info(
                        "notification_sent",
                        telegram_id=user.telegram_id,
                        user_id=user.id,
                        countdown_count=len(countdowns_list)
                    )

                except Exception as e:
                    logger.error(
                        "notification_send_failed",
                        telegram_id=user.telegram_id,
                        error=str(e)
                    )

    def _build_digest(self, countdowns: list, today: date) -> str:
        """Build notification digest message"""
        digest = "📅 **Ежедневный дайджест**\n\n"

        today_events = []
        future_events = []
        past_events = []

        for countdown in countdowns:
            days_delta = (countdown.target_date - today).days

            if days_delta == 0:
                today_events.append(countdown)
            elif days_delta > 0:
                future_events.append((countdown, days_delta))
            else:
                past_events.append((countdown, abs(days_delta)))

        # Today's events
        if today_events:
            digest += "🎉 **Сегодня**\n"
            for cd in today_events:
                digest += f"- {cd.emoji} {cd.title}\n"
            digest += "\n"

        # Upcoming events (next 7 days)
        if future_events:
            upcoming = [e for e in future_events if e[1] <= 7]
            if upcoming:
                digest += "📆 **На этой неделе**\n"
                for cd, days in upcoming:
                    digest += f"- {cd.emoji} {cd.title} (осталось {days} дней)\n"
                digest += "\n"

        # Future events (more than 7 days)
        if future_events:
            later = [e for e in future_events if e[1] > 7]
            if later:
                digest += "📅 **В будущем**\n"
                for cd, days in later:
                    digest += f"- {cd.emoji} {cd.title} ({cd.target_date.strftime('%d.%m.%Y')})\n"
                digest += "\n"

        # Past events (yearly)
        if past_events:
            yearly = [e for e in past_events if e[0].repeat_type == "yearly"]
            if yearly:
                digest += "🔁 **Годовщины**\n"
                for cd, days in yearly:
                    digest += f"- {cd.emoji} {cd.title} (прошло {days} дней назад)\n"
                digest += "\n"

        if not digest.endswith("\n\n"):
            digest += "\n"

        digest += "_Бот Countdown_"

        return digest
