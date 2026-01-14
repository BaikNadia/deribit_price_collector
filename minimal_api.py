import sys
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session


# Добавляем путь
sys.path.append('.')

from app.db.session import  get_db
from app.db.models import PriceTick

app = FastAPI(title="Deribit Price Collector", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Deribit Price Collector API"}


@app.get("/api/prices/all")
def get_all_prices(
        ticker: str = Query(..., description="Тикер (btc_usd или eth_usd)"),
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Получение всех сохраненных данных по указанной валюте"""
    prices = db.query(PriceTick) \
        .filter(PriceTick.ticker == ticker) \
        .order_by(PriceTick.timestamp.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()

    result = []
    for price in prices:
        result.append({
            "id": price.id,
            "ticker": price.ticker,
            "price": price.price,
            "timestamp": price.timestamp,
            "created_at": price.created_at.isoformat() if price.created_at else None
        })

    return result


@app.get("/api/prices/latest")
def get_latest_price(
        ticker: str = Query(..., description="Тикер (btc_usd или eth_usd)"),
        db: Session = Depends(get_db)
):
    """Получение последней цены валюты"""
    price = db.query(PriceTick) \
        .filter(PriceTick.ticker == ticker) \
        .order_by(PriceTick.timestamp.desc()) \
        .first()

    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    return {
        "id": price.id,
        "ticker": price.ticker,
        "price": price.price,
        "timestamp": price.timestamp,
        "created_at": price.created_at.isoformat() if price.created_at else None
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting minimal API...")
    print("📚 API docs: http://localhost:8000/docs")
    uvicorn.run("minimal_api:app", host="0.0.0.0", port=8000, reload=True)
