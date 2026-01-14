import aiohttp
from typing import Dict, Optional

class DeribitClient:
    def __init__(self, base_url: str = "https://test.deribit.com"):
        self.base_url = base_url

    async def get_index_price(self, currency: str) -> Optional[float]:
        """
        Получает индексную цену (index price) для заданной валюты.
        """
        # Приводим к формату API Deribit
        if currency.lower() == "btc_usd":
            index_name = "btc_usd"
        elif currency.lower() == "eth_usd":
            index_name = "eth_usd"
        else:
            index_name = currency.lower().replace("-", "_")

        url = f"{self.base_url}/api/v2/public/get_index_price"
        params = {"index_name": index_name}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result", {})
                        return result.get("index_price")
                    else:
                        print(f"Error fetching price for {currency}: {response.status}")
                        return None
        except Exception as e:
            print(f"Exception in DeribitClient for {currency}: {e}")
            return None

    async def fetch_btc_and_eth_prices(self) -> Dict[str, Optional[float]]:
        """
        Получает цены для BTC и ETH одновременно.
        """
        btc_price = await self.get_index_price("btc_usd")
        eth_price = await self.get_index_price("eth_usd")
        return {"btc_usd": btc_price, "eth_usd": eth_price}
