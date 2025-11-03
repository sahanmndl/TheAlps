from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.investment_preference import RiskTolerance, InvestmentHorizon, TargetAnnualReturn, Sectors, MonthlyInvestmentRange

class InvestmentPreferenceBase(BaseModel):
    risk_tolerance: RiskTolerance
    investment_horizon: InvestmentHorizon
    target_annual_return: TargetAnnualReturn
    monthly_investment_range: MonthlyInvestmentRange
    preferred_sectors: List[Sectors] = Field(default_factory=list)
    avoid_sectors: List[Sectors] = Field(default_factory=list)
    max_position_size: Optional[float] = Field(None, gt=0, le=100)
    dividend_focus: bool = False
    esg_focus: bool = False

    class Config:
        from_attributes = True

class InvestmentPreferenceCreate(InvestmentPreferenceBase):
    pass

class InvestmentPreferenceUpdate(BaseModel):
    risk_tolerance: Optional[RiskTolerance] = None
    investment_horizon: Optional[InvestmentHorizon] = None
    target_annual_return: Optional[TargetAnnualReturn] = None
    monthly_investment_range: Optional[MonthlyInvestmentRange] = None
    preferred_sectors: Optional[List[Sectors]] = None
    avoid_sectors: Optional[List[Sectors]] = None
    max_position_size: Optional[float] = None
    dividend_focus: Optional[bool] = None
    esg_focus: Optional[bool] = None

    class Config:
        from_attributes = True

class InvestmentPreferenceOut(InvestmentPreferenceBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True