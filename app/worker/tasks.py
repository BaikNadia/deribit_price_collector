from app.worker.celery_app import celery_app
from app.services.deribit_client import DeribitClient
from app.db.session import SessionLocal
from app.db.models import Price
import asyncio
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


@celery_app.task
def fetch_and_store_prices():
    """Задача для получения и сохранения цен"""
    logger.info("=" * 50)
    logger.info("🚀 STARTING: fetch_and_store_prices Celery task")
    logger.info("=" * 50)

    async def _async_fetch():
        # Создаем клиент Deribit
        client = DeribitClient()
        logger.info("✅ Deribit client created")

        # Инструменты для отслеживания
        instruments = [
            "BTC-PERPETUAL",
            "ETH-PERPETUAL",
        ]
        logger.info(f"📊 Fetching instruments: {instruments}")

        # Получаем цены
        prices = await client.get_multiple_tickers(instruments)
        logger.info(f"📈 Received data for {len(prices)} instruments")

        if not prices:
            logger.warning("⚠️ No prices received from Deribit")
            return {"status": "no_data", "records": 0}

        # Для отладки: выводим структуру данных
        for instrument_name, data in prices.items():
            if data:
                logger.debug(f"📋 Data for {instrument_name}:")
                logger.debug(f"  Available keys: {list(data.keys())}")
                if 'stats' in data:
                    logger.debug(f"  Stats keys: {list(data['stats'].keys())}")

        # Сохраняем в БД
        db = SessionLocal()
        try:
            count = 0
            for instrument_name, data in prices.items():
                if data and "mark_price" in data:
                    price_value = data.get("mark_price")

                    # Извлекаем дополнительные данные
                    stats = data.get("stats", {})
                    volume_usd = stats.get("volume_usd", 0)
                    volume_eth = stats.get("volume", 0)
                    price_change = stats.get("price_change", 0)

                    # Получаем время из API (если есть)
                    api_timestamp = data.get("timestamp")
                    if api_timestamp:
                        # API возвращает время в миллисекундах
                        record_timestamp = datetime.fromtimestamp(api_timestamp / 1000)
                    else:
                        record_timestamp = datetime.utcnow()

                    # Логируем для отладки
                    logger.info(f"💾 Saving {instrument_name}: ${price_value:,.2f}")
                    logger.debug(f"  Volume USD: ${volume_usd:,.2f}")
                    logger.debug(f"  Volume ETH: {volume_eth:,.2f}")
                    logger.debug(f"  24h Change: {price_change:.2f}%")
                    logger.debug(f"  Timestamp: {record_timestamp}")

                    price_record = Price(
                        instrument_name=instrument_name,
                        price=price_value,
                        mark_iv=data.get("mark_iv"),  # Волатильность, если есть
                        volume=volume_usd,  # Объем в USD
                        timestamp=record_timestamp,  # Время из API
                        source="deribit",
                        additional_data=data  # Сохраняем все данные
                    )
                    db.add(price_record)
                    count += 1

            db.commit()
            logger.info(f"✅ SUCCESS: Saved {count} price records")

            # Логируем сохраненные цены с деталями
            for instrument_name, data in prices.items():
                if data and "mark_price" in data:
                    stats = data.get("stats", {})
                    logger.info(
                        f"   📍 {instrument_name}: "
                        f"${data['mark_price']:,.2f} | "
                        f"24h Δ: {stats.get('price_change', 0):+.2f}% | "
                        f"Vol: ${stats.get('volume_usd', 0):,.0f}"
                    )

            return {"status": "success", "records": count}

        except Exception as e:
            db.rollback()
            logger.error(f"❌ ERROR saving prices: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"status": "error", "error": str(e)}
        finally:
            db.close()
            logger.info("🔒 Database session closed")

    # Запускаем асинхронный код
    try:
        result = asyncio.run(_async_fetch())
        logger.info(f"🏁 TASK COMPLETED: {result}")
        logger.info("=" * 50)
        return result
    except Exception as e:
        logger.error(f"💥 FATAL ERROR in task: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"status": "fatal_error", "error": str(e)}
