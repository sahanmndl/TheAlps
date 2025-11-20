import datetime
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from app.models.auth import AuthResponse, LoginRequest, UserCreate, TokenWithRefresh
from app.db.session import get_db
from app.schemas.user import User
from app.schemas.refresh_token import RefreshToken
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.core.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=user_in.email, hashed_password=get_password_hash(user_in.password), name=user_in.name, is_active=True)

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(subject=str(user.id))
    refresh_token_plain = create_refresh_token()
    refresh_token_hash = hash_token(refresh_token_plain)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    rt = RefreshToken(user_id=user.id, token_hash=refresh_token_hash, expires_at=expires_at)
    db.add(rt)
    db.commit()

    response.set_cookie(
        key="refreshToken",
        value=refresh_token_plain,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {
        "user": user,
        "access_token": access_token
    }

@router.post("/login", response_model=AuthResponse)
def login(user_in: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=str(user.id))
    refresh_token_plain = create_refresh_token()
    refresh_token_hash = hash_token(refresh_token_plain)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    rt = RefreshToken(user_id=user.id, token_hash=refresh_token_hash, expires_at=expires_at)
    db.add(rt)
    db.commit()

    response.set_cookie(
        key="refreshToken",
        value=refresh_token_plain,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # Convert days to seconds
    )

    return {
        "user": user,
        "access_token": access_token
    }

@router.post("/refresh", response_model=TokenWithRefresh)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refreshToken")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    rt_hash = hash_token(refresh_token)
    token_row = db.query(RefreshToken).filter(
        RefreshToken.token_hash == rt_hash, 
        RefreshToken.revoked == False
    ).first()

    if not token_row or token_row.expires_at < datetime.datetime.now(datetime.timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).get(token_row.user_id)
    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token
    }

@router.post("/logout", status_code=204)
def logout():
    return
