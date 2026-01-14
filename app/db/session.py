from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
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
