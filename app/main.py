import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.core import settings, configure_logging, get_logger
from app.db import Base, engine
from app.bot import handlers
from app.bot.middlewares import DBSessionMiddleware
from app.scheduler.jobs import setup_scheduler

logger = get_logger(__name__)


async def on_startup(bot: Bot):
    logger.info("bot_startup")
    # Create tables from models if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_shutdown(bot: Bot):
    logger.info("bot_shutdown")
    await bot.session.close()


async def main():
    configure_logging()
    logger.info("app_start")

    bot = Bot(token=settings.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register middlewares
    dp.message.middleware(DBSessionMiddleware())
    dp.callback_query.middleware(DBSessionMiddleware())

    # Register routers
    dp.include_router(handlers.start.router)
    dp.include_router(handlers.menu.router)
    dp.include_router(handlers.countdown_creation.router)
    dp.include_router(handlers.countdown_management.router)
    dp.include_router(handlers.settings.router)

    # Startup and shutdown
    await on_startup(bot)

    # Setup scheduler
    scheduler = setup_scheduler(bot)
    scheduler.start()
    logger.info("scheduler_started")

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        logger.info("scheduler_shutdown")
        await on_shutdown(bot)


if __name__ == "__main__":
    asyncio.run(main())
