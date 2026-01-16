from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# Используем DATABASE_URL из настроек
DATABASE_URL = settings.DATABASE_URL

# Создаем движок
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


# Функция для получения сессии (для зависимостей FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Импортируем модели для Alembic
# Этот импорт должен быть в конце файла, после определения Base
from app.db import models  # noqa
