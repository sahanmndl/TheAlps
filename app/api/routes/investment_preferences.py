from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.investment_preference import InvestmentPreferenceCreate, InvestmentPreferenceOut, InvestmentPreferenceUpdate
from app.schemas.user import User
from app.services.investment_preferences import InvestmentPreferences

router = APIRouter(prefix="/api/v1/investment-preferences", tags=["Investment Preferences"])

@router.post("/", response_model=InvestmentPreferenceOut, status_code=status.HTTP_201_CREATED)
async def create_investment_preference(preference: InvestmentPreferenceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    preferences_service = InvestmentPreferences(db)
    return await preferences_service.add_preference(current_user.id, preference)

@router.get("/", response_model=InvestmentPreferenceOut, status_code=status.HTTP_200_OK)
async def get_investment_preference(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    preferences_service = InvestmentPreferences(db)
    return await preferences_service.get_preference(current_user.id)

@router.put("/", response_model=InvestmentPreferenceOut, status_code=status.HTTP_200_OK)
async def update_investment_preference(preference: InvestmentPreferenceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    preferences_service = InvestmentPreferences(db)
    return await preferences_service.update_preference(current_user.id, preference)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment_preference(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    preferences_service = InvestmentPreferences(db)
    await preferences_service.delete_preference(current_user.id)
    return None