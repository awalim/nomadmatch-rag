import bcrypt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
import os
import json

from ..models.user import SessionLocal, User

router = APIRouter(prefix="/auth", tags=["auth"])

# Configuración JWT
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Modelos Pydantic
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

# Dependencia para base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funciones auxiliares con bcrypt
def get_password_hash(password: str) -> str:
    """Genera hash de contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica la contraseña con bcrypt"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Endpoints
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Crear nuevo usuario (free por defecto)
    hashed = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed, is_premium=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Generar token
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
    return {
        "email": current_user.email,
        "is_premium": current_user.is_premium,
        "preferences": json.loads(current_user.preferences)
    }

@router.put("/preferences")
async def update_preferences(
    prefs: PreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.preferences = json.dumps(prefs.preferences)
    db.commit()
    return {"message": "Preferences updated"}


@router.post("/upgrade")
async def upgrade_to_premium(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upgrade user to premium (demo - no payment required)"""
    current_user.is_premium = True
    db.commit()
    # Generate new token with premium flag
    token = create_access_token({"sub": current_user.email, "premium": True})
    return {"access_token": token, "token_type": "bearer", "is_premium": True}
