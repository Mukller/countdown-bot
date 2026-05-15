import asyncio
from alembic.config import Config
from alembic.command import upgrade
import os
from app.core.logger import get_logger

logger = get_logger(__name__)


async def run_migrations():
    """Run database migrations"""
    try:
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_ini = os.path.join(current_dir, "..", "..", "alembic.ini")

        if not os.path.exists(alembic_ini):
            logger.warning("alembic_ini_not_found", path=alembic_ini)
            return

        config = Config(alembic_ini)
        upgrade(config, "head")
        logger.info("migrations_completed")
    except Exception as e:
        logger.error("migrations_failed", error=str(e))
        raise
