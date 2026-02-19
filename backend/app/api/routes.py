from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import pandas as pd
from io import StringIO
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..utils.chroma_utils import ChromaManager
from ..utils.llm_utils import generate_premium_advice
from ..models.schemas import (
    ChatRequest, ChatResponse,
    DocumentUploadResponse, HealthResponse,
    QueryRequest, QueryResponse
)
from ..api.auth import get_current_user
from ..models.user import User


router = APIRouter()
chroma_manager = ChromaManager()

# Health check
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status"""
    try:
        stats = chroma_manager.get_stats()
        return HealthResponse(
            status="healthy",
            langflow_connected=False,
            chroma_configured=chroma_manager.initialized,
            stats=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Upload CSV
@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a CSV document to be processed"""
    try:
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode('utf-8')))
        local_chroma = ChromaManager()
        chunks_processed = local_chroma.ingest_dataframe(df, file.filename)
        
        return DocumentUploadResponse(
            message="✅ Document uploaded successfully",
            filename=file.filename,
            success=True,
            chunks_processed=chunks_processed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        # Filter for General tier only (free users)
        # if 'data_type' in df.columns:
        #    df = df[df['data_type'] == 'General']
        
        chunks_processed = chroma_manager.ingest_dataframe(df, file.filename)
        
        # Chat endpoint
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to find cities"""
    try:
        results = chroma_manager.similarity_search(request.message, k=10)
        
        cities = []
        for r in results[:3]:
            metadata = r.get("metadata", {})
            cities.append({
                "city": metadata.get("city", "Unknown"),
                "country": metadata.get("country", ""),
                "budget": metadata.get("budget", "Moderate"),
                "internet": metadata.get("internet", "Good"),
                "visa": metadata.get("visa", "No"),
                "score": round(r.get("similarity_score", 0) * 100, 1)
            })
        
        return ChatResponse(
            response=f"Encontré {len(cities)} ciudades para ti",
            session_id=request.session_id,
            cities=cities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Query endpoint
@router.post("/query", response_model=QueryResponse)
async def query_vector_db(request: QueryRequest):
    """Direct query to ChromaDB"""
    try:
        local_chroma = ChromaManager()  # instancia fresca
        results = local_chroma.similarity_search(
            request.query, 
            k=request.num_results or 10
        )
        return QueryResponse(
            results=results,
            query=request.query,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# Collections endpoint
@router.get("/collections")
async def get_collections():
    """Get ChromaDB collections"""
    try:
        collections = chroma_manager.list_collections()
        stats = chroma_manager.get_stats()
        return {
            "collections": collections,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



class PremiumAdviceResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    count: int
    advice: str  # texto generado por IA

@router.post("/premium/advice", response_model=PremiumAdviceResponse)
async def premium_advice(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_premium:
        raise HTTPException(status_code=403, detail="Se requiere suscripción premium")
    
    # Crear instancia local para asegurar conexión actual
    local_chroma = ChromaManager()
    results = local_chroma.premium_search_with_scoring(request.query, k=request.num_results or 10)
    
    # Generar respuesta humana usando IA
    advice = generate_premium_advice(request.query, results)
    
    return PremiumAdviceResponse(
        results=results,
        query=request.query,
        count=len(results),
        advice=advice
    )
    
