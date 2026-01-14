import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging
import json  # ← ДОБАВЬТЕ ЭТОТ ИМПОРТ

logger = logging.getLogger(__name__)


class DeribitClient:
    """Клиент для работы с Deribit API"""

    def __init__(self):
        self.base_url = settings.DERIBIT_BASE_URL
        self.client_id = settings.DERIBIT_CLIENT_ID
        self.client_secret = settings.DERIBIT_CLIENT_SECRET
        self.timeout = aiohttp.ClientTimeout(total=10)

        logger.debug(f"DeribitClient initialized with URL: {self.base_url}")

    async def get_public_ticker(self, instrument_name: str) -> Optional[Dict[str, Any]]:
        """Получение текущей цены для инструмента"""
        url = f"{self.base_url}/public/ticker"
        params = {"instrument_name": instrument_name}

        logger.debug(f"Fetching ticker for {instrument_name}")

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    logger.debug(f"Response status: {response.status}")

                    if response.status == 200:
                        # ВАЖНО: сначала получаем текст, потом парсим JSON
                        response_text = await response.text()  # ← ИЗМЕНЕНИЕ ЗДЕСЬ
                        logger.debug(f"Response text length: {len(response_text)}")

                        try:
                            data = json.loads(response_text)  # ← ИЗМЕНЕНИЕ ЗДЕСЬ
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error for {instrument_name}: {e}")
                            logger.debug(f"Raw response: {response_text[:500]}")
                            return None

                        logger.debug(f"Parsed JSON: {data}")

                        if "result" in data:
                            result = data["result"]
                            if result is not None:  # ← ДОБАВЬТЕ ЭТУ ПРОВЕРКУ
                                logger.info(
                                    f"Got ticker for {instrument_name}: ${result.get('mark_price', 'N/A'):,.2f}")
                                return result
                            else:
                                logger.warning(f"Result is None for {instrument_name}")
                                return None
                        else:
                            logger.warning(f"No 'result' in response for {instrument_name}: {data}")
                            return None
                    else:
                        text = await response.text()
                        logger.error(f"API error for {instrument_name}: {response.status} - {text}")
                        return None

        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {instrument_name}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {instrument_name}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    async def get_multiple_tickers(self, instruments: List[str]) -> Dict[str, Any]:
        """Получение цен для нескольких инструментов"""
        logger.info(f"Fetching prices for {len(instruments)} instruments: {instruments}")

        # Создаем задачи для всех инструментов
        tasks = [self.get_public_ticker(instr) for instr in instruments]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Обрабатываем результаты
        prices = {}
        for instrument, result in zip(instruments, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {instrument}: {result}")
                continue

            if result is not None:  # ← ИЗМЕНЕНИЕ: проверяем на None
                prices[instrument] = result
            else:
                logger.warning(f"No data for {instrument}")

        logger.info(f"Successfully fetched {len(prices)}/{len(instruments)} instruments")
        return prices

    async def get_instruments(self, currency: str = "BTC") -> List[str]:
        """Получение списка доступных инструментов"""
        url = f"{self.base_url}/public/get_instruments"
        params = {"currency": currency, "kind": "future"}

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        response_text = await response.text()  # ← ИЗМЕНЕНИЕ
                        data = json.loads(response_text)  # ← ИЗМЕНЕНИЕ
                        if "result" in data:
                            instruments = [item["instrument_name"] for item in data["result"]]
                            return instruments
            return []
        except Exception as e:
            logger.error(f"Error getting instruments: {e}")
            return []
