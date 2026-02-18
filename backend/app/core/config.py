import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NomadMatch RAG API"
    
    # Langflow Settings
    LANGFLOW_URL: str = os.getenv("LANGFLOW_URL", "http://langflow:7860")
    LANGFLOW_FLOW_ID: str = os.getenv("LANGFLOW_FLOW_ID", "768c1c22-1496-4ccb-8e6f-40a09f44ae3c")
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # ChromaDB Settings
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "nomadmatch_cities")
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

settings = Settings()
