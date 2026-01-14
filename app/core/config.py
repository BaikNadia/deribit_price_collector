import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения"""
    # База данных (из вашего .env)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "deribit_db")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASS: str = os.getenv("DB_PASS", "password")

    # Redis для Celery (из вашего .env)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    # Deribit API (из вашего .env)
    DERIBIT_CLIENT_ID: str = os.getenv("DERIBIT_CLIENT_ID", "")
    DERIBIT_CLIENT_SECRET: str = os.getenv("DERIBIT_CLIENT_SECRET", "")
    DERIBIT_BASE_URL: str = "https://test.deribit.com/api/v2"

    # Сформированная DATABASE_URL для SQLAlchemy
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


# Создаем экземпляр настроек
settings = Settings()
