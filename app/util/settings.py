from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Customer API"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = "sqlite:///./app.db"
    CORS_ALLOW_ORIGINS: str = "*"   # comma-separated list or "*"
    AI_USE_TRANSFORMERS: bool = False

    # New style config (replaces `class Config`)
    model_config = ConfigDict(env_file=".env")


settings = Settings()
