"""
Routes — API Endpoints de NomadMatch
5 endpoints REST para el sistema RAG.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil

router = APIRouter()

# Will be set by main.py
chroma_manager = None


def set_chroma_manager(cm):
    global chroma_manager
    chroma_manager = cm


class QueryRequest(BaseModel):
    query: str
    num_results: int = 15
    preferences: Optional[dict] = None
    tier: str = "free"  # "free" or "premium"


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


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
        
        # Climate/region boost
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
            "metadata": meta
        }
        
        # Add premium visa/tax data if tier is premium
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


# ────────────────────────────────────────────────
# ENDPOINT 1: Health Check
# ────────────────────────────────────────────────
@router.get("/api/v1/health")
async def health_check():
    stats = chroma_manager.get_stats()
    return {
        "status": "healthy",
        "chroma_configured": True,
        **stats
    }


# ────────────────────────────────────────────────
# ENDPOINT 2: List Collections
# ────────────────────────────────────────────────
@router.get("/api/v1/collections")
async def list_collections():
    stats = chroma_manager.get_stats()
    return {
        "collections": [stats["collection"]],
        "total_docs": stats["total_docs"]
    }


# ────────────────────────────────────────────────
# ENDPOINT 3: Upload & Ingest CSV
# ────────────────────────────────────────────────
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


# ────────────────────────────────────────────────
# ENDPOINT 4: Query (MAIN) — Semantic Search + Ranking
# ────────────────────────────────────────────────
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


# ────────────────────────────────────────────────
# ENDPOINT 5: Chat (Experimental)
# ────────────────────────────────────────────────
@router.post("/api/v1/chat")
async def chat(request: ChatRequest):
    # Simple: search and return natural language response
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
