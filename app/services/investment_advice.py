import asyncio
import json
from typing import List
from sqlalchemy.orm import Session

from app.schemas.holding import Holding
from app.services.investment_preferences import InvestmentPreferences
from app.services.ism_api import ISMApi
from app.services.openai_api import OpenAIAPI
from app.services.portfolio_metrics import PortfolioMetrics
from app.utils.helper_functions import HelperFunctions


class InvestmentAdvice:
    def __init__(self, db: Session, ism_api: ISMApi, openai_api: OpenAIAPI = None):
        self.db = db
        self.ism_api = ism_api
        self.openai_api = openai_api
        self.portfolio_metrics = PortfolioMetrics(ism_api, openai_api)
        self.helper_functions = HelperFunctions(ism_api)
        self.investment_preferences = InvestmentPreferences(db)

    async def _fetch_news_for_holding(self, holding: Holding) -> tuple[str, List[dict]]:
        stock_news = await self.helper_functions.get_cached_stock_specific_news(symbol=holding.symbol, isin_number=holding.isin_number)
        if stock_news:
            return holding.symbol, [
                {
                    "headline": news.headline,
                    "intro": news.intro,
                    "date": news.date
                }
                for news in stock_news
            ]
        return holding.symbol, []

    async def generate_comprehensive_advisory_genai(self, holdings: List[Holding], user_id: int) -> str:
        """
        Generate comprehensive portfolio advisory using GenAI
        """
        try:
            if not holdings:
                return "No holdings to analyze."
            
            if user_id:
                cache_key = f"comprehensive_advisory_genai:{user_id}"
                cached_advisory = await self.helper_functions.get_cached_data(key=cache_key)
                if cached_advisory:
                    return cached_advisory
                
            holdings_metrics_list, portfolio_summary, _ = await self.portfolio_metrics.calculate_current_value_and_pnl(holdings)
            
            market_news = await self.helper_functions.get_cached_news_articles()
            market_news_summaries = []
            for article in market_news:
                title = article.title
                summary = article.summary
                pub_date = article.pub_date.strftime("%Y-%m-%d")
                market_news_summaries.append({
                    "title": title,
                    "summary": summary,
                    "pub_date": pub_date
                })

            news_tasks = [self._fetch_news_for_holding(holding) for holding in holdings]
            news_results = await asyncio.gather(*news_tasks)
            stock_specific_news_summaries = dict(news_results)

            trending_stocks = await self.helper_functions.get_cached_trending_stocks()
            top_gainers, top_losers = [], []
            for stock in trending_stocks.trending_stocks.top_gainers:
                top_gainers.append({
                    "company_name": stock.company_name,
                    "price": stock.price,
                    "percent_change": stock.percent_change,
                    "date": stock.date
                })
            for stock in trending_stocks.trending_stocks.top_losers:
                top_losers.append({
                    "company_name": stock.company_name,
                    "price": stock.price,
                    "percent_change": stock.percent_change,
                    "date": stock.date
                })

            user_investment_preference = ""
            investment_prefs = await self.investment_preferences.get_preference(user_id)
            if investment_prefs:
                user_investment_preference = f"""
                Risk Tolerance: {investment_prefs.risk_tolerance.value}
                Investment Horizon: {investment_prefs.investment_horizon.value}
                Target Annual Return: {investment_prefs.target_annual_return.value}
                Monthly Investment Range: {investment_prefs.monthly_investment_range.value}
                Preferred Sectors: {[sector.value for sector in investment_prefs.preferred_sectors]}
                Avoid Sectors: {[sector.value for sector in investment_prefs.avoid_sectors]}
                Max Position Size: {investment_prefs.max_position_size}%
                Dividend Focus: {'Yes' if investment_prefs.dividend_focus else 'No'}
                ESG Focus: {'Yes' if investment_prefs.esg_focus else 'No'}
                """
            else:
                user_investment_preference = "No specific investment preferences set."


            prompt = f"""
            You are an expert portfolio analyst specializing in Indian equity markets.

            PORTFOLIO HOLDINGS:
            {holdings_metrics_list}

            PORTFOLIO SUMMARY:
            {portfolio_summary}

            LATEST MARKET NEWS:
            {market_news_summaries}

            LATEST STOCK-SPECIFIC NEWS:
            {stock_specific_news_summaries}

            TRENDING STOCKS:
            Top Gainers:
            {top_gainers}
            Top Losers:
            {top_losers}

            USER INVESTMENT PREFERENCES:
            {user_investment_preference}

            Using the above data, provide a detailed investment advisory with the following sections:

            1. PORTFOLIO HEALTH CHECK
                - Summarize overall sentiment and portfolio health.
                - Identify any red flags, risks, or hidden opportunities.

            2. SPECIFIC HOLDINGS RECOMMENDATIONS
                - For each holding: provide a clear decision: HOLD / SELL / BUY MORE.
                - Include recommended price targets, quantities to buy or sell, and timing (this week, this month).
                - Suggest appropriate stop-loss levels.

            3. TOP 3 BUY OPPORTUNITIES FROM THE MARKET
                - Identify the best stocks to buy based on market news and trends.
                - Provide entry price ranges, price targets, stop-loss levels, and suggested capital allocation.
                - Explain why these stocks are attractive investments now.

            4. PORTFOLIO REBALANCING ADVICE
                - Advise on sector-level exposure adjustments based on market trends and risk management.
                - Provide recommended allocation changes with target percentages.

            5. ACTION ITEMS
                - Prioritize action items into:
                    a. Urgent (this week)
                    b. Important (next 2 weeks)
                    c. Monitor (longer term)
                - Be specific about quantities, price levels, and timing.
            
            Tailor all recommendations assuming the user is a retail investor with the given investment preferences.

            If user has medium to long term horizon, recommend SELL decisions only for fundamentally weak stocks or overvalued holdings. Only if it's absolutely necessary.
            Provide recommendations only if they are relevant to the current portfolio and market context. If no action is needed, clearly state that.

            For stock buy recommendations, focus on fundamentally strong companies with good growth prospects in the Indian markets. 
            Take into account recent news, market trends, trending stocks, investment preferences etc., but also look beyond them to identify hidden gems.
            Look for multibagger potential stocks that can deliver substantial returns over the investment horizon.
            
            Avoid vague phrases; be specific, data-driven, and actionable.
            Ensure all numerical values are numbers, not strings.
            For key-value pairs, don't use under scores in the values, use spaces instead.

            Provide the response in the following JSON format. Don't include any explanations outside the JSON structure. ONLY RETURN THE JSON.
            {{
                "portfolio_health_check": {{
                    "overall_sentiment": "<sentiment>",
                    "portfolio_health": "<health status>",
                    "red_flags": ["<flag1>", "<flag2>"],
                    "opportunities": ["<opportunity1>", "<opportunity2>"]
                }},
                "holdings_recommendations": [
                    {{
                        "symbol": "<stock symbol>",
                        "decision": "HOLD|SELL|BUY_MORE",
                        "price_target": 0.0,
                        "stop_loss": 0.0,
                        "quantity_change": 0,
                        "timing": "<timing>",
                        "rationale": "<explanation>"
                    }}
                ],
                "buy_opportunities": [
                    {{
                        "symbol": "<stock symbol>",
                        "company_name": "<company name>",
                        "entry_price_range": {{
                            "min": 0.0,
                            "max": 0.0
                        }},
                        "price_target": 0.0,
                        "stop_loss": 0.0,
                        "capital_allocation_percentage": 0.0,
                        "rationale": "<explanation>"
                    }}
                ],
                "portfolio_rebalancing": {{
                    "sector_adjustments": [
                        {{
                            "sector": "<sector name>",
                            "current_percentage": 0.0,
                            "target_percentage": 0.0,
                            "action": "<action required>"
                        }}
                    ],
                    "recommendation_rationale": "<explanation>"
                }},
                "action_items": {{
                    "urgent": [
                        {{
                            "action": "<action>",
                            "symbol": "<symbol>",
                            "quantity": 0,
                            "price_level": 0.0,
                            "deadline": "<deadline>"
                        }}
                    ],
                    "important": [
                        {{
                            "action": "<action>",
                            "symbol": "<symbol>",
                            "quantity": 0,
                            "price_level": 0.0,
                            "deadline": "<deadline>"
                        }}
                    ],
                    "monitor": [
                        {{
                            "action": "<action>",
                            "symbol": "<symbol>",
                            "condition": "<condition>",
                            "threshold": 0.0
                        }}
                    ]
                }}
            }}
            """

            print(f"Generating comprehensive advisory for user_id={user_id}...")
            advisory_response = self.openai_api.generate_text(prompt)
            advisory_json = json.loads(advisory_response)
            advisory_response = json.dumps(advisory_json, indent=4)
            print(f"Generated comprehensive advisory for user_id={user_id}")

            if user_id:
                await self.helper_functions.set_cached_data(key=cache_key, data=advisory_response, expire_minutes=60)

            return advisory_response
        except Exception as e:
            raise RuntimeError(f"Error generating comprehensive advisory: {str(e)}")
