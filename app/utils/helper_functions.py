from typing import List
from app.cache.redis import RedisService
from app.models.ism_api.stock import ISMStockDetailsResponse, RecentNews
from app.services.ism_api import ISMApi


class HelperFunctions:
    def __init__(self, ism_api: ISMApi):
        self.ism_api = ism_api
        self.cache = RedisService()

    async def cache_stock_specific_news(self, recent_news: List[RecentNews], symbol: str):
        stock_news_cache_key = f"stock_news:{symbol}"
        cached_stock_news = await self.cache.get(stock_news_cache_key)
        if not cached_stock_news and recent_news:
            await self.cache.set(stock_news_cache_key, [news.model_dump(by_alias=True) for news in recent_news], expire_minutes=60)

    async def get_cached_stock_specific_news(self, symbol: str) -> List[RecentNews]:
        stock_news_cache_key = f"stock_news:{symbol}"
        cached_recent_news = await self.cache.get(stock_news_cache_key)
        if cached_recent_news:
            return [RecentNews(**news) for news in cached_recent_news]

        stock_cache_key = f"stock_details:{symbol}"
        cached_stock_details = await self.cache.get(stock_cache_key)
        if cached_stock_details:
            stock_details = ISMStockDetailsResponse(**cached_stock_details)
            stock_recent_news = stock_details.recent_news
            if stock_recent_news:
                await self.cache.set(stock_news_cache_key, [news.model_dump(by_alias=True) for news in stock_recent_news], expire_minutes=60)
                return stock_recent_news
            else:
                return []
        else:
            stock_details = await self.ism_api.get_stock_details(symbol)
            await self.cache.set(stock_cache_key, stock_details.model_dump(by_alias=True), expire_minutes=5)
            stock_recent_news = stock_details.recent_news
            if stock_recent_news:
                await self.cache.set(stock_news_cache_key, [news.model_dump(by_alias=True) for news in stock_recent_news], expire_minutes=60)
                return stock_recent_news
            else:
                return []