from app.core.config import settings
from app.models.ism_api.news import ISMNewsArticle
from app.models.ism_api.stock import ISMStockDetailsResponse, ISMTrendingStocksResponse
import httpx

class ISMApi:
    INDIAN_STOCK_MARKET_API_BASE_URL = "https://stock.indianapi.in"

    @staticmethod
    async def get_stock_details(name: str) -> ISMStockDetailsResponse:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{ISMApi.INDIAN_STOCK_MARKET_API_BASE_URL}/stock",
                    headers={
                        "x-api-key": settings.INDIAN_STOCK_MARKET_API_KEY
                    },
                    params={
                        "name": name
                    }
                )
                response.raise_for_status()
                return ISMStockDetailsResponse(**response.json())
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching stock details: {str(e)}")
        
    @staticmethod
    async def get_news() -> list[ISMNewsArticle]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{ISMApi.INDIAN_STOCK_MARKET_API_BASE_URL}/news",
                    headers={
                        "x-api-key": settings.INDIAN_STOCK_MARKET_API_KEY
                    },
                )
                response.raise_for_status()
                return [ISMNewsArticle(**item) for item in response.json()]
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching news details: {str(e)}")

    @staticmethod
    async def get_trending_stocks() -> ISMTrendingStocksResponse:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{ISMApi.INDIAN_STOCK_MARKET_API_BASE_URL}/trending",
                    headers={
                        "x-api-key": settings.INDIAN_STOCK_MARKET_API_KEY
                    },
                )
                response.raise_for_status()
                return ISMTrendingStocksResponse(**response.json())
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching trending stocks: {str(e)}")
        