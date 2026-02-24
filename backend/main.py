"""
NomadMatch Backend — FastAPI Application
RAG-powered city recommendation system for digital nomads.
"""
import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from chroma_manager import ChromaManager
from routes import router, set_chroma_manager

app = FastAPI(
    title="NomadMatch API",
    description="RAG-powered city recommendation for digital nomads",
    version="1.0.0"
)

# Middleware CORS primero
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el origen real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global OPTIONS (opcional, pero ayuda si hay problemas)
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

# Initialize ChromaManager
cm = ChromaManager()
set_chroma_manager(cm)

# Auto-ingest if collection is empty and CSV exists
CSV_PATH = os.getenv("CITIES_CSV_PATH", "/app/data/cities.csv")
if cm.get_stats()["total_docs"] == 0 and os.path.exists(CSV_PATH):
    print(f"📂 Auto-ingesting {CSV_PATH}...")
    cm.ingest_csv(CSV_PATH)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "app": "NomadMatch API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET  /api/v1/health",
            "GET  /api/v1/collections",
            "POST /api/v1/upload",
            "POST /api/v1/query",
            "POST /api/v1/chat"
        ]
    }
