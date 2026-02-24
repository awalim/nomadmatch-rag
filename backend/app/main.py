"""
NomadMatch Backend — FastAPI Application (Prototipo 4)
RAG-powered city recommendation system for digital nomads.
Punto de entrada único: arranca FastAPI, inicializa ChromaDB y auto-ingesta CSVs.
"""
import os
import glob
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.utils.chroma_utils import ChromaManager
from app.api.routes import router as routes_router, set_chroma_manager
from app.api.auth import router as auth_router

app = FastAPI(
    title="NomadMatch RAG API",
    description="RAG-powered city recommendation for digital nomads",
    version="4.0.0"
)

# ── CORS ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ChromaDB init ─────────────────────────────────
persist_dir = os.getenv("CHROMA_PERSIST_DIR", "/app/chroma_data")
cm = ChromaManager(persist_directory=persist_dir)
set_chroma_manager(cm)

# ── Auto-ingest CSVs on startup ──────────────────
def auto_ingest():
    """
    Busca CSVs en /app/data (backend interno) y /app/external_data (montado desde ./data)
    y los ingesta si ChromaDB está vacío.
    """
    stats = cm.get_stats()
    current_docs = stats.get("total_documents", 0)

    if current_docs > 0:
        print(f"✅ ChromaDB ya tiene {current_docs} documentos — saltando ingesta")
        return

    print("📂 ChromaDB vacío — buscando CSVs para auto-ingestar...")

    # Directorios donde buscar CSVs
    search_dirs = [
        "/app/external_data",  # montado desde ./data (raíz del proyecto)
        "/app/data",           # copiado desde backend/data en el Dockerfile
    ]

    csv_files = []
    for d in search_dirs:
        if os.path.isdir(d):
            found = glob.glob(os.path.join(d, "*.csv"))
            csv_files.extend(found)
            print(f"  📁 {d}: {len(found)} CSV(s) encontrados")

    if not csv_files:
        print("⚠️ No se encontraron CSVs para ingestar")
        return

    import pandas as pd
    total = 0
    for csv_path in csv_files:
        try:
            filename = os.path.basename(csv_path)
            df = pd.read_csv(csv_path)
            print(f"  📊 Ingestando {filename}: {len(df)} filas, {len(df.columns)} columnas")
            count = cm.ingest_dataframe(df, source_file=filename)
            total += count
        except Exception as e:
            print(f"  ❌ Error ingestando {csv_path}: {e}")

    print(f"🎉 Auto-ingesta completada: {total} documentos totales en ChromaDB")

auto_ingest()

# ── Routers ───────────────────────────────────────
app.include_router(routes_router)
app.include_router(auth_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "app": "NomadMatch RAG API",
        "version": "4.0.0",
        "docs": "/docs",
        "endpoints": [
            "GET  /api/v1/health",
            "GET  /api/v1/collections",
            "POST /api/v1/upload",
            "POST /api/v1/query",
            "POST /api/v1/chat",
            "POST /api/v1/auth/register",
            "POST /api/v1/auth/login",
            "GET  /api/v1/auth/me",
        ]
    }
