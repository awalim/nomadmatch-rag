"""
Routes — API Endpoints de NomadMatch (Prototipo 4)
Endpoints REST para búsqueda RAG, upload, health, chat y preferencias de ciudades.
Auth se maneja en auth.py.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import os
import shutil

from ..models.user import User, UserCityPreference
from .deps import get_db, get_current_user

router = APIRouter()

# ── ChromaManager global (set by main.py) ─────────
chroma_manager = None


def set_chroma_manager(cm):
    global chroma_manager
    chroma_manager = cm


# ── Pydantic Models ───────────────────────────────
class QueryRequest(BaseModel):
    query: str
    num_results: int = 15
    preferences: Optional[dict] = None
    tier: str = "free"


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class CityPreferenceRequest(BaseModel):
    city_name: str
    action: str  # "like" o "dislike"


# ── Ranking / Boost Scoring ───────────────────────
def rank_cities(results: list, preferences: dict = None, tier: str = "free") -> list:
    """Apply boost scoring based on metadata matches."""
    if not preferences:
        preferences = {}

    ranked = []
    for r in results:
        meta = r.get("metadata", {})
        score = r.get("base_score", 0.5)
        boosts_applied = []

        # Visa boost
        if preferences.get("visa") == "Yes" and meta.get("visa") == "Yes":
            score += 0.30
            boosts_applied.append("visa:+0.30")

        # Internet boost
        if meta.get("internet") == "Excellent":
            score += 0.15
            boosts_applied.append("internet:+0.15")

        # Budget boost
        pref_budget = preferences.get("budget", "")
        city_budget = meta.get("budget", "")
        if pref_budget == "Very Affordable" and city_budget == "Very Affordable":
            score += 0.30
            boosts_applied.append("budget_match:+0.30")
        elif pref_budget == "Affordable" and city_budget in ("Affordable", "Very Affordable"):
            score += 0.20
            boosts_applied.append("budget_match:+0.20")
        elif pref_budget == "Moderate" and city_budget in ("Moderate", "Affordable"):
            score += 0.10
            boosts_applied.append("budget_match:+0.10")

        # Climate boost
        pref_climate = preferences.get("climate", "")
        if pref_climate == "Warm" and meta.get("summer_temp") in ("Warm", "Hot"):
            score += 0.15
            boosts_applied.append("climate:+0.15")
        elif pref_climate == "Mild" and meta.get("summer_temp") == "Mild":
            score += 0.15
            boosts_applied.append("climate:+0.15")

        # Safety boost
        if meta.get("safety") == "Excellent":
            score += 0.05
            boosts_applied.append("safety:+0.05")

        # Family boost
        if preferences.get("family") == "Yes" and meta.get("family") in ("Good", "Excellent"):
            score += 0.10
            boosts_applied.append("family:+0.10")

        # Nightlife boost
        if preferences.get("nightlife") == "Yes" and meta.get("nightlife") in ("Good", "Excellent"):
            score += 0.10
            boosts_applied.append("nightlife:+0.10")

        # Vibe tag matching
        pref_vibes = preferences.get("vibes", [])
        if isinstance(pref_vibes, str):
            pref_vibes = [v.strip() for v in pref_vibes.split(",")]
        city_vibes = meta.get("vibe_tags", "").lower()
        vibe_matches = sum(1 for v in pref_vibes if v.lower() in city_vibes)
        if vibe_matches > 0:
            vibe_boost = min(vibe_matches * 0.05, 0.15)
            score += vibe_boost
            boosts_applied.append(f"vibes({vibe_matches}):+{vibe_boost:.2f}")

        final_score = min(score, 1.0)

        entry = {
            "city": meta.get("city", "Unknown"),
            "country": meta.get("country", ""),
            "region": meta.get("region", ""),
            "score": round(final_score, 4),
            "score_pct": round(final_score * 100, 1),
            "base_score": r.get("base_score", 0),
            "boosts": boosts_applied,
            "metadata": meta,
        }

        if tier == "premium":
            entry["premium_data"] = {
                "visa_available": meta.get("visa", "No"),
                "visa_type": meta.get("visa_type", "N/A"),
                "visa_duration": meta.get("visa_duration", "N/A"),
                "visa_income_req_eur": meta.get("visa_income_req", 0),
                "visa_score": meta.get("visa_score", "N/A"),
                "schengen": meta.get("schengen", "N/A"),
            }

        ranked.append(entry)

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


# ══════════════════════════════════════════════════
# ENDPOINTS RAG (health, collections, upload, query, chat)
# ══════════════════════════════════════════════════

@router.get("/api/v1/health")
async def health_check():
    stats = chroma_manager.get_stats()
    return {
        "status": "healthy",
        "chroma_configured": chroma_manager.initialized,
        **stats,
    }


@router.get("/api/v1/collections")
async def list_collections():
    stats = chroma_manager.get_stats()
    return {
        "collections": [stats["collection"]],
        "total_docs": stats.get("total_docs", stats.get("total_documents", 0)),
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
        return {"status": "success", "chunks_processed": count, "filename": file.filename}
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
        "tier": request.tier,
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


# ══════════════════════════════════════════════════
# ENDPOINTS PREFERENCIAS DE CIUDADES (Match / Skip)
# ══════════════════════════════════════════════════

@router.post("/api/v1/preferences/city")
async def set_city_preference(
    request: CityPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Guardar o actualizar preferencia (like/dislike) para una ciudad."""
    if request.action not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="Action must be 'like' or 'dislike'")

    existing = db.query(UserCityPreference).filter(
        UserCityPreference.user_id == current_user.id,
        UserCityPreference.city_name == request.city_name,
    ).first()

    if existing:
        existing.action = request.action
    else:
        pref = UserCityPreference(
            user_id=current_user.id,
            city_name=request.city_name,
            action=request.action,
        )
        db.add(pref)

    db.commit()
    return {
        "message": f"Preference saved for {request.city_name}",
        "city_name": request.city_name,
        "action": request.action,
        "user_id": current_user.id,
    }


@router.get("/api/v1/preferences/cities")
async def get_city_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtener todas las preferencias del usuario."""
    prefs = db.query(UserCityPreference).filter(
        UserCityPreference.user_id == current_user.id
    ).all()

    return {
        "user_id": current_user.id,
        "preferences": [
            {
                "city_name": p.city_name,
                "action": p.action,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in prefs
        ],
        "likes": [p.city_name for p in prefs if p.action == "like"],
        "dislikes": [p.city_name for p in prefs if p.action == "dislike"],
    }


@router.delete("/api/v1/preferences/city/{city_name}")
async def delete_city_preference(
    city_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Eliminar preferencia de una ciudad."""
    pref = db.query(UserCityPreference).filter(
        UserCityPreference.user_id == current_user.id,
        UserCityPreference.city_name == city_name,
    ).first()

    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")

    db.delete(pref)
    db.commit()
    return {"message": f"Preference deleted for {city_name}"}


# ══════════════════════════════════════════════════
# ENDPOINT PREMIUM ADVICE (Visa + Tax data)
# ══════════════════════════════════════════════════

class PremiumAdviceRequest(BaseModel):
    query: str = "información de visados e impuestos"
    num_results: int = 10


@router.post("/api/v1/premium/advice")
async def premium_advice(
    request: PremiumAdviceRequest,
    current_user: User = Depends(get_current_user),
):
    """Devuelve datos premium (visa/tax) para usuarios premium."""
    if not current_user.is_premium:
        raise HTTPException(status_code=403, detail="Premium subscription required")

    # Buscar documentos premium en ChromaDB
    results = chroma_manager.search(
        request.query,
        n_results=request.num_results,
        tier="premium",
    )

    # Si no hay resultados premium, buscar todos y filtrar
    if not results:
        all_results = chroma_manager.search(request.query, n_results=50)
        results = [
            r for r in all_results
            if r.get("metadata", {}).get("tier") == "premium"
               or r.get("metadata", {}).get("data_type") in ("Visa", "Tax")
        ][:request.num_results]

    # Deduplicar por ciudad
    seen = set()
    unique = []
    for r in results:
        city = r.get("metadata", {}).get("city", "")
        if city and city not in seen:
            seen.add(city)
            unique.append(r)

    return {
        "results": unique,
        "query": request.query,
        "count": len(unique),
        "advice": None,  # placeholder for LLM-generated advice
    }
