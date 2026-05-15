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
