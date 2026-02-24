"""
Auth — Autenticación JWT para NomadMatch (Prototipo 4)
Registro, login, perfil y upgrade a premium.
"""
import os
import json
import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta

from ..models.user import User
from .deps import get_db, get_current_user, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana


# ── Pydantic Models ──────────────────────────────
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    is_premium: bool

class PreferencesUpdate(BaseModel):
    preferences: dict

class UserOut(BaseModel):
    email: str
    is_premium: bool
    preferences: dict


# ── Helpers ───────────────────────────────────────
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── Endpoints ─────────────────────────────────────

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed, is_premium=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.email, "premium": new_user.is_premium})
    return {"access_token": token, "token_type": "bearer", "is_premium": new_user.is_premium}


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    token = create_access_token({"sub": db_user.email, "premium": db_user.is_premium})
    return {"access_token": token, "token_type": "bearer", "is_premium": db_user.is_premium}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    prefs = current_user.preferences if current_user.preferences else "{}"
    return {
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "preferences": json.loads(prefs),
    }


@router.put("/preferences")
async def update_preferences(
    prefs: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.preferences = json.dumps(prefs.preferences)
    db.commit()
    return {"message": "Preferences updated"}


@router.post("/upgrade")
async def upgrade_to_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.is_premium = True
    db.commit()
    token = create_access_token({"sub": current_user.email, "premium": True})
    return {"access_token": token, "token_type": "bearer", "is_premium": True}
