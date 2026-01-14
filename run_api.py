import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Сначала импортируем настройки для проверки
try:
    from app.core.config import settings
    print("✅ Settings loaded successfully")
except ImportError as e:
    print(f"❌ Error loading settings: {e}")
    exit(1)

app = FastAPI(
    title="Deribit Price Collector API",
    description="API для сбора и получения цен с биржи Deribit",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Импортируем и подключаем роутеры
try:
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")
    print("✅ API router loaded successfully")
except ImportError as e:
    print(f"⚠️  API router not loaded: {e}")

@app.get("/")
def read_root():
    return {"message": "Deribit Price Collector API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting server on http://localhost:8000")
    print(f"📚 API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
