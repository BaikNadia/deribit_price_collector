from fastapi import APIRouter

from app.api.v1.endpoints import prices

api_router = APIRouter()
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
