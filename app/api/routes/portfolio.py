import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.portfolio_metrics import PortfolioMetricsResponse, PortfolioRiskMetricsResponse
from app.schemas.user import User
from app.schemas.holding import Holding
from app.services.investment_advice import InvestmentAdvice
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
        
        holding_metrics, portfolio_summary, _ = await portfolio_metrics.calculate_current_value_and_pnl(holdings)

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

        analysis = await portfolio_metrics.analyze_portfolio_genai(holdings=holdings, user_id=current_user.id)

        if isinstance(analysis, str):
            analysis = json.loads(analysis)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio: {str(e)}")

@router.get("/metrics/risk", response_model=PortfolioRiskMetricsResponse)
async def get_portfolio_risk_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()

        ism_api = ISMApi()
        portfolio_metrics = PortfolioMetrics(ism_api)

        stock_risk_metrics_list, portfolio_risk_metrics = await portfolio_metrics.calculate_risk_metrics(holdings)

        return PortfolioRiskMetricsResponse(
            stocks_risk_metrics=stock_risk_metrics_list,
            portfolio_risk_metrics=portfolio_risk_metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio risk metrics: {str(e)}")
    
@router.get("/genai/risk-analysis", response_model=dict)
async def analyze_portfolio_risk_genai(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()

        ism_api = ISMApi()
        openai_api = OpenAIAPI()
        portfolio_metrics = PortfolioMetrics(ism_api, openai_api)

        analysis = await portfolio_metrics.analyze_portfolio_risk_genai(holdings=holdings, user_id=current_user.id)

        if isinstance(analysis, str):
            analysis = json.loads(analysis)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio risk: {str(e)}")

@router.get("/genai/comprehensive-analysis", response_model=dict)
async def analyze_portfolio_comprehensive_advisory_genai(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()

        ism_api = ISMApi()
        openai_api = OpenAIAPI()
        investment_advice = InvestmentAdvice(db, ism_api, openai_api)

        analysis = await investment_advice.generate_comprehensive_advisory_genai(holdings=holdings, user_id=current_user.id)

        if isinstance(analysis, str):
            analysis = json.loads(analysis)

        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing portfolio comprehensive advisory: {str(e)}")