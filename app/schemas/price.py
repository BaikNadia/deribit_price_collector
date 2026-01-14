from pydantic import BaseModel
from datetime import datetime


class PriceTickBase(BaseModel):
    ticker: str
    price: float
    timestamp: int

class PriceTickCreate(PriceTickBase):
    pass

class PriceTick(PriceTickBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "ticker": "btc_usd",
                "price": 45000.50,
                "timestamp": 1678886400
            }
        }
