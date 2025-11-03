from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from app.schemas.investment_preference import InvestmentPreference
from app.models.investment_preference import InvestmentPreferenceCreate, InvestmentPreferenceUpdate, InvestmentPreferenceOut

class InvestmentPreferences:
    def __init__(self, db: Session):
        self.db = db

    async def add_preference(self, user_id: int, preference: InvestmentPreferenceCreate) -> InvestmentPreferenceOut:
        try:
            existing = self.db.query(InvestmentPreference).filter(InvestmentPreference.user_id == user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Investment preferences already exist for this user")

            db_preference = InvestmentPreference(
                user_id=user_id,
                **preference.model_dump()
            )
            self.db.add(db_preference)
            self.db.commit()
            self.db.refresh(db_preference)
            return db_preference
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding investment preferences: {str(e)}")

    async def get_preference(self, user_id: int) -> Optional[InvestmentPreferenceOut]:
        try:
            preference = self.db.query(InvestmentPreference).filter(
                InvestmentPreference.user_id == user_id
            ).first()
            if not preference:
                raise HTTPException(status_code=404, detail="Investment preferences not found")
            return preference
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving investment preferences: {str(e)}")

    async def update_preference(self, user_id: int, preference: InvestmentPreferenceUpdate) -> InvestmentPreferenceOut:
        try:
            db_preference = self.db.query(InvestmentPreference).filter(
                InvestmentPreference.user_id == user_id
            ).first()
            if not db_preference:
                raise HTTPException(status_code=404, detail="Investment preferences not found")

            for field, value in preference.model_dump(exclude_unset=True).items():
                setattr(db_preference, field, value)

            self.db.add(db_preference)
            self.db.commit()
            self.db.refresh(db_preference)
            return db_preference
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating investment preferences: {str(e)}")

    async def delete_preference(self, user_id: int) -> None:
        try:
            preference = self.db.query(InvestmentPreference).filter(
                InvestmentPreference.user_id == user_id
            ).first()
            if not preference:
                raise HTTPException(status_code=404, detail="Investment preferences not found")

            self.db.delete(preference)
            self.db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting investment preferences: {str(e)}")