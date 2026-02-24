"""
Routes — API Endpoints de NomadMatch
Incluye autenticación, preferencias de ciudades y búsqueda RAG.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import os
import shutil
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Importaciones locales (ajusta las rutas según tu estructura)
from .models.user import SessionLocal, User, UserCityPreference

router = APIRouter()

# ============================================
# Configuración JWT y Seguridad
# ============================================
SECRET_KEY = "your-secret-key-change-in-production"  # ¡Cámbialo en producción!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Dependencia para obtener sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Funciones auxiliares
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# ============================================
# Modelos Pydantic
# ============================================

# Modelos de autenticación
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    is_premium: bool

class UserResponse(BaseModel):
    id: int
    email: str
    is_premium: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Modelos de preferencias
class CityPreferenceRequest(BaseModel):
    city_name: str
    action: str  # "like" o "dislike"

class CityPreferenceResponse(BaseModel):
    message: str
    city_name: str
    action: str
    user_id: int

class PreferencesListResponse(BaseModel):
    user_id: int
    preferences: List[dict]
    likes: List[str]
    dislikes: List[str]

# Modelos para búsqueda
class QueryRequest(BaseModel):
    query: str
    num_results: int = 15
    preferences: Optional[dict] = None
    tier: str = "free"  # "free" or "premium"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

# ============================================
# Variables globales para ChromaManager
# ============================================
chroma_manager = None

def set_chroma_manager(cm):
    global chroma_manager
    chroma_manager = cm

# ============================================
# Funciones de ranking (ya las tenías)
# ============================================
def rank_cities(results: list, preferences: dict = None, tier: str = "free") -> list:
    # (Mismo código que ya tienes, no lo repito para ahorrar espacio)
    # Asegúrate de copiar la función completa desde tu archivo actual
    # ...

# ============================================
# ENDPOINTS DE AUTENTICACIÓN
# ============================================

@router.post("/api/v1/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed,
        is_premium=False,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_premium": new_user.is_premium}

@router.post("/api/v1/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "is_premium": user.is_premium}

@router.get("/api/v1/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/api/v1/auth/upgrade")
async def upgrade_to_premium(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.is_premium = True
    db.commit()
    return {"message": "User upgraded to premium", "is_premium": True}

# ============================================
# ENDPOINTS DE PREFERENCIAS DE CIUDADES
# ============================================

@router.post("/api/v1/preferences/city", response_model=CityPreferenceResponse)
async def set_city_preference(
    request: CityPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if request.action not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Action must be 'like' or 'dislike'")
    
    existing = db.query(UserCityPreference).filter(
        UserCityPreference.user_id == current_user.id,
        UserCityPreference.city_name == request.city_name
    ).first()
    
    if existing:
        existing.action = request.action
    else:
        pref = UserCityPreference(
            user_id=current_user.id,
            city_name=request.city_name,
            action=request.action
        )
        db.add(pref)
    
    db.commit()
    return CityPreferenceResponse(
        message=f"Preference saved for {request.city_name}",
        city_name=request.city_name,
        action=request.action,
        user_id=current_user.id
    )

@router.get("/api/v1/preferences/cities", response_model=PreferencesListResponse)
async def get_city_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    prefs = db.query(UserCityPreference).filter(
        UserCityPreference.user_id == current_user.id
    ).all()
    
    return {
        "user_id": current_user.id,
        "preferences": [
            {
                "city_name": p.city_name,
                "action": p.action,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in prefs
        ],
        "likes": [p.city_name for p in prefs if p.action == "like"],
        "dislikes": [p.city_name for p in prefs if p.action == "dislike"]
    }

@router.delete("/api/v1/preferences/city/{city_name}")
async def delete_city_preference(
    city_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pref = db.query(UserCityPreference).filter(
        UserCityPreference.user_id == current_user.id,
        UserCityPreference.city_name == city_name
    ).first()
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    db.delete(pref)
    db.commit()
    return {"message": f"Preference deleted for {city_name}"}

# ============================================
# ENDPOINTS DE BÚSQUEDA (los que ya tenías)
# ============================================

@router.get("/api/v1/health")
async def health_check():
    stats = chroma_manager.get_stats()
    return {
        "status": "healthy",
        "chroma_configured": True,
        **stats
    }

@router.get("/api/v1/collections")
async def list_collections():
    stats = chroma_manager.get_stats()
    return {
        "collections": [stats["collection"]],
        "total_docs": stats["total_docs"]
    }

@router.post("/api/v1/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files accepted")
    
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        count = chroma_manager.ingest_csv(temp_path)
        return {"status": "success", "chunks_processed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/api/v1/query")
async def query_cities(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = chroma_manager.search(request.query, n_results=request.num_results)
    
    if not results:
        return {"results": [], "query": request.query, "message": "No results found"}
    
    ranked = rank_cities(results, request.preferences, tier=request.tier)
    
    return {
        "results": ranked[:3],
        "total_searched": len(results),
        "query": request.query,
        "tier": request.tier
    }

@router.post("/api/v1/chat")
async def chat(request: ChatRequest):
    results = chroma_manager.search(request.message, n_results=5)
    ranked = rank_cities(results)
    
    if ranked:
        top = ranked[0]
        response = (
            f"Based on your preferences, I recommend {top['city']}, {top['country']} "
            f"({top['score_pct']}% match). It's in {top['region']} with a "
            f"{top['metadata'].get('budget', '')} budget. "
            f"Vibes: {top['metadata'].get('vibe_tags', '')}."
        )
    else:
        response = "I couldn't find matching cities. Try different preferences."
    
    return {"response": response, "session_id": request.session_id}
