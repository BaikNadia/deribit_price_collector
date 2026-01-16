from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Deribit Price Collector API",
    description="API для сбора и получения цен с биржи Deribit",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Deribit Price Collector API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


# Импортируем и подключаем роутеры позже
import sys

sys.path.append(".")
