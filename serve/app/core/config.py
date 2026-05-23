from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "瘾了吗 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27020"
    MONGODB_DB: str = "yinlema"

    # JWT 配置
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
