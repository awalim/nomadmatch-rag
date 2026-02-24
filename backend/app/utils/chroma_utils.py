import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from .scoring import overall_score

class ChromaManager:
    def __init__(self, persist_directory="./chroma_data", collection_name="nomadmatch_cities"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.initialized = False
        self.init_chroma()

    def init_chroma(self):
        """Initialize ChromaDB"""
        try:
            os.makedirs(self.persist_directory, exist_ok=True)

            self.client = chromadb.PersistentClient(path=self.persist_directory)

            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=api_key,
                    model_name="text-embedding-3-small"
                )
                print("✅ OpenAI embeddings configurados")
            else:
                self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
                print("⚠️ Usando embeddings por defecto (sin OpenAI)")

            try:
                self.collection = self.client.get_collection(
    		name=self.collection_name,
    		embedding_function=self.embedding_function
		)
                print(f"✅ Colección existente cargada: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                print(f"✅ Nueva colección creada: {self.collection_name}")

            self.initialized = True
            print(f"🎻 ChromaDB listo: {self.collection_name}")

        except Exception as e:
            print(f"❌ Error initializing ChromaDB: {e}")
            self.initialized = False

    def ingest_dataframe(self, df: pd.DataFrame, source_file: str) -> int:
        """Ingest DataFrame into ChromaDB"""
        if not self.initialized or not self.collection:
            print("❌ ChromaDB no inicializado")
            return 0

        documents = []
        metadatas = []
        ids = []

        # Detect file type based on filename
        is_visa_premium = "visa_premium" in source_file.lower()
        is_tax_premium = "tax_premium" in source_file.lower()
        is_premium = is_visa_premium or is_tax_premium or "tier_premium" in source_file.lower()

        print(f"📄 Procesando {len(df)} filas de '{source_file}'...")
        if is_premium:
            print(f"  → Detectado como archivo PREMIUM ({'visa' if is_visa_premium else 'tax' if is_tax_premium else 'general'})")

        for idx, row in df.iterrows():
            # Build rich text for embedding search
            text_parts = []
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    text_parts.append(f"{col}: {row[col]}")
            text = " | ".join(text_parts)

            # Determine data_type and tier
            if is_visa_premium:
                data_type = "Visa"
                tier = "premium"
            elif is_tax_premium:
                data_type = "Tax"
                tier = "premium"
            elif is_premium:
                data_type = str(row.get("data_type", "Visa"))
                tier = "premium"
            else:
                data_type = str(row.get("data_type", "General"))
                tier = str(row.get("tier", "free"))

            # Get city name (try multiple column names)
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
                "tier": tier
            }

            # For FREE tier: add common fields
            common_field_map = {
                "Monthly_Budget_Single": "budget",
                "Internet_Reliability_Score": "internet",
                "Digital_Nomad_Visa": "visa",
                "Summer_Temperature": "climate",
                "Vibe_Tags": "vibe"
            }
            for csv_col, meta_key in common_field_map.items():
                if csv_col in df.columns and pd.notna(row.get(csv_col)):
                    metadata[meta_key] = str(row[csv_col])

            # For PREMIUM tier: store ALL columns as metadata
            # ChromaDB metadata only supports str, int, float, bool
            if is_premium:
                for col in df.columns:
                    if col.lower() in ["city", "country", "region", "tier"]:
                        continue  # Already added above
                    val = row.get(col)
                    if pd.notna(val):
                        val_str = str(val).strip()
                        if val_str:
                            # Store with original column name (preserving case)
                            metadata[col] = val_str

            documents.append(text)
            metadatas.append(metadata)
            ids.append(f"{source_file}_{idx}")

        # Add in batches
        batch_size = 100
        total_added = 0

        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            try:
                self.collection.upsert(
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
                total_added += (end_idx - i)
                print(f"✅ Batch {i//batch_size + 1}: {end_idx - i} documentos")
                if i == 0 and metadatas:
                    print(f"  → Campos metadata: {list(metadatas[0].keys())}")
            except Exception as e:
                print(f"❌ Error en batch {i//batch_size + 1}: {e}")

        print(f"🎉 Total ingestado: {total_added} documentos")
        return total_added

    def similarity_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Perform similarity search (FREE tier - solo General)"""
        if not self.initialized or not self.collection:
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                where={"tier": "free"}
            )

            formatted_results = []
            if results and 'documents' in results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0
                    score = 1.0 - (distance / 2)

                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": round(score, 3)
                    })

            return formatted_results

        except Exception as e:
            print(f"❌ Error en similarity_search: {e}")
            return []

    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
            return []

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            if self.collection:
                count = self.collection.count()
                return {
                    "total_documents": count,
                    "collection": self.collection_name,
                    "initialized": self.initialized,
                    "persist_directory": self.persist_directory
                }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")

        return {
            "total_documents": 0,
            "collection": self.collection_name,
            "initialized": self.initialized,
            "persist_directory": self.persist_directory
        }

    def delete_collection(self):
        """Delete current collection"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"🗑️ Colección eliminada: {self.collection_name}")
            self.collection = None
            self.initialized = False
        except Exception as e:
            print(f"❌ Error deleting collection: {e}")

    def premium_search_with_scoring(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Devuelve los documentos premium (Visa/Tax) ordenados por overall_score"""
        if not self.initialized or not self.collection:
            return []
        try:
            results = self.collection.get(where={"data_type": {"$in": ["Visa", "Tax"]}})
            documents = []
            if results and 'ids' in results:
                for i in range(len(results['ids'])):
                    meta = results['metadatas'][i]
                    documents.append({
                        "content": results['documents'][i],
                        "metadata": meta,
                        "similarity_score": 1.0,
                        "overall_score": meta.get('overall_score', meta.get('Overall_Score', 0))
                    })
            documents.sort(key=lambda x: x.get('overall_score', 0) or 0, reverse=True)
            return documents[:k]
        except Exception as e:
            print(f"❌ Error en premium_search_with_scoring: {e}")
            return []

    def _calculate_overall_score(self, metadata: Dict) -> Optional[float]:
        """Calcula el Overall_Score según las reglas del archivo de scoring"""
        try:
            tax_rate = metadata.get("Tax_Rate_Standard_Pct")
            visa_available = metadata.get("Digital_Nomad_Visa")
            return None
        except Exception as e:
            print(f"Error calculating overall score: {e}")
            return None
