from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from app.services.notification_service import NotificationService
from app.core.logger import get_logger

logger = get_logger(__name__)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Setup APScheduler with notification jobs"""
    scheduler = AsyncIOScheduler()

    notification_service = NotificationService(bot)

    # Run notification check every minute
    scheduler.add_job(
        notification_service.send_daily_digest,
        'cron',
        minute='*',
        id='daily_digest',
        name='Send daily digest to users',
        replace_existing=True
    )

    return scheduler
