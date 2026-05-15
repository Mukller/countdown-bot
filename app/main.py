import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.core import settings, configure_logging, get_logger
from app.db import Base, engine
from app.bot.handlers import start, menu
from app.bot.middlewares import DBSessionMiddleware

logger = get_logger(__name__)


async def on_startup(bot: Bot):
    logger.info("bot_startup")
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
    dp.include_router(start.router)
    dp.include_router(menu.router)

    # Startup and shutdown
    await on_startup(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    asyncio.run(main())
