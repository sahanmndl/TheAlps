from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.holding import HoldingCreate, HoldingOut, HoldingUpdate
from app.schemas.holding import Holding
from app.schemas.user import User

router = APIRouter(prefix="/api/v1/holdings", tags=["Holdings"])

@router.post("/", response_model=HoldingOut, status_code=status.HTTP_201_CREATED)
def add_holding(h_in: HoldingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_holding = db.query(Holding).filter(Holding.user_id == current_user.id, Holding.symbol == h_in.symbol).first()
    if existing_holding:
        raise HTTPException(status_code=400, detail="You already hold this stock. Please update the existing holding instead.")

    holding = Holding(user_id=current_user.id, **h_in.model_dump())

    db.add(holding)
    db.commit()
    db.refresh(holding)

    return holding

@router.get("/", response_model=List[HoldingOut])
def list_holdings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Holding).filter(Holding.user_id == current_user.id).all()

@router.put("/{holding_id}", response_model=HoldingOut)
def update_holding(holding_id: int, h_upd: HoldingUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    h: Holding = db.query(Holding).get(holding_id)
    if not h or h.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Holding not found")

    for field, value in h_upd.model_dump(exclude_unset=True).items():
        setattr(h, field, value)

    db.add(h)
    db.commit()
    db.refresh(h)

    return h

@router.delete("/{holding_id}", status_code=204)
def delete_holding(holding_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    h: Holding = db.query(Holding).get(holding_id)
    if not h or h.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Holding not found")

    db.delete(h)
    db.commit()
    
    return
