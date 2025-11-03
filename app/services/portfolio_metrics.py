import asyncio
from collections import defaultdict
from decimal import Decimal
from app.cache.redis import RedisService
from app.models.ism_api.stock import ISMStockDetailsResponse
from app.models.portfolio_metrics import HoldingMetrics, PortfolioRiskMetrics, PortfolioSummary, SectorAllocation, StockRiskMetrics
from app.schemas.holding import Holding
from app.services.ism_api import ISMApi
from typing import Dict, List, Optional, Tuple
from asyncio import Semaphore

from app.services.openai_api import OpenAIAPI
from app.utils.helper_functions import HelperFunctions


class PortfolioMetrics:
    def __init__(self, ism_api: ISMApi, openai_api: OpenAIAPI = None):
        self.ism_api = ism_api
        self.openai_api = openai_api
        self.cache = RedisService()
        self.helper_functions = HelperFunctions(ism_api)
        self.semaphore = Semaphore(5)  # Limit concurrent API calls

    async def _fetch_single_stock(self, symbol: str) -> Optional[ISMStockDetailsResponse]:
        async with self.semaphore:  # Control concurrent API calls
            try:
                result = await self.ism_api.get_stock_details(symbol)
                cache_key = f"stock_details:{symbol}"
                await self.cache.set(cache_key, result.model_dump(by_alias=True), expire_minutes=5)
                await self.helper_functions.cache_stock_specific_news(result.recent_news, symbol)
                print(f"Cached stock details for {cache_key}")
                return result
            except Exception as e:
                print(f"Error fetching details for {symbol}: {str(e)}")
                return None

    async def _fetch_stock_details(self, symbols: List[str]) -> Dict[str, ISMStockDetailsResponse]:
        try:
            stock_details_map = {}
            cache_miss_symbols = []
            retry_attempts = 3

            for symbol in symbols:
                cache_key = f"stock_details:{symbol}"
                cached_data = await self.cache.get(cache_key)
                if cached_data:
                    print(f"Cache hit for {cache_key}")
                    stock_details_map[symbol] = ISMStockDetailsResponse(**cached_data)
                else:
                    print(f"Cache miss for {cache_key}")
                    cache_miss_symbols.append(symbol)

            for attempt in range(retry_attempts):
                if not cache_miss_symbols:
                    break

                tasks = [self._fetch_single_stock(symbol) for symbol in cache_miss_symbols]
                results = await asyncio.gather(*tasks)

                next_retry_symbols = []
                for symbol, result in zip(cache_miss_symbols, results):
                    if result:
                        stock_details_map[symbol] = result
                    else:
                        next_retry_symbols.append(symbol)

                cache_miss_symbols = next_retry_symbols

                if cache_miss_symbols and attempt < retry_attempts - 1:
                    print(f"Retrying fetch for symbols: {cache_miss_symbols}, attempt {attempt + 1}")
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff

            return stock_details_map
        except Exception as e:
            raise RuntimeError(f"Error fetching stock details: {str(e)}")

    async def calculate_current_value_and_pnl(self, holdings: List[Holding]) -> tuple[List[HoldingMetrics], PortfolioSummary, Dict[str, ISMStockDetailsResponse]]:
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
                ), {}
            
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

            return holding_metrics_list, portfolio_summary, stock_details_map
        except Exception as e:
            raise RuntimeError(f"Error calculating current value and P&L: {str(e)}")
        
    async def analyze_portfolio_genai(self, holdings: List[Holding], user_id: int = None) -> str:
        """
        Analyze the portfolio using a generative AI model.
        """
        try:
            if not holdings:
                return "No holdings to analyze."
            
            if user_id:
                cache_key = f"portfolio_briefing_genai:{user_id}"
                cached_portfolio_briefing = await self.cache.get(cache_key)
                if cached_portfolio_briefing:
                    print(f"Cache hit for {cache_key}")
                    return cached_portfolio_briefing
                print(f"Cache miss for {cache_key}")

            holdings_metrics_list, portfolio_summary, _ = await self.calculate_current_value_and_pnl(holdings)

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

            pnl is profit and loss
            pct is percentage

            Return in markdown format.
            """

            briefing = self.openai_api.generate_text(prompt)

            if user_id:
                await self.cache.set(cache_key, briefing, expire_minutes=20)
                print(f"Cached briefing for {cache_key}")

            return briefing
        except Exception as e:
            raise RuntimeError(f"Error analyzing portfolio: {str(e)}")
        
    def _extract_beta(self, stock_details: ISMStockDetailsResponse) -> float:
            try:
                if not stock_details.key_metrics:
                    return 0.0

                for metric in stock_details.key_metrics.price_and_volume:
                    if metric.key == "beta" and metric.value:
                        return float(metric.value)
                
                return 0.0
            except (AttributeError, ValueError) as e:
                print(f"Error extracting beta: {str(e)}")
                return 0.0

    def _calculate_concentration_metrics(self, holdings_metrics: List[HoldingMetrics]) -> Tuple[float, float, float]:
        """
        Calculate concentration risk metrics.
        """
        sorted_holdings = sorted(holdings_metrics, key=lambda x: x.weightage, reverse=True)

        top_3_weightage = sum(h.weightage for h in sorted_holdings[:3])

        herfindahl = sum((h.weightage/100) ** 2 for h in holdings_metrics)

        sector_weights = defaultdict(float)
        for holding in holdings_metrics:
            sector_weights[holding.industry] += holding.weightage
        sector_concentration = max(sector_weights.values())

        return top_3_weightage, herfindahl, sector_concentration

    async def calculate_risk_metrics(self, holdings: List[Holding]) -> tuple[List[StockRiskMetrics], PortfolioRiskMetrics]:
        """
        Calculate risk metrics for the portfolio.
        """
        try:
            if not holdings:
                return [], PortfolioRiskMetrics(
                    beta=0.0,
                    total_pnl=0.0,
                    sector_allocations=[],
                    standard_deviation=0.0,
                    top_3_holdings_weightage=0.0,
                    herfindahl_index=0.0,
                    sector_concentration=0.0
                )

            holding_metrics_list, portfolio_summary, stock_details_map = await self.calculate_current_value_and_pnl(holdings)

            portfolio_beta = Decimal('0')
            stock_risk_metrics_list: List[StockRiskMetrics] = []
            for holding in holding_metrics_list:
                stock_details = stock_details_map.get(holding.symbol)
                if not stock_details:
                    continue

                beta = self._extract_beta(stock_details)
                weight = Decimal(str(holding.weightage)) / Decimal('100')
                portfolio_beta += (weight * Decimal(str(beta)))

                stock_risk_metrics = StockRiskMetrics(
                    symbol=holding.symbol,
                    beta=beta,
                    weightage=holding.weightage,
                    unrealized_pnl=holding.unrealized_pnl,
                    risk_meter=stock_details.risk_meter.category_name if stock_details.risk_meter and stock_details.risk_meter.category_name else "Unknown",
                    standard_deviation=stock_details.risk_meter.std_dev if stock_details.risk_meter and stock_details.risk_meter.std_dev else 0.0
                )
                stock_risk_metrics_list.append(stock_risk_metrics)

            top_3_weightage, herfindahl, sector_concentration = self._calculate_concentration_metrics(holding_metrics_list)

            portfolio_standard_deviation = 0.0

            portfolio_risk_metrics=PortfolioRiskMetrics(
                beta=float(portfolio_beta),
                total_pnl=portfolio_summary.total_pnl,
                sector_allocations=portfolio_summary.sector_allocations,
                standard_deviation=portfolio_standard_deviation,
                top_3_holdings_weightage=top_3_weightage,
                herfindahl_index=herfindahl,
                sector_concentration=sector_concentration
            )

            return stock_risk_metrics_list, portfolio_risk_metrics
        except Exception as e:
            raise RuntimeError(f"Error calculating risk metrics: {str(e)}")
        
    async def analyze_portfolio_risk_genai(self, holdings: List[Holding], user_id: int = None) -> str:
        """
        Analyze the portfolio risk using a generative AI model.
        """
        try:
            if not holdings:
                return "No holdings to analyze."
            
            if user_id:
                cache_key = f"portfolio_risk_analysis_genai:{user_id}"
                cached_portfolio_risk_analysis = await self.cache.get(cache_key)
                if cached_portfolio_risk_analysis:
                    print(f"Cache hit for {cache_key}")
                    return cached_portfolio_risk_analysis
                print(f"Cache miss for {cache_key}")

            stock_risk_metrics_list, portfolio_risk_metrics = await self.calculate_risk_metrics(holdings)

            prompt = f"""
            As a risk management advisor, analyze this portfolio's risk profile for a 23-year-old 
            software engineer in India with moderate-aggressive risk tolerance. Generate a risk report 
            (200 words) covering:

            1. Overall risk level assessment
            2. Specific risk concerns (concentration, volatility, sector)
            3. Age-appropriate recommendation
            4. One specific action to reduce risk if needed

            Stock risk metrics: {stock_risk_metrics_list}
            Portfolio risk metrics: {portfolio_risk_metrics}

            pnl is profit and loss
            pct is percentage

            Return in markdown format.
            """

            risk_analysis = self.openai_api.generate_text(prompt)

            if user_id:
                await self.cache.set(cache_key, risk_analysis, expire_minutes=20)
                print(f"Cached risk analysis for {cache_key}")

            return risk_analysis
        except Exception as e:
            raise RuntimeError(f"Error analyzing portfolio risk: {str(e)}")