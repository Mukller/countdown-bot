from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from app.services.notification_service import NotificationService
from app.core.logger import get_logger

logger = get_logger(__name__)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Setup APScheduler with notification jobs"""
    scheduler = AsyncIOScheduler()

    notification_service = NotificationService(bot)

    # Run daily digest at 9 AM
    scheduler.add_job(
        notification_service.send_daily_digest,
        'cron',
        hour=9,
        minute=0,
        id='daily_digest',
        name='Send daily digest to users',
        replace_existing=True
    )

    return scheduler
