from pydantic import BaseModel, Field
from typing import Optional
import datetime

class HoldingBase(BaseModel):
    symbol: str = Field(..., example="TCS")
    name: str = Field(..., example="Tata Consultancy Services")
    isin_number: str = Field(..., example="INE467B01029")
    exchange: Optional[str] = Field(default="NSE")
    shares: int = Field(..., gt=0)
    avg_cost: float = Field(..., gt=0)
    holding_since: Optional[datetime.datetime] = Field(default=datetime.datetime.now(datetime.timezone.utc))

class HoldingCreate(HoldingBase):
    pass

class HoldingUpdate(BaseModel):
    shares: Optional[int] = None
    avg_cost: Optional[float] = None
    holding_since: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class HoldingOut(HoldingBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
