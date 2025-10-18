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

class PortfolioMetricsResponse(BaseModel):
    holding_metrics: List[HoldingMetrics]
    portfolio_summary: PortfolioSummary