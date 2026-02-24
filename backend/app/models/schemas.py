from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None
    cities: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[Dict[str, Any]]] = None

class DocumentUploadResponse(BaseModel):
    message: str
    filename: str
    success: bool
    chunks_processed: Optional[int] = None

class HealthResponse(BaseModel):
    status: str
    langflow_connected: bool
    chroma_configured: bool
    stats: Optional[Dict[str, Any]] = None

class QueryRequest(BaseModel):
    query: str
    num_results: int = 10

class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    count: int

class PremiumQueryRequest(BaseModel):
    query: str
    num_results: int = 15
    include_visa: bool = True
    include_tax: bool = True

class PremiumQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    count: int

class CityMatch(BaseModel):
    city: str
    country: str
    match_score: float
    budget: str
    internet: str
    climate: str
    visa: str
    image_url: Optional[str] = None
    vibe_tags: List[str] = []

class MatchResponse(BaseModel):
    matches: List[CityMatch]
    total_found: int
