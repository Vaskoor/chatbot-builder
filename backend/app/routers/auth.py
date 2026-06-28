from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    authenticate_user, create_access_token, create_refresh_token,
    get_password_hash, get_current_user, decode_token,
)
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserOut, RefreshRequest
router = APIRouter(prefix="/api/auth", tags=["auth"])
@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(400, "An account with this email already exists")
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    return TokenResponse(access_token=access, refresh_token=refresh, user=UserOut.model_validate(user))
@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(401, "Incorrect email or password")
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    return TokenResponse(access_token=access, refresh_token=refresh, user=UserOut.model_validate(user))
@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")
    user = db.query(User).filter(User.id == decoded.get("sub")).first()
    if not user:
        raise HTTPException(401, "User not found")
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    return TokenResponse(access_token=access, refresh_token=refresh, user=UserOut.model_validate(user))
@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
