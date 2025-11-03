from fastapi import FastAPI
from app.api.routes import holdings as holdings_router
from app.api.routes import auth as auth_router
from app.api.routes import portfolio as portfolio_router
from app.api.routes import investment_preferences as investment_preferences_router

app = FastAPI(title="The Alps", version="1.0.0")

app.include_router(auth_router.router)
app.include_router(holdings_router.router)
app.include_router(portfolio_router.router)
app.include_router(investment_preferences_router.router)
