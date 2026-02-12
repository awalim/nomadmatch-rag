import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional

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
            # Asegurar que el directorio existe
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Crear cliente persistente - NUEVA API
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Configurar embeddings
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
            
            # Obtener o crear colección
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name
                )
                print(f"✅ Colección existente cargada: {self.collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                print(f"✅ Nueva colección creada: {self.collection_name}")
            
            self.initialized = True
            print(f"🎯 ChromaDB listo: {self.collection_name}")
            
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
        
        print(f"📥 Procesando {len(df)} filas...")
        
        for idx, row in df.iterrows():
            # Crear texto rico para búsqueda
            text_parts = []
            for col in df.columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    text_parts.append(f"{col}: {row[col]}")
            
            text = " | ".join(text_parts)
            
            # Metadata para filtrado
            metadata = {
                "source": source_file,
                "row_index": str(idx),
                "city": str(row.get("city", "")),
                "country": str(row.get("country", "")),
                "region": str(row.get("region", "")),
                "data_type": str(row.get("data_type", "General")),
                "tier": str(row.get("tier", "free"))
            }
            
            # Añadir campos importantes para filtrado
            if "Monthly_Budget_Single" in row:
                metadata["budget"] = str(row["Monthly_Budget_Single"])
            if "Internet_Reliability_Score" in row:
                metadata["internet"] = str(row["Internet_Reliability_Score"])
            if "Digital_Nomad_Visa" in row:
                metadata["visa"] = str(row["Digital_Nomad_Visa"])
            if "Summer_Temperature" in row:
                metadata["climate"] = str(row["Summer_Temperature"])
            if "Vibe_Tags" in row:
                metadata["vibe"] = str(row["Vibe_Tags"])
            
            documents.append(text)
            metadatas.append(metadata)
            ids.append(f"{source_file}_{idx}")
        
        # Añadir en batches
        batch_size = 100
        total_added = 0
        
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            try:
                self.collection.add(
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
                total_added += (end_idx - i)
                print(f"✅ Batch {i//batch_size + 1}: {end_idx - i} documentos")
            except Exception as e:
                print(f"❌ Error en batch {i//batch_size + 1}: {e}")
        
        print(f"🎉 Total ingestado: {total_added} documentos")
        return total_added
    
    def similarity_search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """Perform similarity search (FREE tier - solo General)"""
        if not self.initialized or not self.collection:
            print("❌ ChromaDB no inicializado")
            return []
        
        try:
            print(f"🔍 Buscando: '{query}'")
            
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
                
                print(f"✅ Encontrados {len(formatted_results)} resultados")
            
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
