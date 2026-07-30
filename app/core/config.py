from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False
    )

    bot_token: str
    database_url: str
    log_level: str = "INFO"


settings = Settings()

# Author: Anton Petnitsky
# GitHub: https://github.com/Mukller/countdown-bot
# Last modified: 2026-05-16 01:00:49 +0300
