from dataclasses import dataclass
from typing import List

from pydantic import BaseModel

@dataclass
class HoldingMetrics:
    symbol: str
    name: str
    shares: int
    avg_cost: float
    current_price: float
    cost_basis: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    days_pnl: float
    weightage: float
    industry: str

@dataclass
class SectorAllocation:
    sector: str
    current_value: float
    weight: float
    holdings: List[str] 

@dataclass
class PortfolioSummary:
    total_invested: float
    total_current_value: float
    total_pnl: float
    total_return_pct: float
    sector_allocations: List[SectorAllocation]

@dataclass
class StockRiskMetrics:
    symbol: str
    beta: float
    weightage: float
    unrealized_pnl: float
    risk_meter: str
    standard_deviation: float

@dataclass
class PortfolioRiskMetrics:
    beta: float
    total_pnl: float
    sector_allocations: List[SectorAllocation]
    standard_deviation: float
    top_3_holdings_weightage: float
    herfindahl_index: float
    sector_concentration: float

class PortfolioMetricsResponse(BaseModel):
    holding_metrics: List[HoldingMetrics]
    portfolio_summary: PortfolioSummary

    class Config:
        from_attributes = True

class PortfolioRiskMetricsResponse(BaseModel):
    stocks_risk_metrics: List[StockRiskMetrics]
    portfolio_risk_metrics: PortfolioRiskMetrics

    class Config:
        from_attributes = True