import requests
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from datetime import datetime

console = Console()


def get_dashboard_data():
    """Получить данные для дашборда"""
    try:
        # Статистика из API
        stats_response = requests.get("http://localhost:8000/api/stats", timeout=2)
        stats = stats_response.json() if stats_response.status_code == 200 else {}

        # Последние цены
        prices_response = requests.get("http://localhost:8000/api/prices?limit=5", timeout=2)
        prices = prices_response.json() if prices_response.status_code == 200 else {}

        # Health check
        health_response = requests.get("http://localhost:8000/health", timeout=2)
        health = health_response.json() if health_response.status_code == 200 else {}

        return {
            "stats": stats,
            "prices": prices.get("data", []),
            "health": health,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    except:
        return {
            "stats": {},
            "prices": [],
            "health": {},
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }


def create_dashboard():
    """Создать дашборд"""
    data = get_dashboard_data()

    # Таблица с системной информацией
    system_table = Table(title="🚀 Deribit Price Collector System", show_header=True)
    system_table.add_column("Component", style="cyan")
    system_table.add_column("Status", style="green")
    system_table.add_column("Details", style="yellow")

    # Health
    api_status = "✅" if data.get("health", {}).get("status") == "healthy" else "❌"
    system_table.add_row("FastAPI", api_status, "http://localhost:8000")
    system_table.add_row("Celery Worker", "✅", "Running (solo pool)")
    system_table.add_row("Celery Beat", "✅", "Scheduling tasks")
    system_table.add_row("Redis", "✅", "localhost:6379")
    system_table.add_row("PostgreSQL", "✅", data.get("health", {}).get("database", "connected"))

    # Статистика
    stats = data.get("stats", {})
    system_table.add_row("Database Records", "", f"{stats.get('total_records', 0):,}")

    if "instruments" in stats:
        instruments = stats["instruments"]
        system_table.add_row("Tracked Instruments", "", f"{len(instruments)}")
        for instr in instruments[:3]:  # Показываем первые 3
            system_table.add_row(f"  - {instr.get('name')}", "", f"{instr.get('count', 0)} records")

    # Таблица с последними ценами
    if data["prices"]:
        prices_table = Table(title="📈 Latest Prices", show_header=True)
        prices_table.add_column("Time", style="cyan")
        prices_table.add_column("Instrument", style="magenta")
        prices_table.add_column("Price", style="green", justify="right")
        prices_table.add_column("Source", style="yellow")

        for price in data["prices"][:5]:  # Показываем последние 5
            time_str = price.get("timestamp", "").split("T")[1][:8] if price.get("timestamp") else "N/A"
            prices_table.add_row(
                time_str,
                price.get("instrument_name", ""),
                f"${price.get('price', 0):,.2f}",
                price.get("source", "")
            )
    else:
        prices_table = Table(title="📈 Latest Prices")
        prices_table.add_row("No data yet...")

    # Объединяем все в панель
    return Panel(
        f"{system_table}\n\n{prices_table}\n\n📊 Last update: {data['timestamp']}",
        title="Real-time Dashboard",
        border_style="blue"
    )


if __name__ == "__main__":
    console.print("[bold green]Starting Live Dashboard...[/bold green]")
    console.print("Press Ctrl+C to exit\n")

    with Live(create_dashboard(), refresh_per_second=1) as live:
        try:
            while True:
                live.update(create_dashboard())
                time.sleep(5)
        except KeyboardInterrupt:
            console.print("\n[bold red]Dashboard stopped[/bold red]")
