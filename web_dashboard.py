from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from datetime import datetime
import asyncio

app = FastAPI(title="Deribit Price Collector Dashboard")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")


# Функция для получения данных
async def get_system_data():
    """Получить данные из API"""
    try:
        # Параллельные запросы
        health_url = "http://localhost:8000/health"
        stats_url = "http://localhost:8000/api/stats"
        prices_url = "http://localhost:8000/api/prices?limit=10"

        # Асинхронные запросы
        import aiohttp
        async with aiohttp.ClientSession() as session:
            tasks = [
                session.get(health_url),
                session.get(stats_url),
                session.get(prices_url)
            ]
            responses = await asyncio.gather(*tasks)

            health_data = await responses[0].json() if responses[0].status == 200 else {}
            stats_data = await responses[1].json() if responses[1].status == 200 else {}
            prices_data = await responses[2].json() if responses[2].status == 200 else {}

            return {
                "health": health_data,
                "stats": stats_data,
                "prices": prices_data.get("data", []),
                "timestamp": datetime.now().isoformat()
            }
    except:
        return {
            "health": {"status": "unknown"},
            "stats": {"total_records": 0},
            "prices": [],
            "timestamp": datetime.now().isoformat()
        }


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Главная страница дашборда"""
    data = await get_system_data()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "health": data["health"],
            "stats": data["stats"],
            "prices": data["prices"],
            "timestamp": data["timestamp"],
            "title": "Deribit Price Collector Dashboard"
        }
    )


@app.get("/api/dashboard")
async def dashboard_api():
    """API endpoint для дашборда"""
    return await get_system_data()


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("📊 Starting Web Dashboard...")
    print("🌐 Open: http://localhost:8080")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8080)
