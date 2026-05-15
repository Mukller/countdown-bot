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

    scheduler.add_listener(
        lambda event: logger.info("scheduler_job_executed", job_id=event.job_id),
        mask='job_executed'
    )

    scheduler.add_listener(
        lambda event: logger.error(
            "scheduler_job_error",
            job_id=event.job_id,
            exception=str(event.exception)
        ),
        mask='job_error'
    )

    return scheduler
