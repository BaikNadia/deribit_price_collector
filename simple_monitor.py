import os
import time
from datetime import datetime

import requests


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def monitor():
    print("=" * 80)
    print("DERIBIT PRICE COLLECTOR - LIVE MONITOR")
    print("=" * 80)

    while True:
        try:
            # Получаем данные
            health = requests.get("http://localhost:8000/health").json()
            stats = requests.get("http://localhost:8000/api/stats").json()
            prices = requests.get("http://localhost:8000/api/prices?limit=5").json()

            clear_screen()

            print("=" * 80)
            print("🚀 DERIBIT PRICE COLLECTOR - LIVE MONITOR")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)

            # Статус системы
            print("\n📊 SYSTEM STATUS:")
            print(
                f"  • API: {'✅ Healthy' if health.get('status') == 'healthy' else '❌ Unhealthy'}"
            )
            print(f"  • Database: {health.get('database', 'Unknown')}")
            print(f"  • Redis: {health.get('redis', 'Unknown')}")
            print(f"  • Total Records: {stats.get('total_records', 0):,}")

            if "instruments" in stats:
                print(f"  • Instruments Tracked: {len(stats['instruments'])}")
                for instr in stats["instruments"]:
                    print(f"    - {instr.get('name')}: {instr.get('count', 0)} records")

            # Последние цены
            print("\n📈 LATEST PRICES:")
            if prices.get("data"):
                for price in prices["data"][:5]:
                    time_str = (
                        price["timestamp"].split("T")[1][:8]
                        if "timestamp" in price
                        else "N/A"
                    )
                    print(
                        f"  • {time_str} | {price['instrument_name']:15} | ${price['price']:10,.2f} | {price['source']}"
                    )
            else:
                print("  No data yet...")

            # Статистика
            print("\n📊 STATISTICS:")
            print("  • Updates every: 30 seconds")
            print(f"  • Next update in: {30 - (int(time.time()) % 30)} seconds")
            print(
                f"  • Data since: {stats.get('time_range', {}).get('oldest', 'N/A')[:19] if stats.get('time_range') else 'N/A'}"
            )

            print("\n" + "=" * 80)
            print("Press Ctrl+C to exit | Auto-refresh every 5 seconds")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Make sure FastAPI server is running on http://localhost:8000")

        time.sleep(5)


if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped")
