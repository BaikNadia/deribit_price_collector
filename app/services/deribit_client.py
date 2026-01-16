import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from app.core.config import settings

logger = logging.getLogger(__name__)


class DeribitClient:
    """Клиент для работы с Deribit API"""

    def __init__(self):
        self.base_url = settings.DERIBIT_BASE_URL
        self.client_id = settings.DERIBIT_CLIENT_ID
        self.client_secret = settings.DERIBIT_CLIENT_SECRET
        self.timeout = aiohttp.ClientTimeout(total=15)

        # Кэш для сессии (лучше переиспользовать)
        self._session = None

        logger.debug(f"DeribitClient initialized with URL: {self.base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получить или создать сессию"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={
                    "User-Agent": "DeribitPriceCollector/1.0",
                    "Accept": "application/json",
                },
            )
        return self._session

    async def close(self):
        """Закрыть сессию"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get_public_ticker(self, instrument_name: str) -> Optional[Dict[str, Any]]:
        """Получение текущей цены для инструмента"""
        url = f"{self.base_url}/api/v2/public/ticker"
        params = {"instrument_name": instrument_name}

        logger.debug(f"Fetching ticker for {instrument_name}")

        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                logger.debug(
                    f"Response status for {instrument_name}: {response.status}"
                )

                if response.status == 200:
                    # Получаем текст ответа
                    response_text = await response.text()

                    if not response_text or len(response_text.strip()) == 0:
                        logger.warning(f"Empty response for {instrument_name}")
                        return None

                    try:
                        data = json.loads(response_text)
                        logger.debug(f"JSON parsed for {instrument_name}")

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error for {instrument_name}: {e}")
                        logger.debug(
                            f"Raw response (first 500 chars): {response_text[:500]}"
                        )
                        return None

                    # Проверяем структуру ответа
                    if "result" not in data:
                        logger.warning(
                            f"No 'result' field in response for {instrument_name}"
                        )
                        logger.debug(f"Full response: {data}")
                        return None

                    result = data["result"]

                    if result is None:
                        logger.warning(f"Result is None for {instrument_name}")
                        return None

                    if not isinstance(result, dict):
                        logger.warning(
                            f"Result is not a dict for {instrument_name}: {type(result)}"
                        )
                        return None

                    # Добавляем timestamp если его нет
                    if "timestamp" not in result:
                        result["timestamp"] = int(datetime.now().timestamp() * 1000)

                    # Логируем успех с деталями
                    mark_price = result.get("mark_price", "N/A")
                    volume_24h = result.get("stats", {}).get("volume_usd", 0)
                    price_change = result.get("stats", {}).get("price_change", 0)

                    logger.info(
                        f"✅ Got ticker for {instrument_name}: "
                        f"${mark_price:,.2f} | "
                        f"24h Δ: {price_change:+.2f}% | "
                        f"Vol: ${volume_24h:,.0f}"
                    )

                    # Для отладки: выводим все доступные ключи
                    logger.debug(f"Available keys in result: {list(result.keys())}")
                    if "stats" in result:
                        logger.debug(f"Stats keys: {list(result['stats'].keys())}")

                    return result

                else:
                    text = await response.text() if response.status != 200 else ""
                    logger.error(
                        f"❌ API error for {instrument_name}: {response.status} - {text[:200]}"
                    )
                    return None

        except asyncio.TimeoutError:
            logger.error(f"⏰ Timeout fetching {instrument_name}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"🌐 Network error fetching {instrument_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"💥 Unexpected error fetching {instrument_name}: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    async def get_multiple_tickers(self, instruments: List[str]) -> Dict[str, Any]:
        """Получение цен для нескольких инструментов"""
        logger.info(
            f"📊 Fetching prices for {len(instruments)} instruments: {instruments}"
        )

        if not instruments:
            logger.warning("⚠️ No instruments provided")
            return {}

        # Создаем задачи для всех инструментов
        tasks = []
        for instrument in instruments:
            if not instrument or not isinstance(instrument, str):
                logger.warning(f"Invalid instrument: {instrument}")
                continue
            tasks.append(self.get_public_ticker(instrument))

        # Выполняем параллельно с таймаутом
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True), timeout=30
            )
        except asyncio.TimeoutError:
            logger.error("⏰ Timeout fetching multiple tickers")
            return {}
        except Exception as e:
            logger.error(f"💥 Error in gather: {e}")
            return {}

        # Обрабатываем результаты
        prices = {}
        successful = 0
        failed = 0

        for instrument, result in zip(instruments, results):
            if isinstance(result, Exception):
                logger.error(f"❌ Error fetching {instrument}: {result}")
                failed += 1
                continue

            if result is not None:
                prices[instrument] = result
                successful += 1

                # Для отладки: выводим структуру первого успешного результата
                if successful == 1:
                    logger.debug(f"📋 Sample data structure for {instrument}:")
                    logger.debug(f"  Top-level keys: {list(result.keys())}")
                    if "stats" in result:
                        logger.debug(f"  Stats: {result['stats']}")
            else:
                logger.warning(f"⚠️ No data for {instrument}")
                failed += 1

        logger.info(
            f"📈 Successfully fetched {successful}/{len(instruments)} instruments "
            f"({failed} failed)"
        )

        return prices

    async def get_instruments(
        self, currency: str = "BTC", kind: str = "future"
    ) -> List[str]:
        """Получение списка доступных инструментов"""
        url = f"{self.base_url}/api/v2/public/get_instruments"
        params = {
            "currency": currency,
            "kind": kind,
            "expired": "false",  # Только активные инструменты
        }

        logger.info(f"🔍 Getting instruments for {currency} ({kind})")

        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    response_text = await response.text()

                    if not response_text:
                        logger.warning("Empty response from get_instruments")
                        return []

                    data = json.loads(response_text)

                    if "result" not in data:
                        logger.warning("No 'result' in get_instruments response")
                        return []

                    instruments = []
                    for item in data["result"]:
                        if isinstance(item, dict) and "instrument_name" in item:
                            instruments.append(item["instrument_name"])

                    logger.info(f"📋 Found {len(instruments)} {currency} instruments")
                    return instruments
                else:
                    text = await response.text()
                    logger.error(
                        f"Error getting instruments: {response.status} - {text}"
                    )
                    return []
        except asyncio.TimeoutError:
            logger.error("Timeout getting instruments")
            return []
        except Exception as e:
            logger.error(f"Error getting instruments: {e}")
            return []

    async def get_historical_volatility(self, instrument_name: str) -> Optional[float]:
        """Получение исторической волатильности"""
        url = f"{self.base_url}/api/v2/public/get_historical_volatility"
        params = {"currency": instrument_name.split("-")[0]}

        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = json.loads(await response.text())
                    if "result" in data and data["result"]:
                        return data["result"]
        except Exception as e:
            logger.error(f"Error getting volatility for {instrument_name}: {e}")

        return None

    async def __aenter__(self):
        """Контекстный менеджер"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекста"""
        await self.close()


# Утилита для быстрого тестирования
async def test_deribit_client():
    """Тестирование клиента"""
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from app.core.config import settings

    print("🧪 Testing Deribit Client...")

    client = DeribitClient()
    try:
        # Тестируем один инструмент
        print("\n1. Testing single instrument...")
        btc_data = await client.get_public_ticker("BTC-PERPETUAL")
        if btc_data:
            print("✅ BTC-PERPETUAL data received")
            print(f"   Price: ${btc_data.get('mark_price', 'N/A'):,.2f}")
            print(
                f"   24h Change: {btc_data.get('stats', {}).get('price_change', 0):+.2f}%"
            )
            print(
                f"   24h Volume: ${btc_data.get('stats', {}).get('volume_usd', 0):,.0f}"
            )
        else:
            print("❌ Failed to get BTC data")

        # Тестируем несколько инструментов
        print("\n2. Testing multiple instruments...")
        instruments = ["BTC-PERPETUAL", "ETH-PERPETUAL"]
        prices = await client.get_multiple_tickers(instruments)

        print(f"✅ Got {len(prices)}/{len(instruments)} instruments")
        for instrument, data in prices.items():
            if data:
                print(f"   {instrument}: ${data.get('mark_price', 'N/A'):,.2f}")

        # Тестируем получение списка инструментов
        print("\n3. Testing instrument list...")
        btc_instruments = await client.get_instruments("BTC")
        print(f"✅ Found {len(btc_instruments)} BTC instruments")
        if btc_instruments:
            print(f"   First 5: {btc_instruments[:5]}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await client.close()
        print("\n🔒 Client closed")


if __name__ == "__main__":
    # Запуск теста
    asyncio.run(test_deribit_client())
