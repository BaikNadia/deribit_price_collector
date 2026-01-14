from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db import models
from app.db.models import PriceTick
from typing import Optional, Type


class PriceService:
    def __init__(self, db: Session):
        self.db = db

    async def create_price_tick(self, ticker: str, price: float, timestamp: int):
        db_price = models.PriceTick(
            ticker=ticker,
            price=price,
            timestamp=timestamp
        )
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price

    def get_prices_by_ticker(self, ticker: str, skip: int = 0, limit: int = 100) -> list[Type[PriceTick]]:
        return self.db.query(models.PriceTick)\
            .filter(models.PriceTick.ticker == ticker)\
            .order_by(desc(models.PriceTick.timestamp))\
            .offset(skip).limit(limit).all()

    def get_latest_price(self, ticker: str) -> Optional[models.PriceTick]:
        return self.db.query(models.PriceTick)\
            .filter(models.PriceTick.ticker == ticker)\
            .order_by(desc(models.PriceTick.timestamp))\
            .first()

    def get_price_by_date(
        self,
        ticker: str,
        date_from: Optional[int] = None,
        date_to: Optional[int] = None
    ) -> list[Type[PriceTick]]:
        query = self.db.query(models.PriceTick)\
            .filter(models.PriceTick.ticker == ticker)

        if date_from:
            query = query.filter(models.PriceTick.timestamp >= date_from)
        if date_to:
            query = query.filter(models.PriceTick.timestamp <= date_to)

        return query.order_by(desc(models.PriceTick.timestamp)).all()

