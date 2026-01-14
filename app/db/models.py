from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PriceTick(Base):
    __tablename__ = "price_ticks"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)  # 'btc_usd' или 'eth_usd'
    price = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False, index=True)  # UNIX timestamp

    # Опционально: можно добавить колонку с обычной датой-временем для удобства
    created_at = Column(DateTime, server_default=func.now())
