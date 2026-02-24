"""
ChromaManager — Motor RAG de NomadMatch
Gestiona la conexión a ChromaDB, ingesta de datos y búsqueda semántica.
"""
import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

COLLECTION_NAME = "nomadmatch_cities"


class ChromaManager:
    def __init__(self):
    # Usar siempre cliente persistente (más simple para Docker)
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
    # Si es una ruta relativa, conviértela a absoluta dentro del proyecto
    if not os.path.isabs(persist_dir):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        persist_dir = os.path.join(base_dir, persist_dir)
    os.makedirs(persist_dir, exist_ok=True)
    self.client = chromadb.PersistentClient(path=persist_dir)
    print(f"✅ ChromaDB PersistentClient usando directorio: {persist_dir}")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key:
        self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_key,
            model_name="text-embedding-3-small"
        )
        print("✅ Using OpenAI text-embedding-3-small (1536 dims)")
    else:
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        print("⚠️ No OPENAI_API_KEY — using default embeddings")

    self.collection = self.client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=self.embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )

    def get_stats(self) -> dict:
        count = self.collection.count()
        return {
            "collection": COLLECTION_NAME,
            "total_docs": count,
            "embedding_model": "text-embedding-3-small",
            "dimensions": 1536
        }

    def build_document(self, row: dict) -> str:
        """Build enriched text document for embedding from a city row."""
        parts = [
            f"city: {row.get('city', '')}",
            f"country: {row.get('Country', '')}",
            f"region: {row.get('Region', '')}",
            f"monthly budget: {row.get('Monthly_Budget_Single', '')} ({row.get('Monthly_Budget_Single_EUR', '')} EUR)",
            f"internet: {row.get('Internet_Reliability_Score', '')} speed {row.get('Internet_Avg_Mbps', '')} Mbps",
            f"coworking: {row.get('Coworking_Availability', '')}",
            f"transport: {row.get('Public_Transport_Score', '')} public transport, {row.get('Bike_Friendly_Score', '')} cycling",
            f"climate: winter {row.get('Winter_Temperature', '')}, summer {row.get('Summer_Temperature', '')}",
            f"sunshine: {row.get('Sunshine_Level', '')}, rainfall: {row.get('Rainfall_Level', '')}",
            f"safety: {row.get('Safety_Score', '')}",
            f"healthcare: {row.get('Healthcare_Quality_Score', '')}",
            f"expat community: {row.get('Expat_Community_Size', '')}, nomad scene: {row.get('Nomad_Community_Score', '')}",
            f"english proficiency: {row.get('English_Proficiency_Score', '')}",
            f"nightlife: {row.get('Nightlife_Score', '')}, dating: {row.get('Dating_Scene_Score', '')}",
            f"family friendly: {row.get('Family_Friendly_Score', '')}",
            f"startup scene: {row.get('Startup_Scene_Score', '')}, tech jobs: {row.get('Tech_Jobs_Score', '')}",
            f"coffee culture: {row.get('Coffee_Culture_Score', '')}, restaurants: {row.get('Restaurant_Diversity_Score', '')}",
            f"outdoor activities: {row.get('Outdoor_Activities_Score', '')}",
            f"cultural events: {row.get('Cultural_Events_Score', '')}",
            f"vibes: {row.get('Vibe_Tags', '')}",
            f"digital nomad visa: {row.get('Digital_Nomad_Visa', 'N/A')}",
            f"visa score: {row.get('Visa_Score', 'N/A')}",
            f"schengen: {row.get('Schengen', 'N/A')}",
        ]
        return " | ".join(parts)

    def build_metadata(self, row: dict) -> dict:
        """Build structured metadata for filtering and boost scoring."""
        return {
            "city": str(row.get("city", "")),
            "country": str(row.get("Country", "")),
            "region": str(row.get("Region", "")),
            "tier": str(row.get("tier", "free")),
            "budget": str(row.get("Monthly_Budget_Single", "")),
            "budget_eur": int(row.get("Monthly_Budget_Single_EUR", 0)),
            "internet": str(row.get("Internet_Reliability_Score", "")),
            "visa": str(row.get("Digital_Nomad_Visa", "No")),
            "visa_score": str(row.get("Visa_Score", "")),
            "summer_temp": str(row.get("Summer_Temperature", "")),
            "winter_temp": str(row.get("Winter_Temperature", "")),
            "safety": str(row.get("Safety_Score", "")),
            "nightlife": str(row.get("Nightlife_Score", "")),
            "family": str(row.get("Family_Friendly_Score", "")),
            "startup": str(row.get("Startup_Scene_Score", "")),
            "coworking": str(row.get("Coworking_Availability", "")),
            "vibe_tags": str(row.get("Vibe_Tags", "")),
            "expat_size": str(row.get("Expat_Community_Size", "")),
            "english": str(row.get("English_Proficiency_Score", "")),
            "outdoor": str(row.get("Outdoor_Activities_Score", "")),
            "sunshine": str(row.get("Sunshine_Level", "")),
            "airport": str(row.get("Airport", "")),
            "coworking_eur": int(row.get("Coworking_Monthly_EUR", 0)),
            "airbnb_eur": int(row.get("Airbnb_Avg_Monthly_EUR", 0)),
            "population": int(row.get("Population", 0)),
            "lgbtq": str(row.get("LGBTQ_Friendliness_Score", "")),
            "pet_friendly": str(row.get("Pet_Friendly_Score", "")),
            "schengen": str(row.get("Schengen", "")),
            "visa_type": str(row.get("Visa_Type", "")),
            "visa_duration": str(row.get("Visa_Duration", "")),
            "visa_income_req": int(row.get("Visa_Income_Req_EUR", 0)),
        }

    def ingest_csv(self, csv_path: str) -> int:
        """Read CSV file and ingest all cities into ChromaDB."""
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded CSV: {len(df)} cities, {len(df.columns)} columns")

        ids = []
        documents = []
        metadatas = []

        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            doc_id = f"nomadmatch_city_{idx}"
            document = self.build_document(row_dict)
            metadata = self.build_metadata(row_dict)

            ids.append(doc_id)
            documents.append(document)
            metadatas.append(metadata)

        # Upsert in batches of 50
        batch_size = 50
        for i in range(0, len(ids), batch_size):
            self.collection.upsert(
                ids=ids[i:i+batch_size],
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )

        count = self.collection.count()
        print(f"✅ Ingested {count} cities into ChromaDB")
        return count

    def search(self, query: str, n_results: int = 15) -> list:
        """Semantic search against ChromaDB. Returns list of results with distances."""
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, self.collection.count() or 50),
            include=["documents", "metadatas", "distances"]
        )

        output = []
        if results and results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                output.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 1.0,
                    "base_score": round(1 - results["distances"][0][i], 4) if results["distances"] else 0.0
                })

        return output
