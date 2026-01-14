from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.price import PriceTick
from app.services.price_service import PriceService

router = APIRouter()

@router.get("/all", response_model=List[PriceTick])
def get_all_prices(
    ticker: str = Query(..., description="Тикер валюты (например, btc_usd)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Получение всех сохраненных данных по указанной валюте."""
    service = PriceService(db)
    return service.get_prices_by_ticker(ticker, skip=skip, limit=limit)

@router.get("/latest", response_model=PriceTick)
def get_latest_price(
    ticker: str = Query(..., description="Тикер валюты (например, btc_usd)"),
    db: Session = Depends(get_db)
):
    """Получение последней цены валюты."""
    service = PriceService(db)
    price = service.get_latest_price(ticker)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found for this ticker")
    return price

@router.get("/by_date", response_model=List[PriceTick])
def get_price_by_date(
    ticker: str = Query(..., description="Тикер валюты (например, btc_usd)"),
    date_from: Optional[int] = Query(None, description="Начальная дата (UNIX timestamp)"),
    date_to: Optional[int] = Query(None, description="Конечная дата (UNIX timestamp)"),
    db: Session = Depends(get_db)
):
    """Получение цены валюты с фильтром по дате."""
    service = PriceService(db)
    return service.get_price_by_date(ticker, date_from=date_from, date_to=date_to)
