"""
ChromaManager — Motor RAG de NomadMatch (Prototipo 4)
Gestiona ChromaDB: ingesta de datos, búsqueda semántica y scoring.
"""
import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional


class ChromaManager:
    def __init__(self, persist_directory="/app/chroma_data", collection_name="nomadmatch_cities"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.initialized = False
        self._init_chroma()

    def _init_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            print(f"✅ ChromaDB PersistentClient: {self.persist_directory}")

            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key:
                self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=api_key,
                    model_name="text-embedding-3-small"
                )
                print("✅ Using OpenAI text-embedding-3-small (1536 dims)")
            else:
                self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
                print("⚠️ No OPENAI_API_KEY — using default embeddings")

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            self.initialized = True
            print(f"🎻 ChromaDB listo: {self.collection_name} ({self.collection.count()} docs)")

        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {e}")
            self.initialized = False

    # ── Stats ─────────────────────────────────────
    def get_stats(self) -> Dict:
        if self.collection:
            count = self.collection.count()
            return {
                "total_documents": count,
                "total_docs": count,  # alias para compatibilidad
                "collection": self.collection_name,
                "initialized": self.initialized,
                "persist_directory": self.persist_directory,
                "embedding_model": "text-embedding-3-small",
            }
        return {
            "total_documents": 0,
            "total_docs": 0,
            "collection": self.collection_name,
            "initialized": self.initialized,
            "persist_directory": self.persist_directory,
        }

    # ── Ingesta desde DataFrame ───────────────────
    def ingest_dataframe(self, df: pd.DataFrame, source_file: str) -> int:
        """Ingest a pandas DataFrame into ChromaDB."""
        if not self.initialized or not self.collection:
            print("❌ ChromaDB no inicializado")
            return 0

        # Detectar tipo de archivo
        is_visa_premium = "visa_premium" in source_file.lower()
        is_tax_premium = "tax_premium" in source_file.lower()
        is_premium = is_visa_premium or is_tax_premium

        print(f"📄 Procesando {len(df)} filas de '{source_file}' ({'PREMIUM' if is_premium else 'FREE'})...")

        documents = []
        metadatas = []
        ids = []

        for idx, row in df.iterrows():
            # Build rich text for embedding
            text_parts = []
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    text_parts.append(f"{col}: {row[col]}")
            text = " | ".join(text_parts)

            # Determine tier and data_type
            if is_visa_premium:
                data_type, tier = "Visa", "premium"
            elif is_tax_premium:
                data_type, tier = "Tax", "premium"
            else:
                data_type = str(row.get("data_type", "General"))
                tier = str(row.get("tier", "free"))

            # City name (try multiple column names)
            city = str(row.get("city", row.get("City", "")))
            country = str(row.get("Country", row.get("country", "")))
            region = str(row.get("Region", row.get("region", "")))

            # Base metadata
            metadata = {
                "source": source_file,
                "row_index": str(idx),
                "city": city,
                "country": country,
                "region": region,
                "data_type": data_type,
                "tier": tier,
            }

            # Campos comunes para free
            common_fields = {
                "Monthly_Budget_Single": "budget",
                "Internet_Reliability_Score": "internet",
                "Digital_Nomad_Visa": "visa",
                "Summer_Temperature": "summer_temp",
                "Winter_Temperature": "winter_temp",
                "Vibe_Tags": "vibe_tags",
                "Safety_Score": "safety",
                "Nightlife_Score": "nightlife",
                "Family_Friendly_Score": "family",
                "Startup_Scene_Score": "startup",
                "Coworking_Availability": "coworking",
                "Expat_Community_Size": "expat_size",
                "English_Proficiency_Score": "english",
                "Outdoor_Activities_Score": "outdoor",
                "Sunshine_Level": "sunshine",
                "Visa_Score": "visa_score",
                "Visa_Type": "visa_type",
                "Visa_Duration": "visa_duration",
                "Schengen": "schengen",
            }
            for csv_col, meta_key in common_fields.items():
                if csv_col in df.columns and pd.notna(row.get(csv_col)):
                    metadata[meta_key] = str(row[csv_col])

            # Campos numéricos
            int_fields = {
                "Monthly_Budget_Single_EUR": "budget_eur",
                "Coworking_Monthly_EUR": "coworking_eur",
                "Airbnb_Avg_Monthly_EUR": "airbnb_eur",
                "Population": "population",
                "Visa_Income_Req_EUR": "visa_income_req",
            }
            for csv_col, meta_key in int_fields.items():
                if csv_col in df.columns and pd.notna(row.get(csv_col)):
                    try:
                        metadata[meta_key] = int(float(row[csv_col]))
                    except (ValueError, TypeError):
                        metadata[meta_key] = str(row[csv_col])

            # Premium: almacenar TODAS las columnas extra
            if is_premium:
                for col in df.columns:
                    if col.lower() in ["city", "country", "region", "tier"]:
                        continue
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip():
                        metadata[col] = str(val)

            documents.append(text)
            metadatas.append(metadata)
            ids.append(f"{source_file}_{idx}")

        # Upsert en batches
        batch_size = 50
        total_added = 0
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            try:
                self.collection.upsert(
                    documents=documents[i:end],
                    metadatas=metadatas[i:end],
                    ids=ids[i:end],
                )
                total_added += (end - i)
            except Exception as e:
                print(f"  ❌ Error en batch {i // batch_size + 1}: {e}")

        print(f"  ✅ Ingestados {total_added} documentos de {source_file}")
        return total_added

    # ── Ingesta desde CSV path (compatibilidad) ──
    def ingest_csv(self, csv_path: str) -> int:
        """Read CSV and ingest into ChromaDB."""
        df = pd.read_csv(csv_path)
        filename = os.path.basename(csv_path)
        return self.ingest_dataframe(df, source_file=filename)

    # ── Búsqueda semántica ────────────────────────
    def search(self, query: str, n_results: int = 15, tier: str = None) -> list:
        """Semantic search against ChromaDB."""
        if not self.initialized or not self.collection:
            return []

        try:
            count = self.collection.count()
            if count == 0:
                return []

            kwargs = {
                "query_texts": [query],
                "n_results": min(n_results, count),
                "include": ["documents", "metadatas", "distances"],
            }

            # Filtrar por tier si se especifica
            if tier:
                kwargs["where"] = {"tier": tier}

            results = self.collection.query(**kwargs)

            output = []
            if results and results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    distance = results["distances"][0][i] if results["distances"] else 1.0
                    output.append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i] if results["documents"] else "",
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": distance,
                        "base_score": round(1 - distance, 4),
                    })
            return output

        except Exception as e:
            print(f"❌ Error en search: {e}")
            return []

    # ── Búsqueda free (alias) ─────────────────────
    def similarity_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Search only free tier documents."""
        results = self.search(query, n_results=k, tier="free")
        return [
            {
                "content": r["document"],
                "metadata": r["metadata"],
                "similarity_score": round(r["base_score"], 3),
            }
            for r in results
        ]

    # ── Búsqueda premium ──────────────────────────
    def premium_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Search premium tier documents (visa/tax)."""
        return self.search(query, n_results=k, tier="premium")

    # ── Utilidades ────────────────────────────────
    def list_collections(self) -> List[str]:
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
            return []

    def delete_collection(self):
        try:
            self.client.delete_collection(self.collection_name)
            print(f"🗑️ Colección eliminada: {self.collection_name}")
            self.collection = None
            self.initialized = False
        except Exception as e:
            print(f"❌ Error deleting collection: {e}")
