import asyncio
from collections import defaultdict
from decimal import Decimal
from app.models.ism_api.stock import ISMStockDetailsResponse
from app.models.portfolio_metrics import HoldingMetrics, PortfolioSummary, SectorAllocation
from app.schemas.holding import Holding
from app.services.ism_api import ISMApi
from typing import Dict, List

from app.services.openai_api import OpenAIAPI


class PortfolioMetrics:
    def __init__(self, ism_api: ISMApi, openai_api: OpenAIAPI = None):
        self.ism_api = ism_api
        self.openai_api = openai_api

    async def _fetch_stock_details(self, symbols: List[str]) -> Dict[str, ISMStockDetailsResponse]:
        try:
            tasks = [self.ism_api.get_stock_details(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            stock_details_map = {}
            for symbol, result in zip(symbols, results):
                if isinstance(result, Exception):
                    print(f"Error fetching details for {symbol}: {str(result)}")
                    continue
                stock_details_map[symbol] = result

            return stock_details_map
        except Exception as e:
            raise RuntimeError(f"Error fetching stock details: {str(e)}")

    async def calculate_current_value_and_pnl(self, holdings: List[Holding]) -> tuple[List[HoldingMetrics], PortfolioSummary]:
        """
        Calculate current value and P&L for a list of holdings.
        """
        try:
            if not holdings:
                return [], PortfolioSummary(
                    total_invested=0.0, 
                    total_current_value=0.0, 
                    total_pnl=0.0, 
                    total_return_pct=0.0,
                    sector_allocations=[]
                )
            
            symbols = list({holding.symbol for holding in holdings})
            stock_details_map = await self._fetch_stock_details(symbols)

            holding_metrics_list: List[HoldingMetrics] = []
            total_invested = Decimal('0')
            total_current_value = Decimal('0')
            sector_values = defaultdict(Decimal)
            sector_holdings = defaultdict(list)

            for holding in holdings:
                stock_details = stock_details_map.get(holding.symbol)
                if not stock_details:
                    continue

                current_price = float(stock_details.current_price.nse or stock_details.current_price.bse or 0.0)
                prev_close = float(stock_details.stock_details_reusable_data.close or 0.0)
                industry = stock_details.industry or "Unknown"

                cost_basis = Decimal(str(holding.shares * holding.avg_cost))
                current_value = Decimal(str(holding.shares * current_price))
                unrealized_pnl = current_value - cost_basis
                unrealized_pnl_pct = (
                    float((Decimal(str(current_price)) - Decimal(str(holding.avg_cost))) / Decimal(str(holding.avg_cost)) * 100)
                    if holding.avg_cost > 0 else 0.0
                )
                days_pnl = holding.shares * (current_price - prev_close)
                sector_values[industry] += current_value
                sector_holdings[industry].append(holding.symbol)

                metrics = HoldingMetrics(
                    symbol=holding.symbol,
                    name=holding.name,
                    shares=holding.shares,
                    avg_cost=holding.avg_cost,
                    current_price=current_price,
                    cost_basis=float(cost_basis),
                    current_value=float(current_value),
                    unrealized_pnl=float(unrealized_pnl),
                    unrealized_pnl_pct=unrealized_pnl_pct,
                    days_pnl=days_pnl,
                    weightage=0.0,
                    industry=industry
                )
                holding_metrics_list.append(metrics)

                total_invested += cost_basis
                total_current_value += current_value

            total_pnl = total_current_value - total_invested
            total_return_pct = float((total_pnl / total_invested * 100) if total_invested > 0 else Decimal('0'))

            sector_allocations = []
            for industry, value in sector_values.items():
                sector_weight = float((value / total_current_value * 100) if total_current_value > 0 else Decimal('0'))
                sector_allocations.append(SectorAllocation(
                    sector=industry,
                    current_value=float(value),
                    weight=sector_weight,
                    holdings=sector_holdings[industry]
                ))

            for metrics in holding_metrics_list:
                metrics.weightage = float((Decimal(str(metrics.current_value)) / total_current_value * 100) 
                                                  if total_current_value > 0 else Decimal('0'))

            portfolio_summary = PortfolioSummary(
                total_invested=float(total_invested),
                total_current_value=float(total_current_value),
                total_pnl=float(total_pnl),
                total_return_pct=total_return_pct,
                sector_allocations=sector_allocations
            )

            return holding_metrics_list, portfolio_summary
        except Exception as e:
            raise RuntimeError(f"Error calculating current value and P&L: {str(e)}")
        
    async def analyze_portfolio_genai(self, holdings: List[Holding]) -> str:
        """
        Analyze the portfolio using a generative AI model.
        """
        try:
            if not holdings:
                return "No holdings to analyze."

            holdings_metrics_list, portfolio_summary = await self.calculate_current_value_and_pnl(holdings)

            prompt = f"""
            You are a professional portfolio analyst for Indian stock markets. 
            Analyze this portfolio data and generate a concise morning briefing (150 words max).

            Focus on:
            1. Overall portfolio health (one sentence)
            2. Top 2-3 notable movers and WHY (sector trends, stock-specific)
            3. One actionable insight or alert
            4. Tone: Professional but conversational, data-driven

            Portfolio holdings: {holdings_metrics_list}
            Portfolio summary: {portfolio_summary}
            """

            analysis = self.openai_api.generate_text(prompt)

            return analysis
        except Exception as e:
            raise RuntimeError(f"Error analyzing portfolio: {str(e)}")

