from app.worker.celery_app import celery_app
from app.services.deribit_client import DeribitClient
from app.services.price_service import PriceService
from app.db.session import SessionLocal
import asyncio
import time

@celery_app.task
def fetch_and_store_prices():
    """
    Celery-задача для периодического получения и сохранения цен.
    """
    async def _async_fetch():
        db = SessionLocal()
        client = DeribitClient()
        service = PriceService(db)

        try:
            # Получаем цены
            prices = await client.fetch_btc_and_eth_prices()
            current_timestamp = int(time.time())  # Текущий UNIX timestamp

            # Сохраняем каждую цену в БД
            for ticker, price in prices.items():
                if price is not None:
                    await service.create_price_tick(
                        ticker=ticker,
                        price=price,
                        timestamp=current_timestamp
                    )
            print(f"✅ Prices fetched and stored at {current_timestamp}")
            print(f"   BTC: ${prices.get('btc_usd')}")
            print(f"   ETH: ${prices.get('eth_usd')}")
        except Exception as e:
            print(f"❌ Error fetching prices: {e}")
        finally:
            db.close()

    # Запускаем асинхронную функцию
    asyncio.run(_async_fetch())

# Конфигурация расписания (каждую минуту)
celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.worker.tasks.fetch_and_store_prices",
        "schedule": 60.0,  # секунды
    },
}
