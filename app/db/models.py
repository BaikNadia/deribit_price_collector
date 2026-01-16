from sqlalchemy import JSON, Column, DateTime, Float, Index, Integer, String
from sqlalchemy.sql import func

from app.db.session import Base


class Price(Base):
    """Модель для хранения цен с Deribit"""

    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    instrument_name = Column(String(100), index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    source = Column(String(50), default="deribit")
    mark_iv = Column(Float, nullable=True)  # Волатильность (опционально)
    volume = Column(Float, nullable=True)  # Объем (опционально)
    additional_data = Column(JSON, nullable=True)  # Для хранения полного ответа API

    # Индексы для быстрого поиска
    __table_args__ = (
        Index("idx_instrument_timestamp", "instrument_name", "timestamp"),
        Index("idx_timestamp", "timestamp"),
    )

    def __repr__(self):
        return f"<Price {self.instrument_name}: {self.price} at {self.timestamp}>"

    def to_dict(self):
        """Конвертация в словарь"""
        return {
            "id": self.id,
            "instrument_name": self.instrument_name,
            "price": self.price,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source": self.source,
            "mark_iv": self.mark_iv,
            "volume": self.volume,
        }
