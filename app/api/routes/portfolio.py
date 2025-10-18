from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.portfolio_metrics import PortfolioMetricsResponse
from app.schemas.user import User
from app.schemas.holding import Holding
from app.services.openai_api import OpenAIAPI
from app.services.portfolio_metrics import PortfolioMetrics
from app.services.ism_api import ISMApi


router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])

@router.get("/metrics/current_value_and_pnl", response_model=PortfolioMetricsResponse)
async def get_portfolio_current_value_and_pnl(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)): 
    try:
        holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()
        
        ism_api = ISMApi()
        portfolio_metrics = PortfolioMetrics(ism_api)
        
        holding_metrics, portfolio_summary = await portfolio_metrics.calculate_current_value_and_pnl(holdings)

        return PortfolioMetricsResponse(
            holding_metrics=holding_metrics,
            portfolio_summary=portfolio_summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating portfolio current value and P&L: {str(e)}")
    
@router.get("/genai/analysis", response_model=dict)
async def analyze_portfolio_genai(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()

        ism_api = ISMApi()
        openai_api = OpenAIAPI()
        portfolio_metrics = PortfolioMetrics(ism_api, openai_api)

        analysis = await portfolio_metrics.analyze_portfolio_genai(holdings)

        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")