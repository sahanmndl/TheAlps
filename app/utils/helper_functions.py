from typing import List
from app.cache.redis import RedisService
from app.models.ism_api.news import ISMNewsArticle
from app.models.ism_api.stock import ISMStockDetailsResponse, ISMTrendingStocksResponse, RecentNews
from app.services.ism_api import ISMApi


class HelperFunctions:
    def __init__(self, ism_api: ISMApi):
        self.ism_api = ism_api
        self.cache = RedisService()

    async def get_cached_data(self, key: str):
        cached_data = await self.cache.get(key)
        if cached_data:
            print(f"Cache hit for {key}")
            return cached_data
        print(f"Cache miss for {key}")

    async def set_cached_data(self, key: str, data, expire_minutes: int = 60):
        await self.cache.set(key, data, expire_minutes=expire_minutes)
        print(f"Cached data for {key}")

    async def cache_news_articles(self, news_articles: List[ISMNewsArticle]):
        news_cache_key = "news_articles"
        cached_news = await self.cache.get(news_cache_key)
        if not cached_news and news_articles:
            await self.cache.set(news_cache_key, [article.model_dump(by_alias=True) for article in news_articles], expire_minutes=180)

    async def get_cached_news_articles(self) -> List[ISMNewsArticle]:
        news_cache_key = "news_articles"
        cached_news = await self.cache.get(news_cache_key)
        if cached_news:
            return [ISMNewsArticle(**article) for article in cached_news]
        else:
            news_articles = await self.ism_api.get_news()
            await self.cache.set(news_cache_key, [article.model_dump(by_alias=True) for article in news_articles], expire_minutes=180)
            return news_articles

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

    async def get_cached_trending_stocks(self) -> ISMTrendingStocksResponse:
        trending_stocks_cache_key = "trending_stocks"
        cached_trending_stocks = await self.cache.get(trending_stocks_cache_key)
        if cached_trending_stocks:
            return ISMTrendingStocksResponse(**cached_trending_stocks)
        else:
            trending_stocks = await self.ism_api.get_trending_stocks()
            await self.set_cached_data(key=trending_stocks_cache_key, data=trending_stocks.model_dump(by_alias=True), expire_minutes=120)
            return trending_stocks