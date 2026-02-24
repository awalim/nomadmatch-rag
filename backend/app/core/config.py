import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NomadMatch RAG API"

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "/app/chroma_data")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "nomadmatch_cities")

    # CORS — incluye frontend en Docker (8080) y desarrollo local (3000)
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "*",
    ]


settings = Settings()
