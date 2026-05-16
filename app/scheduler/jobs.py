from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from aiogram import Bot
from app.services.notification_service import NotificationService
from app.db.models import User
from app.db.session import async_session
from app.core.logger import get_logger

logger = get_logger(__name__)

# Module-level variable to store scheduler instance
_scheduler: AsyncIOScheduler | None = None
_notification_service: NotificationService | None = None


async def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """Setup APScheduler with per-user notification jobs"""
    global _scheduler, _notification_service

    scheduler = AsyncIOScheduler()
    _scheduler = scheduler
    _notification_service = NotificationService(bot)

    # Get all users and create individual jobs for each
    async with async_session() as session:
        users = await session.execute(select(User))
        users_list = users.scalars().all()

        for user in users_list:
            if user.notification_time:
                hour = user.notification_time.hour
                minute = user.notification_time.minute

                scheduler.add_job(
                    _notification_service.send_digest_for_user,
                    'cron',
                    hour=hour,
                    minute=minute,
                    args=(user.id,),
                    id=f'daily_digest_user_{user.id}',
                    name=f'Send daily digest to user {user.id}',
                    replace_existing=True
                )

                logger.info(
                    "scheduler_job_added",
                    user_id=user.id,
                    notification_time=str(user.notification_time)
                )

    return scheduler


async def update_user_notification_job(user_id: int, notification_time) -> None:
    """Update or recreate a user's scheduler job when their notification_time changes"""
    global _scheduler, _notification_service

    if not _scheduler or not _notification_service:
        logger.warning("scheduler_not_initialized", user_id=user_id)
        return

    job_id = f'daily_digest_user_{user_id}'

    # Remove existing job if it exists
    if _scheduler.get_job(job_id):
        _scheduler.remove_job(job_id)

    # Add new job with updated time
    if notification_time:
        hour = notification_time.hour
        minute = notification_time.minute

        _scheduler.add_job(
            _notification_service.send_digest_for_user,
            'cron',
            hour=hour,
            minute=minute,
            args=(user_id,),
            id=job_id,
            name=f'Send daily digest to user {user_id}',
            replace_existing=True
        )

        logger.info(
            "scheduler_job_updated",
            user_id=user_id,
            notification_time=str(notification_time)
        )
