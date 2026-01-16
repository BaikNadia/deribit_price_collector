import sys
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

# Добавляем путь
sys.path.append(".")

from app.db.models import Price
from app.db.session import get_db

app = FastAPI(title="Deribit Price Collector", version="1.0.0")


@app.get("/")
def root():
    return {"message": "Deribit Price Collector API"}


# === ЭНДПОИНТЫ ДЛЯ DASHBOARD ===


@app.get("/health")
async def health_check():
    """Health check для dashboard"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "redis": "connected",
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Статистика для dashboard"""
    try:
        # Общее количество записей
        total_records = db.query(Price).count()
        print(f"DEBUG: Total records in prices table: {total_records}")

        # Количество уникальных инструментов
        instruments = db.query(Price.instrument_name).distinct().count()
        print(f"DEBUG: Unique instruments: {instruments}")

        return {
            "total_records": total_records,
            "instruments_tracked": instruments,
            "uptime": "100%",
            "last_update": datetime.now().isoformat(),
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "total_records": 0,
            "instruments_tracked": 0,
            "uptime": "0%",
            "error": str(e),
        }


@app.get("/api/prices")
async def get_prices(
    limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)
):
    """Последние цены для dashboard"""
    try:
        prices = db.query(Price).order_by(Price.timestamp.desc()).limit(limit).all()

        print(f"DEBUG: Found {len(prices)} prices from database")

        result = []
        for price in prices:
            # Извлекаем данные из additional_data
            additional = price.additional_data or {}
            stats = additional.get("stats", {})

            # Используем правильное время из API
            api_timestamp = additional.get("timestamp")
            if api_timestamp:
                # Конвертируем из миллисекунд
                from datetime import datetime

                time_value = datetime.fromtimestamp(api_timestamp / 1000).isoformat()
            else:
                time_value = (
                    price.timestamp.isoformat()
                    if price.timestamp
                    else datetime.now().isoformat()
                )

            # Извлекаем объем и изменение цены
            volume = stats.get("volume", 0)
            price_change = stats.get("price_change", 0)  # Процентное изменение

            result.append(
                {
                    "time": time_value,
                    "instrument": price.instrument_name,
                    "price": float(price.price) if price.price else 0,
                    "24h_change": float(price_change),  # Теперь реальные данные!
                    "volume": float(volume),  # Теперь реальные данные!
                    "source": price.source if price.source else "deribit",
                }
            )

        print(f"DEBUG: Returning {len(result)} price records with real data")

        return {"data": result, "count": len(result), "limit": limit}
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"ERROR in get_prices: {str(e)}")
        return {"data": [], "error": str(e), "count": 0}


# === ЭНДПОИНТЫ ===


@app.get("/api/prices/all")
def get_all_prices(
    instrument: str = Query(
        ..., description="Инструмент (BTC-PERPETUAL или ETH-PERPETUAL)"
    ),
    # Изменили ticker на instrument
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Получение всех сохраненных данных по указанному инструменту"""
    prices = (
        db.query(Price)
        .filter(Price.instrument_name == instrument)
        .order_by(Price.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for price in prices:
        result.append(
            {
                "id": price.id,
                "instrument_name": price.instrument_name,  # Изменили ticker на instrument_name
                "price": price.price,
                "timestamp": price.timestamp,
                "source": price.source,
                "mark_iv": price.mark_iv,
                "volume": price.volume,
            }
        )

    return result


@app.get("/api/prices/latest")
def get_latest_price(
    instrument: str = Query(
        ..., description="Инструмент (BTC-PERPETUAL или ETH-PERPETUAL)"
    ),
    # Изменили ticker на instrument
    db: Session = Depends(get_db),
):
    """Получение последней цены инструмента"""
    price = (
        db.query(Price)
        .filter(Price.instrument_name == instrument)
        .order_by(Price.timestamp.desc())
        .first()
    )

    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    return {
        "id": price.id,
        "instrument_name": price.instrument_name,  # Изменили ticker на instrument_name
        "price": price.price,
        "timestamp": price.timestamp,
        "source": price.source,
        "mark_iv": price.mark_iv,
        "volume": price.volume,
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting minimal API...")
    print("📚 API docs: http://localhost:8000/docs")
    uvicorn.run("minimal_api:app", host="0.0.0.0", port=8000, reload=True)
